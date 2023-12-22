from typing import Final, Union, Optional, List
import aiohttp
from base_log import LoggerHand
from dictionary_model import WordDef
import os

log = LoggerHand(__name__, f"loggers/{__name__}.log")


class DictionaryRequest:
    def __init__(self):
        self.BASE_API: Final[str] = 'https://api.dictionaryapi.dev/api/v2/entries/en/'
        self.headers: dict = {'Content-Type': 'application/json'}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def get_response(self, en_word: str) -> aiohttp.ClientResponse:
        url_address: str = f"{self.BASE_API}{en_word.lower()}"
        response: aiohttp.ClientResponse = await self.session.get(url_address, headers=self.headers)
        return response

    async def get_audio(self, audio_http: str) -> aiohttp.ClientResponse:
        response: aiohttp.ClientResponse = await self.session.get(audio_http, headers=self.headers)
        return response

    async def close_session(self):
        await self.session.close()


class DefinitionFormatter:
    def __init__(self, response: aiohttp.ClientResponse):
        self.response: aiohttp.ClientResponse = response
        self.AUDIO_REP = 'words_audio_files'

    async def format_definition_response(self) -> Optional[List[dict]]:
        if 200 <= self.response.status < 300:
            json_res: List[dict] = await self.response.json()
            return json_res
        else:
            log.logger.warning(f'The code status of the response is following: {self.response.status}'
                               f'and the msg is: {await self.response.text()}')
            return None

    @staticmethod
    def edit_definition_json(json_res: Union[List[dict], None]) -> Union[List[WordDef], None]:
        if isinstance(json_res, list):
            word_lst: list = []
            for word in json_res:
                user_word: str = word.get('word')
                audio_http: str = word.get('phonetics')[0].get('audio')
                if audio_http == "" and len(word.get('phonetics')) > 1:
                    audio_http: str = word.get('phonetics')[1].get('audio')
                    if audio_http == "" and len(word.get('phonetics')) > 2:
                        audio_http: str = word.get('phonetics')[2].get('audio')
                for meaning in word.get('meanings'):
                    part_of_speech: str = meaning.get('partOfSpeech')
                    for definition in meaning.get('definitions'):
                        word_definition: str = definition.get('definition')
                        example: str = definition.get('example')
                        word_def: WordDef = WordDef(user_word, audio_http, part_of_speech, word_definition, example)
                        word_lst.append(word_def)
            return word_lst
        else:
            return None

    async def load_audio_req(self, audio_res: aiohttp.ClientResponse, audio_file_name: str) -> str:
        file_path = f"{self.AUDIO_REP}/{audio_file_name}.mp3"
        if os.path.isfile(file_path):
            with open(file_path, 'wb') as mp3_ile:
                mp3_ile.write(await audio_res.read())
        return file_path


class MsgCreator:
    def __init__(self, word_lst: List[WordDef],  audio_file_path: str):
        self.word_lst: List[WordDef] = word_lst
        self.audio_file_path: str = audio_file_path

    def create_msg_for_user(self) -> str:
        msg_for_user: str = f"Word: {self.word_lst[0].user_word}\n\n"
        for word_def in self.word_lst:
            msg_for_user += f"\nPart of speech: {word_def.part_of_speech}\n" \
                            f"Definition: {word_def.definition}\n"
            if word_def.example is not None:
                msg_for_user += f"Example: {word_def.example}\n"
        return msg_for_user
