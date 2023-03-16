import discord, asyncio, random, string, re

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Read word files
with open('words.txt', 'r') as f:
    words = f.read().splitlines()
with open('normal_prompts.txt', 'r') as f:
    normal_prompts = f.read().splitlines()
with open('easy_regex_prompts.txt', 'r') as f:
    easy_regex_prompts = f.read().splitlines()
with open('hard_regex_prompts.txt', 'r') as f:
    hard_regex_prompts = f.read().splitlines()

# Generate prompt
def generate_prompt(mode):
    match mode:
        case 'normal':
            prompt = random.choice(normal_prompts)
        case 'easy':
            prompt = random.choice(easy_regex_prompts)
        case 'hard':
            prompt = random.choice(hard_regex_prompts)
    return prompt

# Variables
players = []
lives = {}
current_prompt = None
round_time = 30
game_running = False
game_starting = False
mode = 'normal'

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')

@client.event
async def on_message(message):
    global players, current_prompt, round_time, lives, game_running, game_starting, mode

    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    if message.content == ('!join'):
        if game_running:
            await message.channel.send(f"❌ Sorry {message.author.mention}, you can't join an in-progress game. ❌")
            return
        if message.author not in players:
            players.append(message.author)
            lives[message.author] = 5
            await message.channel.send(f'✅ {message.author.mention} has joined the game. ✅')
        else:
            await message.channel.send(f'❌ {message.author.mention}, you are already in the game. ❌')

    elif message.content == ('!start'):
        if game_running:
            await message.channel.send('❌ A game is already in progress. ❌')
            return
        
        if game_starting:
            await message.channel.send('❌ A game is already starting. ❌')
            return
        
        if len(players) < 2:
            await message.channel.send('❌ Not enough players to start the game. ❌')
            return
        
        game_starting = True
        await message.channel.send('🏁 Starting game in 10 seconds. 🏁')
        await asyncio.sleep(10)
        game_running = True
        game_starting = False
        
        while len(players) > 1 and game_running:

            await message.channel.send(f'⏲️ NEW ROUND: **{round(round_time, 1)} seconds** per player. ⏲️')

            for player in players:
                current_prompt = generate_prompt(mode)
                await message.channel.send(f"🛎️ {player.mention}, it's your turn. Prompt: `{current_prompt}` 🛎️")

                def check(m):
                    if mode == 'normal':
                        return m.author == player and current_prompt in m.content and m.content in words
                    else:
                        return m.author == player and re.match('^' + current_prompt + '$', m.content) and m.content in words

                while game_running:
                    try:
                        msg = await client.wait_for('message', check=check, timeout=round_time)
                        await msg.add_reaction('✅')
                        break

                    except asyncio.TimeoutError:
                        lives[player] -= 2
                        if lives[player] < 0:
                            lives[player] = 0

                        await message.channel.send(f"⏰ Time's up, {player.mention}. **-2 lives** ({lives[player]} lives remaining) ⏰")

                        if lives[player] == 0:
                            await message.channel.send(f'❌ {player.mention} has been eliminated. ❌')
                            players.remove(player)
                            del lives[player]

                        await message.channel.send(f'❗ **SHOWDOWN!** Steal {player.mention}\'s prompt in the next 10 seconds for an extra life. ❗')

                        def stealCheck(m):
                            if mode == 'normal':
                                return current_prompt in m.content and m.content in words
                            else:
                                return re.match('^' + current_prompt + '$', m.content) and m.content in words
                        
                        try:
                            msg = await client.wait_for('message', check=stealCheck, timeout=10)

                            lives[msg.author] += 1

                            await message.channel.send(f'🎉 Congrats, {msg.author.mention}. **+1 life** ({lives[msg.author]} total lives) 🎉')

                        except asyncio.TimeoutError:
                            await message.channel.send(f'💥 Nobody solved {player.mention}\'s prompt. 💥')
                            
                            for p in players:
                                if lives[p] == 0:
                                    await message.channel.send(f'❌ {p.mention} has been eliminated. ❌')
                                    players.remove(p)
                                    del lives[p]

                        break
                
                if len(players) == 1:
                    break

            if round_time > 10:
                round_time -= 2.5
            
            current_prompt = None
        
        # end the game and announce the winner
        await message.channel.send(f'🏆 {players[0].mention} has won the game with {lives[players[0]]} lives remaining! 🏆')
        players = []
        lives = {}
        current_prompt = None
        round_time = 30
        game_running = False

    # ==============
    # OTHER COMMANDS
    # ==============

    elif message.content == '!stop' and message.author in players and game_running:
        players = []
        lives = {}
        current_prompt = None
        round_time = 30
        game_running = False
        await message.channel.send('Game stopped.')

    # Print the list of players
    elif message.content == '!players':
        await message.channel.send(f'👥 Players: {", ".join([p.mention for p in players])} 👥')

    elif message.content == '!help regex':
        regexExplanation = discord.Embed(title="What is regex?",
                      description="**Regular Expressions** are a way to match patterns in strings. They are used in many programming and computer processes, due to their efficiency and flexibility. These may look incredibly complicated, but they’re not — anyone can get the hang of them in under 10 minutes, just pay close attention to the examples below.",
                      colour=0xffffff)
        regexBasic = discord.Embed(title="Basic Rules — These are all you need for the `regex-easy` mode.",
                      description="> Rule 1: A period . matches any letter. \w does the same.\n\ne.g. some answers to `p.\w` are:\n✅ pod | ✅ pet | ❌ package | ❌ egg\n\ne.g. some answers to `.a.` are:\n✅ bar | ✅ cat | ❌ fraud | ❌ each\n\n> Rule 2: Square brackets [ ] match one of the letters inside.\n\ne.g. some answers to `b[aeu]d` are:\n✅ bad | ✅ bed | ❌ bid | ❌ abode\n\ne.g. some answers to `[aeiou]....` are:\n✅ apple | ✅ icons | ❌ eggs | ❌ underneath\n\n> Rule 3: A plus + matches one or more of the previous character.\n\ne.g. some answers to `o.+n` are:\n✅ overthrown | ✅ omen | ❌ on | ❌ oregano\n\ne.g. some answers to `.+es+` are:\n✅ prowess | ✅ times | ❌ me | ❌ basin\n\n> Rule 4: An asterisk * matches zero or more of the previous character.\n\ne.g. some answers to `o.*n` are:\n✅ on | ✅ overthrown | ❌ omens | ❌ oregano\n\ne.g. some answers to `.*e.*` are:\n✅ eggplant | ✅ ledge | ❌ sasquatch | ❌ banana",
                      colour=0xffffff)
        regexAdditional = discord.Embed(title="Additional Rules — These are all you need for the `regex-hard` mode.",
                      description="> Rule 5: [a-x] matches any character between a and x\n\ne.g. some answers to `n[e-p]t` are:\n✅ net | ✅ not | ❌ nut | ❌ nat\n\ne.g. some answers to `b[a-o][a-z][b-x]` are:\n✅ barn | ✅ bore | ❌ bush | ❌ bet\n\n> Rule 6: A square bracket with a caret at the start [^ ] matches any character not inside.\n\ne.g. some answers to `.[^ai].` are:\n✅ bed | ✅ cut | ❌ cat | ❌ rip\n\ne.g. some answers to `.[^aeiou]` are:\n✅ at | ✅ by | ❌ no | ❌ sauce\n\n> Rule 7: Parentheses are capturing groups ( ) and vertical bars | mean OR. \n\ne.g. some answers to `(eg|pa|ba).` are:\n✅ egg | ✅ pat | ❌ leg | ❌ nap\n\ne.g. some answers to `(bo|ro)(ok|ne)` are:\n✅bone | ✅rook | ❌shook | ❌borrow\n\n> Rule 8: A question mark ? matches zero or one of the previous character.\n\ne.g. some answers to `p?o?d` are:\n✅ pod | ✅ proud | ❌ prone | ❌ podge\n\ne.g. some answers to `a.?` are:\n✅ a | ✅ at | ❌ axe | ❌ amplifier\n\n> Rule 9: Curly brackets {m, n} match the previous character between m and n times.\n\ne.g. some answers to `fre{1,2}.+` are:\n✅ fresh | ✅ freeze | ❌ freeeeeze | ❌ freeeeeeeeeeeeeze\n\ne.g. some answers to `.{3,5}` are:\n✅ egg | ✅ eggs | ❌ eggplant | ❌ eggplants",
                      colour=0xffffff)
        await message.channel.send(embed=regexExplanation)
        await message.channel.send(embed=regexBasic)
        await message.channel.send(embed=regexAdditional)

    elif message.content == '!help' or message.content == '!mode' or message.content == '!modes':
        helpCommands = discord.Embed(title="Commands:",
                      description="`!help` — Opens the commands menu.\n\n`!help regex` — A simple explanation of how to regex.`!mode normal` — Basic word game where you complete a word from a 3 or 4 character segment.\n\n`!mode regex-easy` — Word game where you try to match a word to the given regular expression. Contains only [ ] . * + \n\n`!mode regex-hard` — Word game where you try to match a word to the given regular expression. Contains all regex syntax.\n\n`!start` — If no game is currently running, starts a game after 10 seconds.\n\n`!join` — Join a game that is in the process of starting.\n\n`!players` — List all players currently in the game.\n\n`!stop` — End the currently active game.",
                      colour=0xffffff)
        await message.channel.send(embed=helpCommands)

    # Modes
    elif message.content == '!mode normal':
        await message.channel.send('✅ Game changed to normal mode. ✅')
        mode = 'normal'
    elif message.content == '!mode regex-easy':
        await message.channel.send('✅ Game changed to regex mode, easy difficulty. ✅')
        mode = 'regex-easy'
    elif message.content == '!mode regex-hard':
        await message.channel.send('✅ Game changed to regex mode, hard difficulty. ✅')
        mode = 'regex-hard'

client.run(' :) ')
