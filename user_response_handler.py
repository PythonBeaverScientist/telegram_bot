from telegram import Update
from base_log import LoggerHand
import re

log = LoggerHand(__name__, f"loggers/{__name__}.log")
re.IGNORECASE = True


class UserResponseHandler:
    def __init__(self, resp_msg: Update.message):
        self.resp_msg: Update.message = resp_msg

    def transform_msg_com(self):
        msg_text: str = self.resp_msg.text
        com_pattern: str = r'(?P<com_type>\/\w+)\s+(?P<first_arg>\w+)\,\s*(?P<second_arg>[^,]+)'
        command: re.match = re.search(com_pattern, msg_text)
        if command:
            com_type: str = command.group('com_type')
            first_arg: str = command.group('first_arg')
            second_arg: str = command.group('second_arg')
            log.logger.debug(f'User {self.resp_msg.from_user.username}, '
                             f'command {com_type}, {first_arg}, {second_arg}')
            return {'com_type': com_type, 'first_arg': first_arg, 'second_arg': second_arg}
        else:
            return None
