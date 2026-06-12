import json
import logging.handlers


class Utils:

    @staticmethod
    def read_json(settings_file, logger):
        logger.debug('Running function read_json')
        try:
            with open(settings_file, "r") as json_file:
                json_data = json.load(json_file)
                return json_data
        except FileNotFoundError:
            logger.error('Credentials not imported: file {} not found.'.format(settings_file))
            exit(1)
        except json.JSONDecodeError:
            logger.error('Credentials not imported: file {} not valid JSON.'.format(settings_file))
            exit(1)

    @staticmethod
    def set_up_logging(logfile, loghistoryfile, level, mode='w'):
        logger = Utils.set_up_single_logging(logfile, level, mode=mode)

        history_log_handler = logging.handlers.RotatingFileHandler(loghistoryfile, maxBytes=10000000, backupCount=5)
        history_log_handler.setFormatter(Utils.get_formatter())
        logger.addHandler(history_log_handler)

        return logger

    @staticmethod
    def set_up_single_logging(logfile, level, mode='w'):
        logger = logging.getLogger('logger')
        logger.setLevel(level)

        current_log_handler = logging.FileHandler(filename=logfile, mode=mode)
        current_log_handler.setFormatter(Utils.get_formatter())
        logger.addHandler(current_log_handler)
        return logger

    @staticmethod
    def get_handler(logfile, mode='w'):
        current_log_handler = logging.FileHandler(filename=logfile, mode=mode)
        current_log_handler.setFormatter(Utils.get_formatter())
        return current_log_handler

    @staticmethod
    def get_formatter():
        fmt = r'%(asctime)s %(levelname)s: %(message)s'
        dfmt = r'%Y-%m-%d %H:%M:%S'
        return logging.Formatter(fmt, datefmt=dfmt)
