"""Module loader framework.
"""

import logging
import os
import inspect
import imp
import re

global actions

# actions are a dictionary mapping action names to function responses
actions = {}


def dir_load(main_path, path):
    """Load every .py file in a provided directory.
    """
    # a set is used so that the results can be sorted at the end
    result = set()
    # it lists through every item in the directory listing
    path = os.path.join(main_path, path)
    for entry in os.listdir(path):
        if os.path.isfile(os.path.join(path, entry)):
            # if it is a file, its filename is checked against a regex to see if it is a python file
            matches = re.search("(.+\.py)$", entry)
            # if it is a python file, add it to the set of results
            if matches:
                result.add(matches.group(0))
    logging.info(f"Loaded {len(result)} files: {', '.join(result)}.")
    # sort the remaining results, iterate through loading them
    for filename in sorted(result):
        module_name, ext = os.path.splitext(filename)
        fp, path_name, description = imp.find_module(module_name, [path, ])
        module = imp.load_module(module_name, fp, path_name, description)


def add_act(name):
    """Adds the function decorated to the actions function dictionary.
    """
    frame = inspect.stack()[1]
    filename = os.path.relpath(frame[0].f_code.co_filename, global_main_path)

    def wrapper(function):
        actions[name] = function
        logging.info(
            f"Loaded function \"{function}\" as \"{name}\" from \"{filename}\".")
        return function
    return wrapper


def module_setup(main_path, config):
    """Sets up module loading for the chat server application.
    """
    # use this to work around transferring the main path to modules
    # load the modules from the directory in the config
    global global_main_path
    global_main_path = main_path
    dir_load(main_path, config["modules"]["directory"])
    # no way to reliably return the actions list, so don't attempt to


def sanitize_user(user):
    """Removes the channels and password hash from the user object provided.

    In: {
        "uid":"069fd90d-3f9d-44b8-b3ed-50d0fff0d4c5",
        "username":"kat",
        "full_name":"kat witch",
        "email":"kat@kittywit.ch",
        "hash":"28f55587b1e42cf144c15b9c3f39cf5e04e20fb879785225afd62e4dfa951f44",
        "channels":[
            "#lobby",
            "#test"
        ],
        "avatarURL":""
    }

    Out: {
        "uid":"069fd90d-3f9d-44b8-b3ed-50d0fff0d4c5",
        "full_name":"kat witch",
        "username":"kat",
        "email":"kat@kittywit.ch",
        "avatarURL":""
    }
    """
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
        "uid": user["uid"],
        "avatarURL": user["avatarURL"]
    }
