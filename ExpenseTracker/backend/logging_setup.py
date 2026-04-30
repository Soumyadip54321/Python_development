import logging

def setup_logger(logger_name, filename, level = logging.DEBUG):
    # create custom Logger with a name
    logger = logging.getLogger(logger_name)

    # configure custom logger
    logger.setLevel(level)
    file_handler = logging.FileHandler(filename)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return logger