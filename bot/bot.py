import os
import discord
import requests

TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = 'BOT-TEST'

client = discord.Client()


def help_prompt():
	return 'Type "help" for assistance!'


# TODO
def help_message():
	"""
	Message to return when the User requests help (replies to "help").

	<minutes> <increment> <OPTIONAL: rated> <OPTIONAL: FEN>

	Minutes: {Min: 1, Max: 180}
	Increment: {Min: 0, Max: 60}
	Rated: {'r', 'u'}
	FEN: ...

	If FEN is provided, game must be Unrated.
	"""

	NAME = 'ChessChallengeBot'
	p1 = f"""Hello! :wave: I'm {NAME}!
I help the Chess Dojo create custom challenges!
---------------------------------------------------------------------------
:question:**How does it work?**
- All you have to do is send me a message with the game details and I'll create a game for you!
- I will send you two links: one for the White player and another for the Black player.
*Note: Once you finish the challenge playing as one side or the other, clicking "Rematch" will automatically reverse the colors.*
- Once I create the challenge, the two players will have 24 hours to chick on the link to join the game.

:question:**How do I create a challenge?**
I need to know a few things in order to create the challenge:
:one: **Minutes** [*Required*]
    *Number of minutes on each players clock. Min: 1, Max: 180*
:two: **Increment** [*Required*]
    *Number of seconds added to the clock after each move is made. Min: 0, Max: 60*
:three: **Rated** [*Optional*] :arrow_right: *Default: Unrated*
    *Whether or not the game affects the players rating. ["r" > rated | "u" > unrated]*
:four: **FEN** [*Optional*] :arrow_right: *Default: Starting position*
    *Valid FEN of the position you want to start from.*
   
:question:**How do I format the message?**
The message should be formatted as such:
> <minutes> <increment> <rated> <FEN>

- *There should be a space between each element of the challenge.*
- *If you are including a FEN, the game cannot be rated. (Either leave <rated> blank or set it to "u".)*"""
	p2 = """---------------------------------------------------------------------------
:exclamation: **Examples**

*15 minute game, 5 second increment, unrated from the starting position:*
> 15 5

*15 minute game, 5 second increment, rated from the starting position:*
> 15 5 r

*5 minute game, 30 second increment, unrated from a given FEN:*
> 5 30 4k3/8/8/8/8/8/4P3/4K3 w - - 0 1
*or*
> 5 30 u 4k3/8/8/8/8/8/4P3/4K3 w - - 0 1
---------------------------------------------------------------------------
Try it out!
If you ever want me to repeat this message, just type "help"!
"""
	return p1, p2


def interpret_challenge(text):
    """
    Returns a dictionary with {OK: ..., URL: ..., PARAMS: ..., MESSAGE: ...}.
    This will be fed into a `request.post()`
    """
   
    # Instantiate min/max.
    MIN_MINUTES = 1
    MAX_MINUTES = 180
    MIN_INC = 0
    MAX_INC = 60
    RATED_OPTIONS = {'r', 'u'}
   
    # Instantiate variables.
    OK = True
    URL = 'https://lichess.org/api/challenge/open'
    PARAMS = {
        'rated': None,
        'clock.limit': None,
        'clock.increment': None,
        'fen': None
    }
    MESSAGE = None
   
    rated = None
   
    # Split text.
    s = text.split()
   
    # Does the challenge satisfy minimum requirements?
    if len(s) < 2:
        OK = False
        MESSAGE = 'Must include at least: "<minutes> <increment>".'
    if not OK:
        return dict(OK=OK, MESSAGE=MESSAGE)
   
    # Are minutes input correctly?
    try:
        minutes = int(s[0])
       
        # Minutes constraints.
        if minutes < MIN_MINUTES:
            minutes = MIN_MINUTES
        elif minutes > MAX_MINUTES:
            minutes = MAX_MINUTES
    except ValueError:
        OK = False
        MESSAGE = f'Could not interpret <minutes = {s[0]}>.'
    if not OK:
        return dict(OK=OK, MESSAGE=MESSAGE)
       
    # Is increment input correctly?
    try:
        increment = int(s[1])
       
        # Minutes constraints.
        if increment < MIN_INC:
            increment = MIN_INC
        elif increment > MAX_INC:
            increment = MAX_INC
    except ValueError:
        OK = False
        MESSAGE = f'Could not interpret <increment = {s[1]}>.'
    if not OK:
        return dict(OK=OK, MESSAGE=MESSAGE)
   
    # Just a time?
    if len(s) == 2:
        PARAMS = {
            'rated': rated,
            'clock.limit': minutes*60,
            'clock.increment': increment,
            'fen': None
        }
        return dict(OK=OK, URL=URL, PARAMS=PARAMS, MESSAGE=MESSAGE)
   
    # If <time inc rated>, then assert correctness.
    if len(s) == 3:
        if str(s[2]).lower() not in RATED_OPTIONS:
            OK = False
            MESSAGE = f'"Rated" should be either "r"(rated) or "u"(unrated). Recieved: <"rated" = {s[2]}>.'
        else:
            if str(s[2]).lower() == 'r':
                rated = 'true'
            else:
                rated = None
           
            # EVERYTHING GOOD.
            PARAMS = {
                'rated': rated,
                'clock.limit': minutes*60,
                'clock.increment': increment,
                'fen': None
            }
            return dict(OK=OK, URL=URL, PARAMS=PARAMS, MESSAGE=MESSAGE)
    if not OK:
        return dict(OK=OK, MESSAGE=MESSAGE)
   
    # Check FEN compatibility.
    if (len(s) > 3) and (len(s[2]) == 1) and (str(s[2]).lower() != 'u'):
        OK = False
        MESSAGE = f'Games with a FEN must be unrated. Recieved: <"rated" = {s[2]}>'
    if not OK:
        return dict(OK=OK, MESSAGE=MESSAGE)
   
    # Extracting rated and FEN.
    if (len(s) > 3) and (s[2] in RATED_OPTIONS):
        if str(s[2]).lower() == 'r':
            rated = 'true'
        else:
            rated = None
   
    if str(s[2]).lower() in RATED_OPTIONS:
        FEN = ' '.join(s[3:])
    else:
        FEN = ' '.join(s[2:])
   
    PARAMS = {
        'rated': rated,
        'clock.limit': minutes*60,
        'clock.increment': increment,
        'fen': FEN
    }
    return dict(OK=OK, URL=URL, PARAMS=PARAMS, MESSAGE=MESSAGE)


# @client.event
# async def on_ready():
# 	for guild in client.guilds:
# 		if guild.name == GUILD:
# 			break
# 	print(f'{client.user} has connected to Discord!')
# 	print(f'Guild: {guild.name} [ id: {guild.id} ]')

@client.event
async def on_message(message):
	if message.channel.name != 'bot-lounge':
		return
	if message.author == client.user:
		return

	# if not message.guild:
	if message.content.lower() == 'help':
		parts = help_message()
		for p in parts:
			await message.channel.send(p)
	else:
		try:
			d = interpret_challenge(message.content)
			if not d.get('OK'):
				d_message = d.get('MESSAGE')
				await message.channel.send(f'Challenge Failed :thumbsdown:\n{d_message}\n{help_prompt()}')
			else:
				r = requests.post(d.get('URL'), d.get('PARAMS'))
				if not r.ok:
					await message.channel.send(f'Challenge Failed :thumbsdown:\n{r.json()}')
					return
				else:
					challenge = r.json()
					await message.channel.send(f'Challenge Created! :thumbsup:\nWhite - Join Game: {challenge.get("urlWhite")}\nBlack - Join Game: {challenge.get("urlBlack")}')
			# # Interpretation logic.
			# FORMATTED_FEN = message.content.replace(' ', '_')
			# URL = f'https://lichess.org/editor/{FORMATTED_FEN}'
			# await message.channel.send(URL)
		except discord.errors.Forbidden:
			pass


client.run(TOKEN)
