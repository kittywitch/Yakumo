import wx, os, json, hashlib

import chen.frames.register

class LoginFrame(wx.Frame):
    def __init__(self, title, server, parent=None):
        wx.Frame.__init__(self, parent=None, title="Login")

        panel = wx.Panel(self, -1, wx.DefaultPosition,wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL)

        self.server = server
        window_rows = wx.BoxSizer(wx.VERTICAL)

        username_row = wx.BoxSizer(wx.HORIZONTAL)
        password_row = wx.BoxSizer(wx.HORIZONTAL)
        remember_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row = wx.BoxSizer(wx.HORIZONTAL)

        self.username = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(150, 25))
        username_label = wx.StaticText(panel, label='Username')
        username_row.Add(username_label, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        username_row.Add(self.username, 3, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 

        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(150, 25))
        password_label = wx.StaticText(panel, label='Password')
        password_row.Add(password_label, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        password_row.Add(self.password, 3, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 


        login_button = wx.Button(panel, 1, "Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)  
        button_row.Add(login_button, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        register_button = wx.Button(panel, 1, "Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        button_row.Add(register_button, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 

        window_rows.Add(username_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(password_row, 0, wx.EXPAND|wx.ALL)
        window_rows.Add(button_row, 0, wx.EXPAND|wx.ALL)

        panel.SetSizer(window_rows)
        self.Centre() 
        self.Show() 
        self.Fit()  

    def on_login(self, e):
        m = hashlib.sha256()
        m.update(self.password.GetValue().encode("utf-8"))
        self.server.sendLine(json.dumps({
            "action":"auth",
            "username":self.username.GetValue(),
            "hash":m.hexdigest()
        }).encode("utf-8"))
        self.Close()        

    def on_register(self, e):
        regWin = chen.frames.register.RegisterFrame("Register", self, parent=self)
        regWin.Show()

