import asyncio
import datetime
import json
import os
import re

import dotenv
import openai
from telegram import constants, Update, Message
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, Defaults

import config

dotenv.load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
openai.api_key = OPENAI_TOKEN
TARGET_USERNAMES = json.loads(os.getenv("TARGET_USERNAMES"))
ALLOWED_CHATS = json.loads(os.getenv("ALLOWED_CHATS"))


def log_message(chat_history: list, message_sender: str, message_timestamp: str, message_text: str, reply: Message=None):
    reply_to = f"[Replying to {reply['from'].first_name}'s message sent at {reply.date.strftime(config.DATE_FORMAT)}]" if reply else ""
    message = f"{message_sender}, [{message_timestamp}]{reply_to}\n{message_text}"
    chat_history.append(message)
    print(message)
    while len(chat_history) > config.CHAT_HISTORY_LENGTH:
        chat_history.pop(0)
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get chat and message information
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    message_sender = message['from'].first_name
    message_sender_username = message['from'].username
    message_timestamp = message.date.strftime(config.DATE_FORMAT)
    message_text = message.text if not message.sticker else message.sticker.emoji
    message_reply = message.reply_to_message
    log_message(chat_history, message_sender, message_timestamp, message_text, message_reply)

    # Only run prompts for messages from certain users
    if message_sender_username not in TARGET_USERNAMES:
        return
    
    # Check message meaness
    check_prompt = config.generate_check_prompt(message_text)
    sentiment_check = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature = 0.2,
        max_tokens = 1,
        messages=[
            {"role": "system", "content": config.SYSTEM_ROLE_CHECK},
            {"role": "user", "content": check_prompt}
        ]
    )
    sentiment_response = sentiment_check.choices[0].message.content
    print("SENTIMENT:", sentiment_response)
    sentiment_cleaned = re.sub(r'\D', '', sentiment_response)
    sentiment_int = int(sentiment_cleaned) if sentiment_cleaned != "" else 0
    print("SENTIMENT CLEANED:", sentiment_int)
    if not (4 <= sentiment_int <= 9):
        return
    
    # Generate roast reply
    thread = "\n\n".join(chat_history)
    main_prompt = config.generate_main_prompt(message_sender, thread)
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": config.SYSTEM_ROLE_MAIN},
            {"role": "user", "content": main_prompt}
        ]
    )
    main_response = completion.choices[0].message.content
    main_response_cleaned_left_quote = re.sub(r'^["\']', '', main_response)
    main_response_cleaned_right_quote = re.sub(r'["\']$', '', main_response_cleaned_left_quote)
    main_response_cleaned_you = re.sub(r'^You: ', '', main_response_cleaned_right_quote)
    print("RESPONSE:", main_response)
    print("\033[91m" + "CLEANED RESPONSE: " + main_response_cleaned_you + "\033[00m")
    log_message(chat_history, "You", datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime(config.DATE_FORMAT), main_response, message)
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=message_id, text=main_response)


if __name__ == '__main__':
    with open("chat_history.json", "rb") as file:
        chat_history = json.load(file)
        print("\033[92m" + "Chat history:" + "\033[00m")
        for message in chat_history:
            print(message)
    defaults = Defaults(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).defaults(defaults).build()
    message_handler = MessageHandler(filters.Chat(chat_id=ALLOWED_CHATS) & (filters.TEXT | filters.Sticker.ALL) & (~filters.COMMAND) & filters.UpdateType.MESSAGE, handle_message)
    application.add_handler(message_handler)
    print("\033[92m" + "Bot started, waiting for messages..." + "\033[00m")
    asyncio.run(application.run_polling())
