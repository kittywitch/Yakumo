"""Config in code.
"""

import os
import json
import logging


def config_setup(main_path):
    """Sets up configuration for the chat client application. Configuration is done inside the Python file, so I can comment the config itself without further dependencies for things like YAML.
    """

    config = {
        "upload_url": "http://localhost",
        "address": "localhost",
        "port": 4242,
        "logging": {
            # this turns logging on and off, True = on.
            "toggle": True,
            # defining separately whatevel is used for the logger on both file and console, and their formats
            "file": {
                # level of severity for output
                "level": "debug",
                # folder location from base_path to store log
                "location": "./data",
                # filename to store log
                "filename": "server.log",
                # filemode for writing
                "mode": "w",
                # format of the log output
                "fmt": "[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s",
                # format used for time
                "time_format": "%Y-%m-%d %H:%M:%S"
            },
            "console": {
                # level of severity for output
                "level": "debug",
                # format of the log output
                "fmt": "[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s"
            },
        },
    }
    return config
