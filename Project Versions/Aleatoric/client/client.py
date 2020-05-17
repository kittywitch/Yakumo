from twisted.internet import endpoints, defer, task, reactor
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
import logging, time, hashlib, json, os, uuid, re, inspect, uuid, wx, threading

class AleatoricClient(LineReceiver):
    def connectionMade(self):
        self.pipein, self.pipeout = os.pipe()

    def lineReceived(self, line):
        os.write(pipeout, line)

class AleatoricClientFactory(ReconnectingClientFactory):
    protocol = AleatoricClient

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class AleatoricFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500,-1))
        self.control = wx.TextCtrl(self, size=(500,300), style=wx.TE_READONLY)
        self.textin = wx.TextCtrl(self, size=(500,-1), style=wx.TE_LEFT)
        self.CreateStatusBar()

        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.vbox = wx.GridBagSizer(2, 1)
        self.vbox.Add(self.control, pos=(0,0), flag=wx.EXPAND)
        self.vbox.Add(self.textin, pos=(1,0), flag=wx.BOTTOM)
        self.vbox.Fit(self)

        self.SetSizer(self.vbox)
#        self.SetAutoLayout(1)
        self.Show(True)
    
    def OnAbout(self, e):
        dialog = wx.MessageDialog(self, "A chat application written in Python using the Twisted networking library and wxWidgets.", "Aleatoric v0.0.1", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()
    
    def OnExit(self, e):
        os._exit(1)
        self.Close(True)

def twisted_subsystem():
    factory = AleatoricClientFactory()
    reactor.connectTCP("localhost", 8007, factory)
    reactor.run(installSignalHandlers=False)

def main():
    twisted_thread = threading.Thread(target=twisted_subsystem)
    twisted_thread.start()
    app = wx.App(False)
    global frame
    frame = AleatoricFrame(None, "Aleatoric v0.0.1")
    app.MainLoop()

if __name__ == '__main__':
	main()