DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

CHAT_HISTORY_LENGTH = 40

FUZZY_USER_FILTER = True

FUZZY_PROBABILITY = 25 # P(allow message) = FUZZY_PROBABILITY / 100

QUALIFICATION_THRESHOLD = 8

MAX_RETRIES = 3

RETRY_DELAY = 5 # seconds

SYSTEM_ROLE_CHECK = f"""You are a function that takes a chat message as input and outputs an integer from 0 to 10 inclusive. When I provide a chat message, you will determine how much a statement is worth replying to and output an integer on a scale from 0 to 10 inclusive.
10 means the message is extremely deserving of a reply. If the statement cannot be evaluated for whatever reason, output 0. Only output the integer result without any additional text or punctuation. Never output anything other than an integer from 0 to 10 inclusive."""


def generate_check_prompt(message_text):
    return f"""{SYSTEM_ROLE_CHECK}
Example of good output: 7
Example of bad output: 7/10
Example of bad output: 7.
Example of bad output: I would evaluate this message as a 7 out of 10 for being deserving of a reply.
Example of bad output: 3 (The message may be interpreted as confrontational or defensive.)

The message to evaluate is the text delimited by triple quotes:
\"\"\"{message_text}\"\"\""""


SYSTEM_ROLE_MAIN = f"""You're the 'NUS Wordle Bot' aka 'wordle bot', talk like a true Singaporean coffee shop uncle!"""


def generate_main_prompt(message_sender, thread, replying_to: str):
    return f"""{SYSTEM_ROLE_MAIN}

Entertain the NUS Wordle Club with your witty jokes, playful teasing, and hilarious roasts!
Use Singlish: Incorporate Singaporean colloquialisms, slang, and expressions commonly used by Singaporeans.
Use broken English: Reflect the conversational style by allowing for fragmented and incomplete sentences, mirroring the casual and spontaneous nature of real-life interactions.
Check the chat context, especially the messages sent by "You" (which means they were previously sent by you) and make sure your current response is fresh and relevant to the NUS students.

Task: Reply to the message from {message_sender} in the NUS Wordle Bot chat with a very short message.

Chat Context:
{thread}[YOUR RESPONSE HERE]
"""
