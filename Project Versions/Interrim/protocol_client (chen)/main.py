import wx, os, json, re, uuid, wx.richtext, requests, datetime, io, hashlib, webbrowser, pyperclip
from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic

import frames.upload, frames.connect, frames.register

def save_token(token):
    if not os.path.exists("./data/token.txt"):
        with open("data/token.txt", "w+") as token_file:
            token_file.write(token)

def load_token():
    if os.path.exists("./data/token.txt"):
        with open("data/token.txt", "r") as token_file:
            return token_file.read()
    else:
        return False

class ChatMessage():
    def __init__(self, channel, mid, username, message, timestamp):
        self.id = mid
        self.username = username
        self.channel = channel
        self.message = message
        self.timestamp = timestamp

class ChatFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Chen")
        self.protocol = None
        self.database = {}
        self.token = load_token()
        self.message_id = 0

        # File Menu
        file_menu = wx.Menu()
        about_menu_action = file_menu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, about_menu_action)
        exit_menu_action = file_menu.Append(wx.ID_EXIT,"&Exit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_action)

        # User Menu
        user_menu = wx.Menu()
        uploads_list_action = user_menu.Append(wx.ID_ANY, "&Uploads", " See your previous uploads.")
        self.Bind(wx.EVT_MENU, self.on_upload_list, uploads_list_action)

        # Chat Menu
        chat_menu = wx.Menu()
        #chat_mode_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Mode", " Set the mode for the channel.")
        #self.Bind(wx.EVT_MENU, self.on_chat_mode, chat_mode_action)
        #chat_topic_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Topic", " Set the topic for the channel.")
        #self.Bind(wx.EVT_MENU, self.on_chat_topic, chat_topic_action)
        chat_send_sd = chat_menu.Append(wx.ID_ANY, "&Send self-destructing message", " Send self destructing message to the selected channel.")
        self.Bind(wx.EVT_MENU, self.on_send_sd, chat_send_sd)

        # Menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu,"&File")
        menu_bar.Append(chat_menu,"&Chat")
        menu_bar.Append(user_menu,"&User")
        self.SetMenuBar(menu_bar)

        # Input Row
        input_row = wx.BoxSizer(wx.HORIZONTAL)
        self.user_input = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user_input.Bind(wx.EVT_TEXT_ENTER, self.send)
        upload_button = wx.Button(self, -1, "Upload")
        upload_button.Bind(wx.EVT_BUTTON, self.on_open) 
        input_row.Add(self.user_input, 5, wx.EXPAND)
        input_row.Add(upload_button, 1, wx.EXPAND)

        # Output Box
        output_row = wx.BoxSizer(wx.HORIZONTAL)
        self.output = wx.richtext.RichTextCtrl(self, style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY)
        self.channel_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.on_channel_select, self.channel_list) 
        output_row.Add(self.channel_list, 1, wx.EXPAND|wx.ALL)
        output_row.Add(self.output, 4, wx.EXPAND|wx.ALL)

        # Window Rows
        window_rows = wx.BoxSizer(wx.VERTICAL)
        window_rows.Add(output_row, 5, wx.EXPAND|wx.ALL)
        window_rows.Add(input_row, 0, wx.EXPAND|wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

    def send(self, evt):
        self.details = self.protocol.factory.details       
        selected_index = self.channel_list.GetSelection()
        if selected_index != -1:
            self.protocol.sendLine(json.dumps({
                "action":"user_message", 
                "channel":self.channel_list.GetString(selected_index), 
                "timestamp":int(datetime.datetime.utcnow().timestamp()), 
                "message":self.user_input.GetValue()
            }).encode("utf-8"))
            self.user_input.SetValue("")
        else:
            dialog = wx.MessageDialog(self, "No channel is selected.", "Warning", wx.ICON_WARNING)
            dialog.ShowModal()
            dialog.Destroy()
    
    def on_channel_select(self, e):
        selected_index = self.channel_list.GetSelection()
        current_channel = self.channel_list.GetString(selected_index)
        self.output.Clear()
        for message in self.database[current_channel]:
            self.output.WriteText(f"{message.username}: {message.message}")
            self.output.Newline()
            self.output.SetInsertionPointEnd()

    
    def on_upload_list(self, e):
        res = requests.post('http://localhost/api/uploads', json={
            "token":self.token
        })
        if res.ok:
            result = res.json()
        uploadWin = frames.upload.UploadsFrame("Login", self, res.json()["uploads"], parent=self)
        uploadWin.Show()

    def on_send_sd(self, e):
        self.details = self.protocol.factory.details       
        selected_index = self.channel_list.GetSelection()
        dlg = wx.TextEntryDialog(self, 'How long do you want that message to last?','Message duration')
        if dlg.ShowModal() == wx.ID_OK:
            duration = int(dlg.GetValue())
            if selected_index != -1:
                self.protocol.sendLine(json.dumps({
                    "action":"user_message_sd",
                    "duration":duration,
                    "channel":self.channel_list.GetString(selected_index), 
                    "timestamp":int(datetime.datetime.utcnow().timestamp()), 
                    "message":self.user_input.GetValue()
                }).encode("utf-8"))
                self.user_input.SetValue("")
            else:
                dialog = wx.MessageDialog(self, "No channel is selected.", "Warning", wx.ICON_WARNING)
                dialog.ShowModal()
                dialog.Destroy()
    #def on_chat_mode(self, e):
    #    pass

    #def on_chat_topic(self, e):
    #    pass

    def on_about(self, e):
        dialog = wx.MessageDialog(self, "A chat application written in Python using the Twisted networking library and wxWidgets.", "Chen v0.0.1", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def on_open(self, e):
        # a channel must be selected for the user to upload a file for it to be linked into
        selected_index = self.channel_list.GetSelection()
        if selected_index != -1:
            # ask the user for the file to open
            with wx.FileDialog(self, "Upload file", wildcard="*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                # if the user hit the cancel button, we don't want to do anything
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return

                # from the file path, try to upload the file in a multipart request with the token being posted alongside the file itself to flask
                pathname = fileDialog.GetPath()
                try:
                    files = {
                        'token': (None, self.token),
                        'upload_file': (os.path.basename(pathname), open(pathname, 'rb'), 'application/octet-stream')
                    }
                    r = requests.post("http://localhost/api/upload", files=files)
                    print(r)
                    if r.ok:
                        url = f"http://localhost{r.json()['url']}"
                        self.protocol.sendLine(json.dumps({
                            "action":"user_upload", 
                            "channel":self.channel_list.GetString(selected_index), 
                            "timestamp":int(datetime.datetime.utcnow().timestamp()), 
                            "url":url
                        }).encode("utf-8"))
                        self.output.WriteText(f"File uploaded to: {url}")
                        self.output.Newline()
                        self.output.SetInsertionPointEnd()
                        print(r.json())
                except IOError:
                    wx.LogError("Cannot open file '%s'." % newfile)
        else:
            dialog = wx.MessageDialog(self, "No channel is selected.", "Warning", wx.ICON_WARNING)
            dialog.ShowModal()
            dialog.Destroy()

    def on_exit(self, e):
        # when the exit button is hit, you wanna close the program
        os._exit(1)
        self.Close(True)
       
class ChenCProtocol(basic.LineReceiver):
    def __init__(self):
        self.output = None
        self.remember = False
        self.user = None

    def delete_line(self, tupy):
        del self.factory.gui.database[tupy[1]][tupy[0]]
        selected_index = self.factory.gui.channel_list.GetSelection()
        current_channel = self.factory.gui.channel_list.GetString(selected_index)
        self.factory.gui.output.Clear()
        for message in self.factory.gui.database[current_channel]:
            self.factory.gui.output.WriteText(f"{message.username}: {message.message}")
            self.factory.gui.output.Newline()
            self.factory.gui.output.SetInsertionPointEnd()

    def dataReceived(self, line):
        data = json.loads(line)
        print(f"data in: {data}")
        gui = self.factory.gui
        lines = []
        #try:
        if data["action"] == "auth_req":
            connWin = frames.connect.ConnectFrame("Login", self, parent=self)
            connWin.Show()
        if data["action"] == "auth_success":
            user = json.loads(data['user'])
            gui.channel_list.InsertItems(user["channels"], 0)
            print(data['token'])
            gui.token = data['token']
            if not os.path.exists("./data/token.txt") and self.remember:
                save_token(data['token'])
            for channel in user["channels"]:
                self.sendLine(json.dumps({
                    "action":"join_channel",
                    "channel":channel
                }).encode("utf-8"))
                gui.database[channel] = []
            lines.append(f"Logged in as {user['username']} - {user['realname']}.")
            lines.append("\n")
            lines.append("Please select a channel to begin.")
        if data["action"] == "register_success":
            user = json.loads(data['user'])
            gui.channel_list.InsertItems(user["channels"], 0)
            print(data['token'])
            gui.token = data['token']
            if not os.path.exists("./data/token.txt") and self.remember:
                save_token(data['token'])
            for channel in user["channels"]:
                gui.database[channel] = []
            lines.append(f"Registered as {user['username']} - {user['realname']}.")
            lines.append("\n")
            lines.append("Please select a channel to begin.")
        if data["action"] == "user_message_out":
            gui.database[data["channel"]].append(ChatMessage(data["channel"], gui.message_id, data["username"], data["message"], data["timestamp"]))
            gui.message_id = gui.message_id + 1
            lines.append(f"{data['username']}: {data['message']}")
        if data["action"] == "user_message_sd_out":
            gui.database[data["channel"]].append(ChatMessage(data["channel"], gui.message_id, data["username"], data["message"], data["timestamp"]))
            reactor.callLater(int(data["duration"]), self.delete_line, (gui.message_id, data["channel"]))
            gui.message_id = gui.message_id + 1
            lines.append(f"{data['username']}: {data['message']}")
        if data["action"] == "user_upload_out":
            gui.database[data["channel"]].append(ChatMessage(data["channel"], gui.message_id, data["username"], data["url"], data["timestamp"]))
            gui.message_id = gui.message_id + 1
            lines.append(f"User \"{data['username']}\" has uploaded: {data['url']}")
        #except:
            #pass
        gui.protocol = self    
        if gui:
            for output_line in lines:
                if output_line == "\n":
                    gui.output.Newline()    
                else:
                    gui.output.WriteText(output_line)
                    gui.output.Newline()
                    gui.output.SetInsertionPointEnd()

    def connectionMade(self):
        #self.output = self.factory.gui.output  # redirect Twisted's output
        pass


class ChenCFactory(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = ChenCProtocol
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
    reactor.connectSSL("localhost", 4242, ChenCFactory(frame), ssl.CertificateOptions(verify=False))
    reactor.run()