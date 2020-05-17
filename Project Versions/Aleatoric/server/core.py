from twisted.internet import ssl, reactor, endpoints, defer, task
from twisted.protocols.basic import LineReceiver
from twisted.internet import protocol, endpoints, error, reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols import basic
import uuid, json, os, hashlib, time, logging, threading, coloredlogs, http.client, urllib

# pushover
def push_notify(msg):
    client = http.client.HTTPSConnection("api.pushover.net:443")
    client.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a7q4soxthj1ruji13vfo5wej3oe1n8",
        "user": "u9dy5r6f1jdg8wujbtae69yfyxwpu9",
        "message": msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    try:
        response = client.getresponse()
        logging.debug(response.read())
        return response
    except:
        return None

# to be in server.py

def socket_send(server, data):
	server.sendLine(data.encode("utf-8"))

class AleatoricServer(basic.LineReceiver):
    def connectionMade(self):
        self._peer = self.transport.getPeer()
        self._sockaddr = f"{self._peer.host}:{self._peer.port}"
        logging.info(f"A connection has been made from {self._sockaddr}.")
        pass
    def connectionLost(self, reason):
        pass
    def lineReceived(self, line):
        line = line.decode("utf-8")
        if line == "nya":
            print("nya detected, sending mew!")
            socket_send(self, "mew!")
        #try:
        #    message = json.loads(line)
        #except Exception as e:
        #    logging.error(f"Error \"{e}\" with input \"{line}\".")
    
class AleatoricServerFactory(protocol.Factory):
    protocol = AleatoricServer

# actual core

def main():
    threading.current_thread().name = 'AleatoricServer'
    # Sets up a debug level logger that overwrites the file
    logging.basicConfig(level=logging.DEBUG,filemode="w")
    logFormatter = logging.Formatter("[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    # Remove the default logger.
    rootLogger.handlers = []
    # Hook the logger up to the file "server.log"
    fileHandler = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "server.log"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    # Hook the logger up to the console
    coloredlogs.install(level='DEBUG',fmt="[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s")
    push_notify("Aleatoric Server Instance Booted")
    factory = AleatoricServerFactory()
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(AleatoricServerFactory())
    reactor.run()

if __name__ == '__main__':
	main()