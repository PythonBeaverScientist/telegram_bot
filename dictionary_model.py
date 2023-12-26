from dataclasses import dataclass
from typing import Optional


@dataclass(init=True, repr=True, eq=True)
class WordDef:
    user_word: Optional[str] = None
    audio_http: Optional[str] = None
    part_of_speech: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
