from twisted.internet import protocol
from twisted.protocols import basic
import json, logging

class RanSProtocol(basic.LineReceiver):
    def __init__(self):
        self.authenticated = False

    def handle_message(self, message):
        if message["action"] in self.factory.actions.keys():
            logging.info(f"Action {message['action']} triggered.")
            self.factory.actions[message["action"]](message, self)
        else:
            logging.warning(f"Action {message['action']} not found.")

    def p_send(self, action, content=None):
        if content:
            self.sendLine(json.dumps({
                "action":action,
                "content":content
            }).encode("utf-8"))
        else:
            self.sendLine(json.dumps({
                "action":action
            }).encode("utf-8"))

    def connectionMade(self):
        self.ip = self.transport.getPeer().host
        # Request authentication details from the client.
        self.p_send("auth_req")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        logging.info(f"Lost connection from {self.ip}.")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        #try:
        line = line.decode("utf-8")
        logging.debug(f"Client {self.ip} sent: \"{line}\"")
        message = json.loads(line)
        if "action" in message:
            if self.authenticated:
                self.handle_message(message)
            else:
                if message["action"] == "auth":
                    self.handle_message(message)
                else:
                    reason = "does not comply with the Yakumo protocol requirements and has sent a message which does not adhere to the specification."
                    logging.error(f"Client {self.ip} {reason}")
                    self.p_send("auth_fail", f"Your client {reason}")
                    self.transport.loseConnection()
        else:
            reason = "does not comply with the Yakumo protocol requirements and has sent a message which does not adhere to the specification."
            logging.error(f"Client {self.ip} {reason}")
            self.p_send("auth_fail", f"Your client {reason}")
            self.transport.loseConnection()
#        except:
#            reason = "does not comply with the Yakumo protocol requirements and has sent a malformed message."
#            logging.error(f"Client {self.ip} {reason}")
#            self.p_send("auth_fail", f"Your client {reason}")
#            self.transport.loseConnection()

class RanSFactory(protocol.ServerFactory):    
    def __init__(self, actions):
        self.protocol  = RanSProtocol
        self.actions = actions
        self.clients = []