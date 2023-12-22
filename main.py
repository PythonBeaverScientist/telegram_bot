from typing import Final, Union

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from weather_api_handler import BaseRequest, ResponseFormatter
import json
from user_response_handler import UserResponseHandler
from db_orm import add_new_unique_user, add_users_request
from db_client import DBClient
from base_log import LoggerHand

# Создание экземпляра клиента базы данных и sqlalchemy_engine
db_client: DBClient = DBClient()
db_engine = db_client.create_sql_alchemy_engine()

# Создание логгера
log = LoggerHand(__name__, f"loggers/{__name__}.log")

with open('credentials/bot_verification.json', 'r') as file:
    bot_credentials: dict = json.load(file)

TOKEN: Final[str] = bot_credentials['bot_token']
BOT_USERNAME: Final[str] = bot_credentials['bot_username']


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_new_unique_user(update.message.from_user, db_engine)
    await update.message.reply_text('Hello! Thanks for chatting with me. How can I help you?')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This will be some useful information in the future!')


async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your id is: {update.message.from_user.id}")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This will be some useful information in the future!')


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_hand: UserResponseHandler = UserResponseHandler(update.message)
    request = BaseRequest()
    func_args: Union[None, dict] = resp_hand.transform_msg_com()
    add_users_request(update, db_engine, func_args)
    if func_args:
        response: requests.Response = request.get_response(func_args.get('first_arg'),
                                                           func_args.get('second_arg'), func_args.get('third_arg'))
        api_response_formatter = ResponseFormatter(response, func_args.get('first_arg'))
        answer: str = api_response_formatter.answer
        if isinstance(answer, str):
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f'Something must be wrong with the server. Please try again')
    else:
        await update.message.reply_text('Please explain yourself in more comprehensible expressions')


# Responses
def handle_responses(user_response: str) -> str:
    user_response: str = user_response.lower()
    if 'hello' or 'hey' or 'привет' in user_response:
        return 'Hello you there!'
    else:
        return 'Please explain yourself in more comprehensible expressions'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    message_text: str = update.message.text
    print(f"User: {update.message.chat.id} in {message_type}: {message_text}")
    if message_type == 'group':
        if BOT_USERNAME in message_text:
            new_message_text: str = message_text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_message_text)
        else:
            return
    else:
        response: str = handle_responses(message_text)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.error(f"Update caused the following error: {context.error}")


if __name__ == '__main__':
    log.logger.debug('Starting bot')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('get_id', get_id_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('weather', weather_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polling
    app.run_polling(poll_interval=3)
