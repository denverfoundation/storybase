import logging


class ExceptionHandler(logging.Handler):
    def emit(self, record):
        raise Exception(record.getMessage())
