import discord, asyncio, random, string, re

# Create a new client instance
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
turn = None
cycles = 0
bomb = False
currentPrompt = 'a'
mode = 'normal'

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
    index = random.randint(0, len(word2) - 2)
    segment3 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment4 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment5 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment6 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment7 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    segment8 = word2[index:index+2]

    # Generate 2 option based string matches
    or1 = "(" + segment3 + "|" + segment4 + "|" + segment5 + ")"
    or2 = "(" + segment6 + "|" + segment7 + "|" + segment8 + ")"

    match difficulty:
        case 'normal': 
            index = random.randint(0, len(word1) - 3)
            regex = word1[index:index+3]

            matches = 0
            for word in words10k:
                if re.match('^.*' + regex + '.*$', word):
                    matches += 1
            
            if matches >= 100:
                return regex
            else:
                return generatePrompt(difficulty)
            
        case 'hard':
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
            
        case 'extreme':
            options1 = [letter1, segment1, sb1, nsb1, charRange1, or1]
            options2 = [letter2, segment2, sb2, nsb2, charRange2, or2]
            begin = ['.+', '.*', letter1, letter2, sb1, sb2]
            connect = ['.+', '.*', '+', '*', '+.+', '+.*', '?', numRange1, numRange2]

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
            
            if matches >= 20 and matches <= 500:
                return regex
            else:
                return generatePrompt(difficulty)

# When the bot is ready, print a message
@client.event
async def on_ready(): 
    print(f'Successfully logged in as {client.user}')

# Read messages and respond to commands
@client.event
async def on_message(message):
    global players, turn, cycles, bomb, currentPrompt, mode

    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # ==================
    # COMMANDS: PRE-GAME
    # ==================
    
    # Start a new game
    elif message.content == '!start':

        # If turn is not None, a game is already in progress
        if turn is not None:
            await message.channel.send('Game is already in progress.')

        # If there are less than 2 players, the game cannot start
        elif len(players) < 1: # !!! CHANGE THIS TO 2
            await message.channel.send('Need at least 2 players to start.')

        # All conditions met, start the game
        else:
            await message.channel.send('Game starting in 10 seconds...')
            
            await asyncio.sleep(10)

            turn = 0
            currentPrompt = generatePrompt(mode)
            await message.channel.send(f"{players[turn].mention}, it's your turn. Match `{currentPrompt}`")
    
    # Join the game
    elif message.content == '!join':

        # If turn is not None, a game is already in progress
        if turn is not None:
            await message.channel.send(f'Sorry {message.author.mention}, you cannot join an in-progress game.')

        # If the player is not in players, add them
        elif message.author not in players:
            players.append(message.author)
            await message.channel.send(f'{message.author.mention} has joined the game.')

        # If the player is already in players, do nothing
        else: 
            await message.channel.send(f'{message.author.mention}, you are already in the game.')
    
    # Print the list of players
    elif message.content == '!players':
        await message.channel.send(f'Players: {", ".join([p.mention for p in players])}')

    elif message.content == '!mode normal':
        await message.channel.send('Difficulty set to normal.')
        mode = 'normal'

    elif message.content == '!mode hard':
        await message.channel.send('Difficulty set to hard.')
        mode = 'hard'

    elif message.content == '!mode extreme':
        await message.channel.send('Difficulty set to extreme.')
        mode = 'extreme'

    # ==================
    # COMMANDS: MID-GAME
    # ==================

    # Stop game if it is in progress and the message author is a current player
    elif message.content == '!stop' and turn is not None and message.author in players:
        players = []
        turn = None
        await message.channel.send('Game stopped.')

    # ==================
    # TURNS AND GAMEPLAY
    # ==================

    # Game in progress and message from current turn player (this takes the turn response, keep this below commands)
    elif turn is not None and message.author == players[turn]:

        # Check the message against the regex
        if re.match('^' + currentPrompt + '.*' + '$', message.content) and message.content in words84k:
            await message.channel.send('Correct!')

            # Cycle to the next player, returning to 0 when last player is reached
            turn = (turn + 1) % len(players)

            # If turn is 0, one round cycle has ended. Game then continues to next turn below
            if turn == 0:
                cycles += 1
                await message.channel.send(f'Round cycle complete. Moving on to round {cycles + 1}.')

            # Game continues to next turn
            if turn < len(players):
                currentPrompt = generatePrompt(mode)
                await message.channel.send(f"{players[turn].mention}, it's your turn. Match `{currentPrompt}`")

    # Game in progress and message from non-current turn player
    # elif turn is not None and message.author != players[turn]:
        # await message.channel.send(f"{message.author.mention}, it's not your turn.")

# Run the bot
client.run(' :) ')
