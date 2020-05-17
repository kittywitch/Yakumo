import wx, os, json, re, uuid
from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic


class ChatFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Aleatoric")
        self.protocol = None  # twisted Protocol
        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(300, 25))

        sizer.Add(self.text, 5, wx.EXPAND)
        sizer.Add(self.ctrl, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.ctrl.Bind(wx.EVT_TEXT_ENTER, self.send)

    def send(self, evt):
        self.details = self.protocol.factory.details
        commandFormat = re.compile("\/\S+")
        if commandFormat.match(self.ctrl.GetValue()):
            userCheck = re.compile("\/users")
            if userCheck.match(self.ctrl.GetValue()):
                msg = json.dumps({
                    "action":"listUsers"
                })
                self.protocol.sendLine(msg.encode("utf-8"))
            nickCheck = re.compile("\/id\_setup\s([^\/]+)\/([^\/]+)\/([^\/]+)")
            if nickCheck.match(self.ctrl.GetValue()):
                matches = re.search(nickCheck, self.ctrl.GetValue())
                id = str(uuid.uuid1())
                nick = matches[1]
                user = matches[2]
                real = matches[3]
                msg = json.dumps({
                    "action":"setupNick",
                    "id":id,
                    "username":user,
                    "nickname":nick,
                    "realname":real
                })
                self.details["id"] = id
                self.details["username"] = user
                self.details["nickname"] = nick
                self.details["realname"] = real
                print(msg)
                self.protocol.sendLine(msg.encode("utf-8"))
        else:
            self.protocol.sendLine(json.dumps({"action":"userMessage", "message":self.ctrl.GetValue()}).encode("utf-8"))
        self.ctrl.SetValue("")
    
    def OnAbout(self, e):
        dialog = wx.MessageDialog(self, "A chat application written in Python using the Twisted networking library and wxWidgets.", "Aleatoric v0.0.1", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()
    
    def OnExit(self, e):
        os._exit(1)
        self.Close(True)



class AleatoricCProtocol(basic.LineReceiver):
    def __init__(self):
        self.output = None

    def dataReceived(self, line):
        data = json.loads(line)
        print(f"data in: {data}")
        gui = self.factory.gui
        proc = ""
        try:
            if data["action"] == "connectionReceived":
                proc = "Connection to server successful.\n"
                self.sendLine(json.dumps({
                    "action":"acknowledgeSuccess"
                }).encode("utf-8"))
            if data["action"] == "noAckDeny":
                proc = "Connection to server failed.\n"
            if data["action"] == "nickSet":
                proc = "Successfully set nickname.\n"
            if data["action"] == "userInMessage":
                proc = f"{data['nickname']}: {data['message']}\n"
            if data["action"] == "userList":
                proc = "User List:\n"
                for user in data["users"]:
                    proc += f'{user["username"]} - {user["nickname"]} - {user["realname"]}\n'
        except:
            pass
        gui.protocol = self    
        if gui:
            val = gui.text.GetValue()
            gui.text.SetValue(val + proc)
            gui.text.SetInsertionPointEnd()

    def connectionMade(self):
        #self.output = self.factory.gui.text  # redirect Twisted's output
        pass


class AleatoricCFactory(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = AleatoricCProtocol
        self.details = {}

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()


if __name__ == '__main__':
    app = wx.App(False)
    frame = ChatFrame()
    frame.Show()
    reactor.registerWxApp(app)
    reactor.connectSSL("localhost", 8007, AleatoricCFactory(frame), ssl.CertificateOptions(verify=False))
    reactor.run()