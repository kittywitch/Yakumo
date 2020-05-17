"""Logger setup.
"""

import logging
import coloredlogs
import os


def logging_setup(main_path, config):
    """Sets up logging for the chat server application, firstly to the file "./data/server.log", secondly to the console.
    """
    # pulling details from config
    # check if logging is enabled at all, if it isn't enabled, return
    if not config["logging"]["toggle"]:
        return

    # file mode for the filehandler
    file_mode = config["logging"]["file"]["mode"]
    # severity debug level for the file logger
    file_level = logging.getLevelName(
        config["logging"]["file"]["level"].upper())
    # sets up a logger with a basic config so that logging is initialised with the DEBUG level minimum, filemode to overwrite.
    logging.basicConfig(level=file_level, filemode=file_mode)
    # sets up a custom log format that looks better, gives me more information about what's going on where in the code where i'm producing log messages, in this case for the server.log file created below
    log_formatter = logging.Formatter(
        config["logging"]["file"]["fmt"], config["logging"]["file"]["time_format"])
    # get the default logger
    root_logger = logging.getLogger()
    # remove the default logger handler
    root_logger.handlers = []
    # check for the existence of the "./data/" directory
    if not os.path.isdir(os.path.join(main_path, "./data")):
        # if the "./data" directory does not exist, create it
        os.mkdir(os.path.join(
            main_path, config["logging"]["file"]["location"]))
    # create a new handler which writes to the specified file
    combined_location_and_name = config["logging"]["file"]["location"] + \
        "/" + config["logging"]["file"]["filename"]
    file_handler = logging.FileHandler(
        os.path.join(main_path, "data/server.log"))
    # add the custom file handler to the default logger
    root_logger.addHandler(file_handler)

    # console output format for the logger
    console_format = config["logging"]["console"]["fmt"]
    # severity debug level for the console logger
    console_level = config["logging"]["console"]["level"].upper()
    # attach the logger to the console through coloredLogs with my custom format
    coloredlogs.install(level=console_level, fmt=console_format)
