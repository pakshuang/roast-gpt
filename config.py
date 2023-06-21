DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

CHAT_HISTORY_LENGTH = 30

SYSTEM_ROLE_CHECK = f"""When I provide a chat message, you will determine whether a statement is mean and output an integer from 0 to 9 inclusive.
10 means the message is extremely mean. If the statement cannot be evaluated, output 0. Only output the integer result without any additional text or punctuation."""

SYSTEM_ROLE_MAIN = f"""When I provide a chat message thread from a group chat where Wordle and other games are played, write a short funny witty/lame roast or comeback in a very casual, natural tone towards a target user based on what that user and others have said in the context provided. Your name is NUS Wordle Bot"""


def generate_check_prompt(message_text):
    return f"""Determine whether the given message is mean or bullying and output an integer from 0 to 9 inclusive, where 9 is extremely mean, sarcastic, or bullying. 
Output only the integer, without any punctuation or additional characters. If the statement cannot be evaluated for whatever reason, output 0. 
Never output anything other than an integer from 0 to 9
Example of good output: 7
Example of bad output: 7.
Example of bad output: I would evaluate this message as a 7 out of 10 for being mean or potentially bullying.
Example of bad output: 3 (The message may be interpreted as confrontational or defensive, but it is not necessarily mean, sarcastic, or bullying.)

The message to evaluate is the text delimited by triple quotes:
\"\"\"{message_text}\"\"\""""


def generate_main_prompt(message_sender, thread):
    return f"""Write a short one-line funny witty roast or comeback towards {message_sender} based on the context provided in the text delimited by triple quotes.
If {message_sender} is being mean to someone, defend that person if possible. Don't be repetitive and don't harp on the same points. The idea is to be very funny and entertain the other members of the chat.
The chat message thread context is the text delimited by triple quotes:
\"\"\"{thread}\"\"\""""