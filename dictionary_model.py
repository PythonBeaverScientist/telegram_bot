from dataclasses import dataclass
from typing import Union


@dataclass(init=True, repr=True, eq=True)
class WordDef:
    user_word: Union[str, None] = None
    audio_http: Union[str, None] = None
    part_of_speech: Union[str, None] = None
    definition: Union[str, None] = None
    example: Union[str, None] = None
