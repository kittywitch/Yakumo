from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic
import time, socket, http.client, urllib, json, os

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

def t():
    return "["+ time.strftime("%H:%M:%S") +"] "

def ssend(server, data):
    print(f"sending out: {data}")
    server.sendLine(data.encode("utf-8"))

class AleatoricSProtocol(basic.LineReceiver):
    name = "Unnamed"

    def connectionMade(self):
        ssend(self, json.dumps(
            {
                "action":"connectionReceived"
            }
        ))
        self.count = 0
        self.firstmsg = True
        print(f"Connection from: {self.transport.getPeer().host}")

    def connectionLost(self, reason):
        ssend(self, json.dumps({
            "action":"connectionDropped",
            "user":self.name
        }))
        id = self.factory.clients[self]
        del(self.factory.users[id])
        del(self.factory.clients[self])

    def lineReceived(self, line):
        data = json.loads(line)
        print(f"data in: {data}")
        if data["action"] == "acknowledgeSuccess" and self.firstmsg == True:
            self.factory.clients[self] = ""
            self.firstmsg = False
        elif self.firstmsg == True and data["action"] != "acknowledgeSuccess":
            ssend(self, json.dumps({
                "action":"noAckDeny"
            }))
            self.transport.loseConnection()
        if data["action"] == "setupNick":
            self.factory.users[data["id"]] = {
                "username":data["username"],
                "nickname":data["nickname"],
                "realname":data["realname"]
            }
            self.factory.clients[self] = data["id"]
            self.name = data["id"]
            ssend(self, json.dumps({
                "action":"nickSet"
            }))
        if data["action"] == "listUsers":
            users = []
            for user, keys in self.factory.users.items():
                users.append(keys)
            msg = json.dumps({
                "action":"userList",
                "users":users
            })
            ssend(self, msg)
        if data["action"] == "userMessage":
            for client in self.factory.clients:
                client.sendLine(json.dumps({
                    "action":"userInMessage",
                    "message":data["message"],
                    "nickname":self.factory.users[self.name]["nickname"]
                }).encode("utf-8"))


class AleatoricSFactory(protocol.ServerFactory):
    protocol  = AleatoricSProtocol
    clients = {}
    users = {}

if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "keys/server.pem")) as f:
        certData = f.read()
    certificate = ssl.PrivateCertificate.loadPEM(certData).options()
    push_notify(f"Aleatoric - Running on {socket.gethostname()}")
    reactor.listenSSL(8007, AleatoricSFactory(), certificate)
    reactor.run()