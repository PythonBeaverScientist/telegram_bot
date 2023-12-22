from typing import Final, Union, Optional, List
import requests
from base_log import LoggerHand
from dictionary_model import WordDef
import os

log = LoggerHand(__name__, f"loggers/{__name__}.log")


class DictionaryRequest:
    def __init__(self):
        self.BASE_API: Final[str] = 'https://api.dictionaryapi.dev/api/v2/entries/en/'
        self.headers: dict = {'Content-Type': 'application/json'}

    def get_response(self, en_word: str) -> requests.Response:
        response: requests.Response = requests.get(f"{self.BASE_API}{en_word.lower()}", headers=self.headers)
        return response

    def get_audio(self, audio_http: str) -> requests.Response:
        response: requests.Response = requests.get(audio_http, headers=self.headers)
        return response


class DefinitionFormatter:
    def __init__(self, response: requests.Response):
        self.response: requests.Response = response
        self.AUDIO_REP = 'words_audio_files'

    def format_definition_response(self) -> Optional[List[dict]]:
        if 200 <= self.response.status_code < 300:
            json_res: List[dict] = self.response.json()
            return json_res
        else:
            log.logger.warning(f'The code status of the response is following: {self.response.status_code}'
                               f'and the msg is: {self.response.text}')
            return None

    @staticmethod
    def edit_definition_json(json_res: Union[List[dict], None]) -> Union[List[WordDef], None]:
        if isinstance(json_res, list):
            word_lst: list = []
            for word in json_res:
                user_word: str = word.get('word')
                audio_http: str = word.get('phonetics')[0].get('audio')
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

    def load_audio_req(self, audio_res: requests.Response, audio_file_name: str) -> str:
        file_path = f"{self.AUDIO_REP}/{audio_file_name}.mp3"
        if os.path.isfile(file_path):
            with open(file_path, 'wb') as mp3_ile:
                mp3_ile.write(audio_res.content)
        return audio_file_name
