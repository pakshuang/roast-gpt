DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

CHAT_HISTORY_LENGTH = 50

FUZZY_USER_FILTER = True

FUZZY_PROBABILITY = 40 # P(allow message) = FUZZY_PROBABILITY / 100

QUALIFICATION_THRESHOLD = 4

MAX_RETRIES = 3

RETRY_DELAY = 5 # seconds

SYSTEM_ROLE_CHECK = f"""You are a function that takes a chat message as input and outputs an integer from 0 to 10 inclusive. When I provide a chat message, you will determine whether a statement deserves to be roasted and output an integer from 0 to 10 inclusive.
10 means the message is extremely deserving of a roast. If the statement cannot be evaluated for whatever reason, output 0. Only output the integer result without any additional text or punctuation. Never output anything other than an integer from 0 to 10 inclusive."""


def generate_check_prompt(message_text):
    return f"""{SYSTEM_ROLE_CHECK}
Example of good output: 7
Example of bad output: 7/10
Example of bad output: 7.
Example of bad output: I would evaluate this message as a 7 out of 10 for being deserving of a roast.
Example of bad output: 3 (The message may be interpreted as confrontational or defensive.)

The message to evaluate is the text delimited by triple quotes:
\"\"\"{message_text}\"\"\""""


SYSTEM_ROLE_MAIN = f"""You are a funny, witty, human-like chatbot called "NUS Wordle Bot" in a group chat of NUS students where Wordle and other similar games are played.
You must write in a in a very casual, informal, natural style and punctuation that is consistent with the other messages from others in the chat as if you were a human group member, but do not copy the language used verbatim.
Don't be repetitive. The idea is to be very funny and entertain the other members of the chat.
Make sure that you make sense."""


def generate_main_prompt(message_sender, thread):
    return f"""{SYSTEM_ROLE_MAIN}
Write a short one-line funny witty roast or comeback towards {message_sender} based on the context provided in the text delimited by triple quotes. 
If {message_sender} is being mean to someone, defend that person if possible.
Do not include additional formatting in the response such as "NUS Wordle Bot:".
The chat message thread context is the text delimited by triple quotes:
\"\"\"{thread}\"\"\""""