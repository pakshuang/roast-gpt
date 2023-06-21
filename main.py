import asyncio
from datetime import datetime
import os
import re

import dotenv
import openai
from telegram import constants, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes
from telegram.ext.filters import MessageFilter

import config

dotenv.load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
openai.api_key = OPENAI_TOKEN
TARGET_USERNAMES = os.getenv("TARGET_USERNAMES")
ALLOWED_CHATS = os.getenv("ALLOWED_CHATS")


class MessageChatFilter(MessageFilter):
    def filter(self, message: str):
        return message.chat.id in ALLOWED_CHATS


def log_message(previous_messages: list, message_sender: str, message_timestamp: str, message_text: str):
    message = f"{message_sender}, [{message_timestamp}]\n{message_text}"
    print(message)
    previous_messages.append(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get chat and message information
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    message_sender = update.message['from'].first_name
    message_sender_username = update.message['from'].username
    message_timestamp = update.message.date.strftime(config.DATE_FORMAT)
    message_text = update.message.text

    # Handle chat history
    log_message(previous_messages, message_sender, message_timestamp, message_text)
    while len(previous_messages) > config.CHAT_HISTORY_LENGTH:
        previous_messages.pop(0)

    # Only run for messages from certain users
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
    
    thread = "\n\n".join(previous_messages)
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
    print("CLEANED RESPONSE:", main_response_cleaned_you)
    log_message(previous_messages, "You", datetime.now().strftime(config.DATE_FORMAT), main_response)
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=message_id, text=main_response)


if __name__ == '__main__':
    previous_messages = []
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    message_handler = MessageHandler(MessageChatFilter() & filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)
    print("Bot started, waiting for messages...")
    asyncio.run(application.run_polling())