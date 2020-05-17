"""The file that defines the protocol.
"""

from twisted.internet import protocol
from twisted.protocols import basic
from twisted.internet import reactor

import json
import logging


class RanSProtocol(basic.LineReceiver):
    def __init__(self):
        self.authenticated = False
        self.user = None

    def send_wrap(self, dict):
        message = json.dumps(dict).encode("utf-8")
        if self.authenticated:
            logging.debug(f"{self.ip} / {self.user['username']} -> {message}")
        else:
            logging.debug(f"{self.ip} / unauthenticated -> {message}")
        self.sendLine(message)

    def authentication_check(self):
        if not self.authenticated:
            self.drop_user(
                f"User from \"{self.ip}\" hasn't authenticated after {self.factory.config['authentication']['timeout']}s.")

    def handle_message(self, message):
        if message["action"] in self.factory.actions.keys():
            logging.info(f"Action {message['action']} triggered.")
            self.factory.actions[message["action"]](message, self)

    def drop_user(self, reason):
        # simple way to generate these responses to a user and to drop them from the server
        self.send_wrap({
            "action": "connection_closed",
            "type": "error",
            "reason": reason
        })
        if self.authenticated:
            logging.warning(f"{self.ip} / {self.user['username']} -! {reason}")
        else:
            logging.warning(f"{self.ip} -! {reason}")
        self.transport.loseConnection()

    # base twisted functions

    def connectionMade(self):
        # get the clients IP address
        self.ip = self.transport.getPeer().host
        # check authentication status after duration specified in config, time user out if period elapses if user is still unauthenticated after 60s
        reactor.callLater(
            self.factory.config["authentication"]["timeout"], self.authentication_check)
        self.send_wrap(
            {"action": "auth_req"}
        )

    def connectionLost(self, reason):
        if self.authenticated:
            try:
                self.factory.clients.pop(self)
            except KeyError:
                pass

    def lineReceived(self, line):
        # decode the line from the bytes object in utf-8
        line = line.decode("utf-8")
        if self.authenticated:
            logging.debug(f"{self.ip} / {self.user['username']} <- {line}")
        else:
            logging.debug(f"{self.ip} / unauthenticated <- {line}")
        # check if it is valid json, if it isn't, exception will occur
        try:
            ingest = json.loads(line)
        except ValueError as e:
            self.drop_user(f"Malformed JSON sent by \"{self.ip}\".")
        else:
            message = ingest
            if "action" in message:
                if self.authenticated:
                    self.handle_message(message)
                else:
                    # unauthenticated users can only register or authenticate, but those messages are handled properly
                    if message["action"] == "auth" or message["response"] == "register":
                        self.handle_message(message)
                    else:
                        # sending anything but that is not allowed within the protocol
                        self.drop_user(
                            "\"{self.ip}\" attempted to act without registering or authenticating.")


class RanSFactory(protocol.ServerFactory):
    def __init__(self, main_path, actions, config, users, channels, roles):
        self.main_path = main_path
        self.actions = actions
        self.config = config
        self.users = users
        self.protocol = RanSProtocol
        self.clients = {}
        self.channels = channels
        self.roles = roles
