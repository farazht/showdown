import discord
import asyncio

# Create a new client instance
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Create a list of players, and turn/cycles counters
players = []
turn = None
cycles = 0

# When the bot is ready, print a message
@client.event
async def on_ready(): 
    print(f'Successfully logged in as {client.user}')

# Read messages and respond to commands
@client.event
async def on_message(message):
    global players, turn, cycles
    
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Start a new game
    if message.content == '!start':

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

            await message.channel.send(f"Game started. {players[0].mention}, it's your turn.")
            turn = 0
    
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

    # Stop game if it is in progress and the message author is a current player
    elif message.content == '!stop' and turn is not None and message.author in players:
        players = []
        turn = None
        await message.channel.send('Game stopped.')

    # Game in progress and message from current player (this takes the turn response, keep this below commands)
    elif turn is not None and message.author == players[turn]:

        # Print the message (for testing)
        await message.channel.send(f'You said: {message.content}')

        # Cycle to the next player, returning to 0 when last player is reached
        turn = (turn + 1) % len(players)

        # If turn is 0, one round cycle has ended. Game then continues to next turn below
        if turn == 0:
            await message.channel.send('(test) CYCLE END')
            cycles += 1

        # Game continues to next turn
        if turn < len(players):
            await message.channel.send(f"{players[turn].mention}, it's your turn.")

# Run the bot
client.run(' :) ')
