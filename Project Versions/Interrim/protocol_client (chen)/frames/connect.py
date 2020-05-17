import wx, os, json, hashlib

import frames.register

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
        regWin = frames.register.RegisterFrame("Register", self, parent=self)
        regWin.Show()

