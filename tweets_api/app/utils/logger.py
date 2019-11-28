import logging
from .config import Config


# Class of the logger
class Logger:
    _logger = None

    @staticmethod
    def log(__name__):
        if Logger._logger is None:
            Logger._logger = logging.getLogger(__name__)
            Logger._logger.setLevel(getattr(logging, Config.log_level()))
            # Here we define our formatter
            formatter = logging.Formatter('%(asctime)s [ %(name)s  %(filename)s:%(lineno)s  %(funcName)s() ][ %(levelname)s ]: %(message)s')

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(formatter)
            Logger._logger.addHandler(stream_handler)

        return Logger._logger
