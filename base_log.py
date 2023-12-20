import logging


class LoggerHand:
    def __init__(self, log_name: str, file_name: str):

        # create logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        # create console handler with debug level
        self.con_hand = logging.StreamHandler()
        self.con_hand.setLevel(logging.DEBUG)

        # create file handler with debug level
        self.file_hand = logging.FileHandler(file_name)
        self.file_hand.setLevel(logging.DEBUG)

        # create formatter
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.con_hand.setFormatter(self.formatter)
        self.logger.addHandler(self.con_hand)

        self.file_hand.setFormatter(self.formatter)
        self.logger.addHandler(self.file_hand)
