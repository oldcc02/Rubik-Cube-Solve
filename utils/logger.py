import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s-%(levelname)s-%(name)s:  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def new_logger(file_path):
    logger_name = file_path.split("/")[-1]
    return logging.getLogger(logger_name)
