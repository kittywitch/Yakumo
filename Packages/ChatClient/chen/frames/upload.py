import wx, wx.richtext, datetime, webbrowser, pyperclip

class UploadsFrame(wx.Frame):
    def __init__(self, title, server, upload_list, parent=None):
        wx.Frame.__init__(self, parent=None, title="Uploads")
        self.server = server
        self.index = 0
        
        # upload list
        self.upload_list = wx.ListCtrl(self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_VRULES)
        self.upload_list.AppendColumn("Date", width=wx.LIST_AUTOSIZE)
        self.upload_list.AppendColumn("URL", width=wx.LIST_AUTOSIZE_USEHEADER)

        # button row
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
        
        window_rows = wx.BoxSizer(wx.VERTICAL)
        window_rows.Add(self.upload_list, 4, wx.GROW)
        window_rows.Add(button_row, 0, wx.EXPAND|wx.ALL)

        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

        # for each upload, get the time and insert it into the upload list
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
            url = f"{self.server.protocol.factory.cfg['upload_url']}{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
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
            url = f"{self.server.protocol.factory.cfg['upload_url']}{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
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
            url = f"{self.server.protocol.factory.cfg['upload_url']}{self.upload_list.GetItem(itemIdx=current, col=1).GetText()}"
            webbrowser.open_new_tab(url)
            if prev == -1:
                break
            else:
                prev = current
