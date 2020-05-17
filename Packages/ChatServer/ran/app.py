"""The main file for the chat server project.
"""

from twisted.internet import reactor, ssl
import os
import logging
import sys
import threading
import socket

import ran.logger
import ran.config
import ran.librarian
import ran.reactor
import ran.notification

global base_path


def main():
    print("")
    print("$$$$$$$\\                      ")
    print("$$  __$$\\                     ")
    print("$$ |  $$ | $$$$$$\\  $$$$$$$\\  ")
    print("$$$$$$$  | \\____$$\\ $$  __$$\\")
    print("$$  __$$<  $$$$$$$ |$$ |  $$ |")
    print("$$ |  $$ |$$  __$$ |$$ |  $$ |")
    print("$$ |  $$ |\\$$$$$$$ |$$ |  $$ |")
    print("\\__|  \\__| \\_______|\\__|  \\__|")
    print("")
    print("The chat protocol server of the Yakumo System.")
    print("")
    # provide the directory of the app.py to other modules
    base_path = os.path.dirname(os.path.abspath(__file__))
    # set up config
    cfg, users, channels, roles = ran.config.config_setup(base_path)
    # notify over pushover
    ran.notification.push(
        f"Ran server started {socket.gethostname()}", cfg["modules"]["pushover"])
    # set up logger
    ran.logger.logging_setup(base_path, cfg)
    # log details on loaded data
    logging.info(f"Loaded {len(users)} users.")
    logging.info(f"Loaded {len(channels)} channels.")
    logging.info(f"Loaded {len(roles)} roles.")
    # load modules
    ran.librarian.module_setup(base_path, cfg)
    # make actions a local scope variable
    actions = ran.librarian.actions
    # log details on loaded modules
    logging.info(
        f"Loaded {len(actions)} modules: {', '.join(actions.keys())}.")
    # set up reactor
    ran.reactor.reactor_setup(base_path, actions, cfg, users, channels, roles)


if __name__ == "__main__":
    main()
