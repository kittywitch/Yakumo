import wx, os, json, re, uuid, wx.richtext, requests, datetime, io, hashlib, webbrowser, pyperclip
from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic

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
        self.previously_selected = 0
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
        chat_mode_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Mode", " Set the mode for the channel.")
        self.Bind(wx.EVT_MENU, self.on_chat_mode, chat_mode_action)
        chat_topic_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Topic", " Set the topic for the channel.")
        self.Bind(wx.EVT_MENU, self.on_chat_topic, chat_topic_action)

        # Menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu,"&File")
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
        commandFormat = re.compile("\/\S+")
        if commandFormat.match(self.user_input.GetValue()):
            userCheck = re.compile("\/users")
            if userCheck.match(self.user_input.GetValue()):
                msg = json.dumps({
                    "action":"listUsers"
                })
                self.protocol.sendLine(msg.encode("utf-8"))
            nickCheck = re.compile("\/id\_setup\s([^\/]+)\/([^\/]+)\/([^\/]+)")
            if nickCheck.match(self.user_input.GetValue()):
                matches = re.search(nickCheck, self.user_input.GetValue())
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
            selected_index = self.channel_list.GetSelection()
            if selected_index != -1:
                self.protocol.sendLine(json.dumps({
                    "action":"user_message", 
                    "channel":self.channel_list.GetString(selected_index), 
                    "timestamp":int(datetime.datetime.utcnow().timestamp()), 
                    "message":self.user_input.GetValue()
                }).encode("utf-8"))
            else:
                dialog = wx.MessageDialog(self, "No channel is selected.", "Warning", wx.ICON_WARNING)
                dialog.ShowModal()
                dialog.Destroy()

        self.user_input.SetValue("")
    
    def on_channel_select(self, e):
        selected_index = self.channel_list.GetSelection()
        previous_channel = self.channel_list.GetString(self.previously_selected)
        current_channel = self.channel_list.GetString(selected_index)
        self.output.Clear()
        for message in self.database[current_channel]:
            self.output.WriteText(f"{message.username}: {message.message}")
            self.output.Newline()
            self.output.SetInsertionPointEnd()
            
        #self.previously_selected = selected_index
    
    def on_upload_list(self, e):
        res = requests.post('http://localhost/api/uploads', json={
            "token":self.token
        })
        if res.ok:
            result = res.json()
        uploadWin = UploadsFrame("Login", self, res.json()["uploads"])
        uploadWin.Show()

    def on_chat_mode(self, e):
        pass

    def on_chat_topic(self, e):
        pass

    def on_about(self, e):
        dialog = wx.MessageDialog(self, "A chat application written in Python using the Twisted networking library and wxWidgets.", "Chen v0.0.1", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def on_open(self, e):
        selected_index = self.channel_list.GetSelection()
        if selected_index != -1:
            # otherwise ask the user what new file to open
            with wx.FileDialog(self, "Open file", wildcard="*",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     # the user changed their mind

                # Proceed loading the file chosen by the user
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
        os._exit(1)
        self.Close(True)

class UploadsFrame(wx.Frame):
    def __init__(self, title, server, upload_list, parent=None):
        wx.Frame.__init__(self, parent=None, title="Uploads")
        self.server = server
        self.index = 0
        window_rows = wx.BoxSizer(wx.VERTICAL)
        
        content_row = wx.BoxSizer(wx.HORIZONTAL)
        self.upload_list = wx.ListCtrl(self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_VRULES)
        self.upload_list.AppendColumn("Date", width=wx.LIST_AUTOSIZE)
        self.upload_list.AppendColumn("URL", width=wx.LIST_AUTOSIZE_USEHEADER)
        content_row.Add(self.upload_list, flag=wx.ALL, border=5, proportion=1)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        insert_button = wx.Button(self, 1, "Insert")
        insert_button.Bind(wx.EVT_BUTTON, self.on_insert)
        button_row.Add(insert_button, flag=wx.LEFT, border=2, proportion=1)
        copy_button = wx.Button(self, 1, "Copy")
        copy_button.Bind(wx.EVT_BUTTON, self.on_copy)
        button_row.Add(copy_button, flag=wx.CENTRE, border=2, proportion=1)
        open_button = wx.Button(self, 1, "Open")
        open_button.Bind(wx.EVT_BUTTON, self.on_open)
        button_row.Add(open_button, flag=wx.RIGHT, border=2, proportion=1)

        window_rows.Add(content_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(button_row, 0, wx.EXPAND|wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

        for upload in upload_list:
            date = datetime.datetime.fromtimestamp(upload["time"]).strftime("%F %T %Z")
            self.upload_list.InsertItem(self.index, date)
            self.upload_list.SetItem(self.index, 1, upload["url"])
            self.index += 1

    def on_insert(self, e):
        urls = []
        prev = -1
        while True:
            current = self.upload_list.GetNextSelected(prev)
            url = f"http://localhost{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
            urls.append(url)
            print(current)
            if prev == -1:
                break
            else:
                prev = current
        self.server.user_input.AppendText(" ".join(urls))

    def on_copy(self, e):
        urls = []
        prev = -1
        while True:
            current = self.upload_list.GetNextSelected(prev)
            url = f"http://localhost{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
            urls.append(url)
            print(current)
            if prev == -1:
                break
            else:
                prev = current
        pyperclip.copy(" ".join(urls))

    def on_open(self, e):
        prev = -1
        while True:
            current = self.upload_list.GetNextSelected(prev)
            url = f"http://localhost{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
            webbrowser.open_new_tab(url)
            if prev == -1:
                break
            else:
                prev = current

class ConnectFrame(wx.Frame):
    def __init__(self, title, server, parent=None):
        wx.Frame.__init__(self, parent=None, title="Login")
        self.server = server
        window_rows = wx.BoxSizer(wx.VERTICAL)

        username_row = wx.BoxSizer(wx.HORIZONTAL)
        password_row = wx.BoxSizer(wx.HORIZONTAL)
        remember_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row = wx.BoxSizer(wx.HORIZONTAL)

        self.username = wx.TextCtrl(self, style=wx.TE_LEFT, size=(150, 25))
        username_label = wx.StaticText(self, label='Username')
        username_row.Add(username_label, flag=wx.ALL, border=5)
        username_row.Add(self.username, flag=wx.ALL, border=5, proportion=1)

        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(150, 25))
        password_label = wx.StaticText(self, label='Password')
        password_row.Add(password_label, flag=wx.ALL, border=5)
        password_row.Add(self.password, flag=wx.ALL, border=5, proportion=1)

        self.remember_box = wx.CheckBox(self, style=wx.CHK_2STATE, label="Remember this login.")
        remember_row.Add(self.remember_box, flag=wx.ALL, border=10)

        login_button = wx.Button(self, 1, "Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)  
        button_row.Add(login_button, flag=wx.LEFT, border=2, proportion=1)
        register_button = wx.Button(self, 1, "Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        button_row.Add(register_button, flag=wx.CENTRE, border=2, proportion=1)
        clear_token_button = wx.Button(self, 1, "Clear Token")
        clear_token_button.Bind(wx.EVT_BUTTON, self.on_clear_token)
        button_row.Add(clear_token_button, flag=wx.RIGHT, border=2, proportion=1)
        
        if self.server.factory.gui.token is not False:
            self.username.Enable(False)
            self.remember_box.Enable(False)
            self.password.Enable(False)

        window_rows.Add(username_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(password_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(remember_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(button_row, 0, wx.EXPAND|wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

    def on_login(self, e):
        self.server.remember = self.remember_box.GetValue()
        if self.server.factory.gui.token is not False:
            self.server.sendLine(json.dumps({
                "action":"auth",
                "token":self.server.factory.gui.token
            }).encode("utf-8"))
        else:
            m = hashlib.sha256()
            m.update(self.password.GetValue().encode("utf-8"))
            self.server.sendLine(json.dumps({
                "action":"auth",
                "username":self.username.GetValue(),
                "password":m.hexdigest()
            }).encode("utf-8"))
        self.Close()

    def on_clear_token(self, e):
        if os.path.exists("./data/token.txt"):
            question = wx.MessageDialog(self, "Are you sure you want to clear the current token?", "Token Status", wx.YES_NO|wx.ICON_QUESTION)
            if question.ShowModal() == wx.ID_YES:
                os.remove("./data/token.txt")
                self.server.factory.gui.token = False
                dialog = wx.MessageDialog(self, "Current token has been cleared.", "Token Status", wx.ICON_INFORMATION)
                self.username.Enable(True)
                self.password.Enable(True)
                self.remember_box.Enable(True)
                dialog.ShowModal()
                dialog.Destroy()
                question.Destroy()
            else:
                question.Destroy()
        else:
            dialog = wx.MessageDialog(self, "No token is currently enrolled.", "Token Status", wx.ICON_WARNING)
            dialog.ShowModal()
            dialog.Destroy()
        

    def on_register(self, e):
        pass

        
class ChenCProtocol(basic.LineReceiver):
    def __init__(self):
        self.output = None
        self.remember = False
        self.user = None

    def dataReceived(self, line):
        data = json.loads(line)
        print(f"data in: {data}")
        gui = self.factory.gui
        lines = []
        #try:
        if data["action"] == "auth_req":
            connWin = ConnectFrame("Login", self)
            connWin.Show()
        if data["action"] == "auth_success":
            user = json.loads(data['user'])
            gui.channel_list.InsertItems(user["channels"], 0)
            print(data['token'])
            gui.token = data['token']
            if not os.path.exists("./data/token.txt") and self.remember:
                save_token(data['token'])
            for channel in user["channels"]:
                gui.database[channel] = []
            lines.append(f"Logged in as {user['username']} - {user['realname']}.")
            lines.append("\n")
            lines.append("Please select a channel to begin.")
        if data["action"] == "user_message_out":
            gui.database[data["channel"]].append(ChatMessage(data["channel"], gui.message_id, data["username"], data["message"], data["timestamp"]))
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