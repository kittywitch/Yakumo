"""Config in code.
"""

import os
import json
import logging


def config_setup(main_path):
    """Sets up configuration for the chat server application. Configuration is done inside the Python file, so I can comment the config itself without further dependencies for things like YAML.
    """
    # import user data
    with open(os.path.join(main_path, "./data/user.json")) as jf:
        users = json.load(jf)

    # import channel data
    with open(os.path.join(main_path, "./data/channel.json")) as jf:
        channels = json.load(jf)

    # import role data
    with open(os.path.join(main_path, "./data/role.json")) as jf:
        roles = json.load(jf)

    config = {
        "connection": {
            # port the server binds on
            "port": 4242,
            # ssl settings
            "ssl": {
                # toggles SSL, it's inadvisable to turn it off
                "toggle": True,
                # SSL keys location
                "directory": "./data/keys",
                # filename of SSL key
                "filename": "server.pem"
            }
        },
        "authentication": {
            # time in seconds before a user is dropped for not logging in or registering an account
            "timeout": 60
        },
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
        "modules": {
            # defines modules directory location
            "directory": "./modules",
            # pushover specific configuration
            "pushover": {
                # enable pushover support
                "toggle": True,
                # get details from pushover
                "token": "a7q4soxthj1ruji13vfo5wej3oe1n8",
                "user": "u9dy5r6f1jdg8wujbtae69yfyxwpu9"
            }
        }
    }
    return config, users, channels, roles
