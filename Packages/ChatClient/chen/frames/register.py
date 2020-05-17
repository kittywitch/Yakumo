import wx, os, json, hashlib

class RegisterFrame(wx.Frame):
    def __init__(self, title, server, parent=None):
        wx.Frame.__init__(self, parent=None, title="Register")
        self.server = server
        window_rows = wx.BoxSizer(wx.VERTICAL)

        username_row = wx.BoxSizer(wx.HORIZONTAL)
        full_name_row = wx.BoxSizer(wx.HORIZONTAL)
        email_row = wx.BoxSizer(wx.HORIZONTAL)
        password_row = wx.BoxSizer(wx.HORIZONTAL)
        remember_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row = wx.BoxSizer(wx.HORIZONTAL)

        self.username = wx.TextCtrl(self, style=wx.TE_LEFT, size=(150, 25))
        username_label = wx.StaticText(self, label='Username')
        username_row.Add(username_label, flag=wx.ALL, border=5)
        username_row.Add(self.username, flag=wx.ALL, border=5, proportion=1)

        self.full_name = wx.TextCtrl(self, style=wx.TE_LEFT, size=(150, 25))
        full_name_label = wx.StaticText(self, label='Display Name')
        full_name_row.Add(full_name_label, flag=wx.ALL, border=5)
        full_name_row.Add(self.full_name, flag=wx.ALL, border=5, proportion=1)

        self.email = wx.TextCtrl(self, style=wx.TE_LEFT, size=(150, 25))
        email_label = wx.StaticText(self, label='Email')
        email_label_row.Add(email_label, flag=wx.ALL, border=5)
        email_label_row.Add(self.email, flag=wx.ALL, border=5, proportion=1)

        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(150, 25))
        password_label = wx.StaticText(self, label='Password')
        password_row.Add(password_label, flag=wx.ALL, border=5)
        password_row.Add(self.password, flag=wx.ALL, border=5, proportion=1)

        register_button = wx.Button(self, 1, "Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        button_row.Add(register_button, flag=wx.CENTRE, border=2, proportion=1)

        window_rows.Add(username_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(full_name_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(email_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(password_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(button_row, 0, wx.EXPAND|wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

    def on_register(self, e):
        m = hashlib.sha256()
        m.update(self.password.GetValue().encode("utf-8"))
        self.server.server.sendLine(json.dumps({
            "action":"register",
            "username":self.username.GetValue(),
            "full_name":self.full_name.GetValue(),
            "email":self.email.GetValue(),
            "hash":m.hexdigest()
        }).encode("utf-8"))
        self.Close()