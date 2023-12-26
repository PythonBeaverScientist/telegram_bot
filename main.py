from typing import Final, Union
import json
import aiohttp
import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from weather_api_handler import BaseRequest, ResponseFormatter
from user_response_handler import UserResponseHandler
from db_orm import add_new_unique_user, add_users_request
from db_client import DBClient
from base_log import LoggerHand
from dictionary_api_handler import DictionaryRequest, DefinitionFormatter, MsgCreator
# from command_handler import word_def_logic

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
    await update.message.reply_text('Hello! You may want to use /help command to discover my abilities.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_for_user: str = "This bot has 3 types of commands.\n" \
                        "1. /get_id - command that has no arguments. You get your ID and ID " \
                        "of the current chat.\n" \
                        "2. /en_word <some word> - command that has one argument - some english word. " \
                        "You get list of definitions for this word and audio file, that helps to understand " \
                        "how to pronounce this word correctly. \n" \
                        "3. /weather <current | forecast>, <city>, <quantity of days> - command has 2 or 3 arguments " \
                        "that separated by comma. \n" \
                        "If you want to find out weather at the current moment you need to use argument current " \
                        "and place. \n" \
                        "If want forecast for the next few days use argument forecast than place and quantity of " \
                        "days since the current day and forward. Maximum range for this parameter - 14."
    await update.message.reply_text(msg_for_user)


async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_for_user: str = f"Your ID is: {update.message.from_user.id}\n" \
                        f"Chat ID is: {update.message.chat_id}"
    await update.message.reply_text(msg_for_user)


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This will be some useful information in the future!')


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_hand: UserResponseHandler = UserResponseHandler(update.message)
    request = BaseRequest()
    func_args: Union[None, dict] = resp_hand.transform_msg_com()
    db_user_request = add_users_request(update, db_engine, func_args)
    if func_args:
        response: aiohttp.ClientResponse = await asyncio.create_task(request.get_response(func_args.get('first_arg'),
                                                           func_args.get('second_arg'), func_args.get('third_arg')))
        api_response_formatter = ResponseFormatter(response, func_args.get('first_arg'))
        answer: str = await asyncio.create_task(api_response_formatter.get_ready_answer(db_user_request, db_engine))
        await request.close_session()
        if isinstance(answer, str):
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f'Something must be wrong with the server. Please try again')
    else:
        await update.message.reply_text('Please explain yourself in more comprehensible expressions')


async def word_def_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_hand: UserResponseHandler = UserResponseHandler(update.message)
    en_word: str = resp_hand.transform_com_word_def()
    user_msg_model = add_users_request(update, db_engine, {'en_word': en_word})
    def_req = DictionaryRequest()
    get_text_task = asyncio.create_task(def_req.get_response(en_word))
    def_res = await get_text_task
    def_for = DefinitionFormatter(def_res)
    json_answer = await asyncio.create_task(def_for.format_definition_response())
    wrd_lst = def_for.edit_definition_json(json_answer)
    get_audio_task = asyncio.create_task(def_req.get_audio(wrd_lst[0].audio_http))
    audio_res = await get_audio_task
    audio_file_path = await asyncio.create_task(def_for.load_audio_req(audio_res, en_word))
    msg_creator: MsgCreator = MsgCreator(wrd_lst, audio_file_path)
    msg_for_user = msg_creator.create_msg_for_user(user_msg_model, db_engine)
    await def_req.close_session()
    audio: bytes = msg_creator.read_audio_file(audio_file_path)
    await update.message.reply_text(msg_for_user)
    await update.message.reply_audio(audio=audio, title=f"{en_word}.mp3")


# Responses
def handle_responses(user_response: str) -> str:
    user_response: str = user_response.lower()
    if 'hello' or 'привет' in user_response:
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
    app.add_handler(CommandHandler('en_word', word_def_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polling
    app.run_polling(poll_interval=3)
