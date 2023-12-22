from telegram import Update
from base_log import LoggerHand
import re

log = LoggerHand(__name__, f"loggers/{__name__}.log")


class UserResponseHandler:
    def __init__(self, resp_msg: Update.message):
        self.resp_msg: Update.message = resp_msg

    def transform_msg_com(self):
        msg_text: str = self.resp_msg.text
        command_pattern: str = r'(?P<com_type>\/\w+)\s+(?P<first_arg>\w+)'
        command: re.match = re.search(command_pattern, msg_text)
        com_pattern: str = ''
        if command.group('first_arg') == 'current':
            com_pattern: str = r'(?P<com_type>\/\w+)\s+(?P<first_arg>\w+)\,\s*(?P<second_arg>[^,]+)'
        elif command.group('first_arg') == 'forecast':
            com_pattern: str = r'(?P<com_type>\/\w+)\s+(?P<first_arg>\w+)\,\s*(?P<second_arg>[^,]+)' \
                               r'\,\s*(?P<third_arg>\w+)'
        command: re.match = re.search(com_pattern, msg_text)
        if command:
            com_type: str = command.group('com_type')
            first_arg: str = command.group('first_arg')
            second_arg: str = command.group('second_arg')
            third_arg: str = ''
            if first_arg == 'forecast':
                third_arg: str = command.group('third_arg')
            log.logger.debug(f'User {self.resp_msg.from_user.username}, '
                             f'command {com_type}, {first_arg}, {second_arg}, {third_arg}')
            return {'com_type': com_type, 'first_arg': first_arg, 'second_arg': second_arg, 'third_arg': third_arg}
        else:
            return None

    def transform_com_word_def(self) -> str:
        msg_text: str = self.resp_msg.text
        command_pattern: str = r'(?P<com_type>\/\w+)\s+(?P<first_arg>\w+)'
        en_word: str = re.search(command_pattern, msg_text).group('first_arg')
        return en_word
