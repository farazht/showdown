import discord, asyncio, random, string, re

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Read word files
with open('words10k.txt', 'r') as f:
    words10k = f.read().splitlines()
with open('words84k.txt', 'r') as f:
    words84k = f.read().splitlines()

# Variables
players = []
lives = {}
current_prompt = None
round_time = 30
game_running = False
mode = 'normal-easy'

# ================
# PROMPT GENERATOR
# ================

def generatePrompt(difficulty):
    word1 = random.choice(words10k)
    word2 = random.choice(words10k)

    while len(word1) < 3:
        word1 = random.choice(words10k)
    while len(word2) < 3:
        word2 = random.choice(words10k)

    regex = ""

    # Generate 2 random letters
    letters = ''.join(random.sample(string.ascii_lowercase, 2))
    letter1 = letters[0]
    letter2 = letters[1]

    # Generate 2 random 2-character substrings
    index = random.randint(0, len(word1) - 2)
    segment1 = word1[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment2 = word2[index:index+2]

    # Generate 2 strings of 4-7 unique random letters in [ ]
    sb1 = "[" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"
    sb2 = "[" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"

    # Generate 2 strings of 4-7 unique random letters in [^ ]
    nsb1 = "[^" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"
    nsb2 = "[^" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"

    # Generate 2 number ranges
    numRange1 = "{" + str(random.randint(0, 3)) + "," + str(random.randint(6, 10)) + "}"
    numRange2 = "{" + str(random.randint(0, 3)) + "," + str(random.randint(6, 10)) + "}"

    # Generate 2 character ranges (e.g. [a-z])
    charRange1 = "[" + random.choice('abcdefghijklm') + "-" + random.choice('nopqrstuvwxyz') + "]"
    charRange2 = "[" + random.choice('abcdefghijklm') + "-" + random.choice('nopqrstuvwxyz') + "]"

    # Generate 6 more segments for the ors
    index = random.randint(0, len(word1) - 2)
    segment3 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment4 = word2[index:index+2]
    index = random.randint(0, len(word1) - 2)
    segment5 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment6 = word2[index:index+2]
    index = random.randint(0, len(word1) - 2)
    segment7 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment8 = word2[index:index+2]

    # Generate 2 option based string matches
    or1 = "(" + segment3 + "|" + segment4 + "|" + segment5 + ")"
    or2 = "(" + segment6 + "|" + segment7 + "|" + segment8 + ")"

    match difficulty:
        case 'normal-easy': 
            index = random.randint(0, len(word1) - 3)
            regex = word1[index:index+3]

            matches = 0
            for word in words10k:
                if re.match('^.*' + regex + '.*$', word):
                    matches += 1
            
            if matches >= 50 and matches <= 1000 and regex not in words10k:
                return regex
            else:
                return generatePrompt(difficulty)
            
        case 'normal-hard':
            length = random.randint(3, 4)
            index = random.randint(0, len(word1) - length)
            regex = word1[index:index+length]

            matches = 0
            for word in words10k:
                if re.match('^.*' + regex + '.*$', word):
                    matches += 1
            
            if matches >= 20 and matches <= 500 and regex not in words10k:
                return regex
            else:
                return generatePrompt(difficulty)
            
        case 'regex-easy':
            options1 = [letter1, segment1, sb1]
            options2 = [letter2, segment2, sb2]
            begin = ['.+', '.*', letter1, letter2]
            connect = ['.+', '.*']

            match(random.randint(1, 8)):
                case 1: regex = random.choice(options1) + random.choice(connect)
                case 2: regex = random.choice(begin) + random.choice(options1)
                case 3: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2)
                case 4: regex = random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)
                case other: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)

            matches = 0
            for word in words10k:
                if re.match('^' + regex + '$', word):
                    matches += 1
            
            if matches >= 50 and matches <= 1000:
                return regex
            else:
                return generatePrompt(difficulty)
            
        case 'regex-hard':
            options1 = [letter1, segment1, sb1, nsb1, charRange1, or1]
            options2 = [letter2, segment2, sb2, nsb2, charRange2, or2]
            begin = ['.+', '.*', letter1, letter2, sb1, sb2]
            connect = ['.+', '.*', '+', '*', '+.+', '+.*', '?', numRange1, numRange2]

            match(random.randint(1, 8)):
                case 1: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2)
                case 2: regex = random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)
                case other: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)

            matches = 0
            for word in words10k:
                if re.match('^' + regex + '$', word):
                    matches += 1
            
            if matches >= 20 and matches <= 500:
                return regex
            else:
                return generatePrompt(difficulty)

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')

@client.event
async def on_message(message):
    global players, current_prompt, round_time, lives, game_running, mode

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
        
        if len(players) < 2:
            await message.channel.send('❌ Not enough players to start the game. ❌')
            return
        
        await message.channel.send('🏁 Starting game in 5 seconds. 🏁')
        await asyncio.sleep(5)
        game_running = True
        
        while len(players) > 1:

            await message.channel.send(f'⏲️ NEW ROUND: **{round(round_time, 1)} seconds** per player. ⏲️')

            for player in players:
                current_prompt = generatePrompt(mode)
                await message.channel.send(f"🛎️ {player.mention}, it's your turn. Prompt: `{current_prompt}` 🛎️")

                def check(m):
                    if mode == 'normal-easy' or mode == 'normal-hard':
                        return m.author == player and current_prompt in m.content and m.content in words84k
                    else:
                        return m.author == player and re.match('^' + current_prompt + '$', m.content) and m.content in words84k

                while True:
                    try:
                        msg = await client.wait_for('message', check=check, timeout=round_time)
                        await message.channel.send(f'🎉 Correct! 🎉')
                        break

                    except asyncio.TimeoutError:
                        lives[player] -= 1

                        await message.channel.send(f"⏰ Time's up, {player.mention}. **-1 life** ({lives[player]} lives remaining) ⏰")

                        if lives[player] == 0:
                            await message.channel.send(f'❌ {player.mention} has been eliminated. ❌')
                            players.remove(player)
                            del lives[player]

                        await message.channel.send(f'💣 **WORD BOMB!** If nobody solves {player.mention}\'s prompt in the next 5 seconds, **EVERYBODY** loses a life. 💣')

                        def stealCheck(m):
                            if mode == 'normal-easy' or mode == 'normal-hard':
                                return m.author != player and current_prompt in m.content and m.content in words84k
                            else:
                                return m.author != player and re.match('^' + current_prompt + '$', m.content) and m.content in words84k
                        
                        try:
                            msg = await client.wait_for('message', check=stealCheck, timeout=5)

                            lives[msg.author] += 1

                            await message.channel.send(f'🎉 Congrats, {msg.author.mention}. **+1 life** ({lives[msg.author]} lives remaining) 🎉')

                        except asyncio.TimeoutError:
                            await message.channel.send(f'💥 Nobody solved {player.mention}\'s prompt. Everyone **-1 life**. 💥')
                            
                            for p in players:
                                if lives[p] == 0:
                                    await message.channel.send(f'❌ {p.mention} has been eliminated. ❌')
                                    players.remove(p)
                                    del lives[p]

                        break
                
                if len(players) == 1:
                    break

            if round_time > 5:
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
                      description="> Rule 1: A period . matches any letter.\n\ne.g. some answers to `p..` are:\n✅ pod | ✅ pet | ❌ package | ❌ egg\n\ne.g. some answers to `.a.` are:\n✅ bar | ✅ cat | ❌ fraud | ❌ each\n\n> Rule 2: Square brackets [ ] match one of the letters inside.\n\ne.g. some answers to `b[aeu]d` are:\n✅ bad | ✅ bed | ❌ bid | ❌ abode\n\ne.g. some answers to `[aeiou]....` are:\n✅ apple | ✅ icons | ❌ eggs | ❌ underneath\n\n> Rule 3: A plus + matches one or more of the previous character.\n\ne.g. some answers to `o.+n` are:\n✅ overthrown | ✅ omen | ❌ on | ❌ oregano\n\ne.g. some answers to `.+es+` are:\n✅ prowess | ✅ times | ❌ me | ❌ basin\n\n> Rule 4: An asterisk * matches zero or more of the previous character.\n\ne.g. some answers to `o.*n` are:\n✅ on | ✅ overthrown | ❌ omens | ❌ oregano\n\ne.g. some answers to `.*e.*` are:\n✅ eggplant | ✅ ledge | ❌ sasquatch | ❌ banana",
                      colour=0xffffff)
        regexAdditional = discord.Embed(title="Additional Rules — These are all you need for the `regex-hard` mode.",
                      description="> Rule 5: [a-x] matches any character between a and x\n\ne.g. some answers to `n[e-p]t` are:\n✅ net | ✅ not | ❌ nut | ❌ nat\n\ne.g. some answers to `b[a-o][a-z][b-x]` are:\n✅ barn | ✅ bore | ❌ bush | ❌ bet\n\n> Rule 6: A square bracket with a caret at the start [^ ] matches any character not inside.\n\ne.g. some answers to `.[^ai].` are:\n✅ bed | ✅ cut | ❌ cat | ❌ rip\n\ne.g. some answers to `.[^aeiou]` are:\n✅ at | ✅ by | ❌ no | ❌ sauce\n\n> Rule 7: Parentheses are capturing groups ( ) and vertical bars | mean OR. \n\ne.g. some answers to `(eg|pa|ba).` are:\n✅ egg | ✅ pat | ❌ leg | ❌ nap\n\ne.g. some answers to `(bo|ro)(ok|ne)` are:\n✅bone | ✅rook | ❌shook | ❌borrow\n\n> Rule 8: A question mark ? matches zero or one of the previous character.\n\ne.g. some answers to `p?o?d` are:\n✅ pod | ✅ proud | ❌ prone | ❌ podge\n\ne.g. some answers to `a.?` are:\n✅ a | ✅ at | ❌ axe | ❌ amplifier\n\n> Rule 9: Curly brackets {m, n} match the previous character between m and n times.\n\ne.g. some answers to `fre{1,2}.+` are:\n✅ fresh | ✅ freeze | ❌ freeeeeze | ❌ freeeeeeeeeeeeeze\n\ne.g. some answers to `.{3,5}` are:\n✅ egg | ✅ eggs | ❌ eggplant | ❌ eggplants",
                      colour=0xffffff)
        await message.channel.send(embed=regexExplanation)
        await message.channel.send(embed=regexBasic)
        await message.channel.send(embed=regexAdditional)

    elif message.content == '!help' or message.content == '!mode' or message.content == '!modes':
        helpCommands = discord.Embed(title="Commands:",
                      description="`!help` — Opens the commands menu.\n\n`!help regex` — A simple explanation of how to regex.\n\n`!mode normal-easy` — Basic word game where you complete a word from a 3-character segment.\n\n`!mode normal-hard` — Basic word game where you complete a word from a 3 or 4 character segment, with harder prompts.\n\n`!mode regex-easy` — Word game where you try to match a word to the given regular expression. Contains only [ ] . * + \n\n`!mode regex-hard` — Word game where you try to match a word to the given regular expression. Contains all regex syntax.\n\n`!start` — If no game is currently running, starts a game after 10 seconds.\n\n`!join` — Join a game that is in the process of starting.\n\n`!players` — List all players currently in the game.\n\n`!stop` — End the currently active game.",
                      colour=0xffffff)
        await message.channel.send(embed=helpCommands)

    # Modes
    elif message.content == '!mode normal-easy':
        await message.channel.send('✅ Game changed to normal mode, easy difficulty. ✅')
        mode = 'normal-easy'
    elif message.content == '!mode normal-hard':
        await message.channel.send('✅ Game changed to normal mode, hard difficulty. ✅')
        mode = 'normal-hard'
    elif message.content == '!mode regex-easy':
        await message.channel.send('✅ Game changed to regex mode, easy difficulty. ✅')
        mode = 'regex-easy'
    elif message.content == '!mode regex-hard':
        await message.channel.send('✅ Game changed to regex mode, hard difficulty. ✅')
        mode = 'regex-hard'

client.run(' :) ')
