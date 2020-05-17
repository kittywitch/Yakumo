import chen.logger
import chen.config
import chen.frames.register
import chen.frames.login
import chen.frames.upload
from time import strftime
import wx
import os
import json
import re
import uuid
import wx.richtext
import requests
import datetime
import io
import hashlib
import webbrowser
import pyperclip
import logging
import coloredlogs
from twisted.internet import wxreactor
wxreactor.install()
from twisted.protocols import basic
from twisted.internet import reactor, protocol, ssl


class ChatMessage():
    # Class for containing this data used for the "database"
    def __init__(self, channel, mid, username, message, timestamp):
        self.id = mid
        self.username = username
        self.channel = channel
        self.message = message
        self.timestamp = timestamp


class ChatFrame(wx.Frame):
    def __init__(self):
        # the Frame superclass init
        wx.Frame.__init__(self, parent=None, title="Chen")
        # the protocol is set in connectionMade
        self.protocol = None
        # the list of messages for each channel ["channel_name" -> [ChatMessage(...), ...]]
        self.database = {}
        # the ID of the newest loaded message in each channel
        self.message_id = {}

        # File Menu
        file_menu = wx.Menu()
        about_menu_action = file_menu.Append(
            wx.ID_ABOUT, "&About", " Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, about_menu_action)
        exit_menu_action = file_menu.Append(
            wx.ID_EXIT, "&Exit", " Terminate the program")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_action)

        # User Menu
        user_menu = wx.Menu()
        uploads_list_action = user_menu.Append(
            wx.ID_ANY, "&Uploads", " See your previous uploads.")
        self.Bind(wx.EVT_MENU, self.on_upload_list, uploads_list_action)

        # Chat Menu
        chat_menu = wx.Menu()
        #chat_mode_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Mode", " Set the mode for the channel.")
        #self.Bind(wx.EVT_MENU, self.on_chat_mode, chat_mode_action)
        #chat_topic_action = chat_menu.Append(wx.ID_ANY, "&Set Chat Topic", " Set the topic for the channel.")
        #self.Bind(wx.EVT_MENU, self.on_chat_topic, chat_topic_action)
        chat_open_sd = chat_menu.Append(
            wx.ID_ANY, "&Open chat", " Open chat with input dialogue.")
        self.Bind(wx.EVT_MENU, self.on_open_sd, chat_open_sd)
        do_user_list = chat_menu.Append(
            wx.ID_ANY, "&User list", " See channel userlist.")
        self.Bind(wx.EVT_MENU, self.on_open_sd, chat_open_sd)
        chat_send_sd = chat_menu.Append(
            wx.ID_ANY, "&Send self-destructing message", " Send self destructing message to the selected channel.")
        self.Bind(wx.EVT_MENU, self.on_send_sd, chat_send_sd)

        # Menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(chat_menu, "&Chat")
        menu_bar.Append(user_menu, "&User")
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
        self.output = wx.richtext.RichTextCtrl(
            self, style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY)
        self.channel_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.on_channel_select, self.channel_list)
        output_row.Add(self.channel_list, 1, wx.EXPAND | wx.ALL)
        output_row.Add(self.output, 4, wx.EXPAND | wx.ALL)

        # Window Rows
        window_rows = wx.BoxSizer(wx.VERTICAL)
        window_rows.Add(output_row, 5, wx.EXPAND | wx.ALL)
        window_rows.Add(input_row, 0, wx.EXPAND | wx.ALL)

        self.SetAutoLayout(True)
        self.SetSizer(window_rows)
        self.Layout()

    def send_wrap(self, data):
        self.protocol.sendLine(json.dumps(data).encode("utf-8"))

    def do_user_list(self, data):
        pass

    def send(self, evt):
        selected_index = self.channel_list.GetSelection()
        if selected_index != -1:
            self.send_wrap({
                "action": "user_message",
                "channel": self.channel_list.GetString(selected_index),
                "timestamp": int(datetime.datetime.utcnow().timestamp()),
                "flags": [],
                "message": self.user_input.GetValue()
            })
            self.user_input.SetValue("")
        else:
            dialog = wx.MessageDialog(
                self, "No channel is selected.", "Warning", wx.ICON_WARNING)
            dialog.ShowModal()
            dialog.Destroy()

    def on_channel_select(self, e):
        selected_index = self.channel_list.GetSelection()
        current_channel = self.channel_list.GetString(selected_index)
        self.output.Clear()
        for message in self.database[current_channel]:
            self.output.WriteText(
                f"[{strftime('%Y-%m-%d %H:%M:%S')}] {message.username}: {message.message}")
            self.output.Newline()
            self.output.SetInsertionPointEnd()

    def on_upload_list(self, e):
        res = requests.post('http://localhost/api/uploads', json={
            "username": self.protocol.user["username"]
        })
        if res.ok:
            result = res.json()
        uploadWin = chen.frames.upload.UploadsFrame(
            "Login", self, res.json()["uploads"], parent=self)
        uploadWin.Show()

    def on_open_sd(self, e):
        """Opening a chat.
        """
        # get channel selected
        selected_index = self.channel_list.GetSelection()
        # get name of channel / user
        dlg = wx.TextEntryDialog(
            self, 'Who or where do you want to open a chat with?', 'Username / Channel Name')
        # if user hits ok,
        if dlg.ShowModal() == wx.ID_OK:
            # get the name, open the chat
            if len(dlg.GetValue()):
                self.channel_list.InsertItems(
                    [dlg.GetValue()], self.channel_list.GetCount())
                self.database[dlg.GetValue()] = []
                self.message_id[dlg.GetValue()] = 0
                if dlg.GetValue()[0] in ["&", "#"]:
                    self.send_wrap({
                        "action": "join_channel",
                        "channel": dlg.GetValue()
                    })
            else:
                dialog = wx.MessageDialog(
                    self, "Unlikely to be a valid location.", "Warning", wx.ICON_WARNING)
                dialog.ShowModal()
                dialog.Destroy()

    def on_send_sd(self, e):
        """Sending a self-destructing message.
        """
        # get channel selected
        selected_index = self.channel_list.GetSelection()
        # ask user for seconds duration
        dlg = wx.TextEntryDialog(
            self, 'How long do you want that message to last?', 'Message duration in seconds')
        # if the user presses OK,
        if dlg.ShowModal() == wx.ID_OK:
            # get the duration
            duration = int(dlg.GetValue())
            # if a channel is selected,
            if selected_index != -1:
                # send the message and clear the input buffer
                self.send_wrap({
                    "action": "user_message",
                    "duration": duration,
                    "channel": self.channel_list.GetString(selected_index),
                    "flags": ["sd"],
                    "timestamp": int(datetime.datetime.utcnow().timestamp()),
                    "message": self.user_input.GetValue()
                })
                self.user_input.SetValue("")
            else:
                dialog = wx.MessageDialog(
                    self, "No channel is selected.", "Warning", wx.ICON_WARNING)
                dialog.ShowModal()
                dialog.Destroy()

    # def on_chat_mode(self, e):
    #    pass

    # def on_chat_topic(self, e):
    #    pass

    def on_about(self, e):
        dialog = wx.MessageDialog(
            self, "A chat application written in Python using the Twisted networking library and wxWidgets.", "Chen v0.0.1", wx.OK)
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

                # from the file path, try to upload the file in a multipart request with the username being posted alongside the file itself to flask
                pathname = fileDialog.GetPath()
                try:
                    files = {
                        'username': (None, self.protocol.user["username"]),
                        'upload_file': (os.path.basename(pathname), open(pathname, 'rb'), 'application/octet-stream')
                    }
                    r = requests.post(
                        "http://localhost/api/upload", files=files)
                    if r.ok:
                        url = f"http://localhost{r.json()['url']}"
                        self.send_wrap({
                            "action": "user_message",
                            "flags": ["upload"],
                            "channel": self.channel_list.GetString(selected_index),
                            "timestamp": int(datetime.datetime.utcnow().timestamp()),
                            "message": url
                        })
                except IOError:
                    wx.LogError("Cannot open file")
        else:
            dialog = wx.MessageDialog(
                self, "No channel is selected.", "Warning", wx.ICON_WARNING)
            dialog.ShowModal()
            dialog.Destroy()

    def on_exit(self, e):
        # when the exit button is hit, you wanna close the program
        os._exit(1)
        self.Close(True)


class ChenCProtocol(basic.LineReceiver):
    def __init__(self):
        self.output = None
        # user object from the server
        self.user = None

    def delete_line(self, location):
        """Facilitates self-destructing messages.
        """
        # location -> location[0] is message id, location[1] is channel_name
        logging.debug(location)
        # the message in question before deletion
        previous = self.factory.gui.database[location[1]][location[0] - 1]
        # replacing the message in question -> "deletion"
        self.factory.gui.database[location[1]][location[0] - 1] = ChatMessage(
            previous.channel, self.factory.gui.message_id[previous.channel], "System", "Message deleted.", previous.timestamp)
        # if it's in the current channel, redraw that channel
        selected_index = self.factory.gui.channel_list.GetSelection()
        current_channel = self.factory.gui.channel_list.GetString(
            selected_index)
        if current_channel == location[1]:
            self.factory.gui.output.Clear()
            for message in self.factory.gui.database[current_channel]:
                self.factory.gui.output.WriteText(
                    f"[{datetime.date.fromtimestamp(message.timestamp).strftime('%Y-%m-%d %H:%M:%S')}] {message.username}: {message.message}")
                self.factory.gui.output.Newline()
                self.factory.gui.output.SetInsertionPointEnd()

    def dataReceived(self, line):
        # if it's not valid JSON, it'll ValueError, otherwise the try: and else: blocks will run fine.
        try:
            logging.debug(f"<- {line}")
            ingest = json.loads(line)
        except ValueError as e:
            self.drop_user(f"Malformed JSON sent by \"{self.ip}\".")
        else:
            # Safe ingested message
            message = ingest
            # GUI object
            gui = self.factory.gui
            # list for lines to add to GUI
            lines = []

        if message["action"] == "auth_req":
            # show the login window upon login
            login_window = chen.frames.login.LoginFrame(
                "Login", self, parent=self)
            login_window.Show()

        if message["action"] == "auth_success":
            self.user = message['user']
            gui.channel_list.InsertItems(self.user["channels"], 0)
            for channel in self.user["channels"]:
                gui.database[channel] = []
                gui.message_id[channel] = 0
            lines.append(
                f"[{strftime('%Y-%m-%d %H:%M:%S')}] Logged in as {self.user['username']} - {self.user['full_name']} - {self.user['email']}.")
            lines.append("\n")
            lines.append("Please select a channel to begin.")

        if message["action"] == "register_success":
            self.user = message['user']
            gui.channel_list.InsertItems(self.user["channels"], 0)
            for channel in self.user["channels"]:
                gui.database[channel] = []
                gui.message_id[channel] = 0
            lines.append(
                f"Registered as {self.user['username']} - {self.user['full_name']} - {self.user['email']}.")
            lines.append("\n")
            lines.append("Please select a channel to begin.")

        if message["action"] == "user_message_out":
            # if it's not a channel and it's not in the database, it's a new user messaging, so open a "channel" for that user.
            if not message["channel"][0] in ["&", "#"] and message["channel"] not in gui.database:
                gui.database[message["channel"]] = []
                gui.message_id[message["channel"]] = 0
                gui.channel_list.InsertItems(
                    [message["channel"]], gui.channel_list.GetCount())
            # append the message to the channel database
            gui.database[message["channel"]].append(ChatMessage(
                message["channel"], gui.message_id[message["channel"]], message["username"], message["message"], message["timestamp"]))
            # increment the message_id, it is never decremented
            gui.message_id[message["channel"]
                           ] = gui.message_id[message["channel"]] + 1
            if "sd" in message["flags"]:
                reactor.callLater(int(message["duration"]), self.delete_line, (
                    gui.message_id[message["channel"]], message["channel"]))
            # get selected channel, if it is the current channel, append the new messages to that channel to it
            if gui.channel_list.GetSelection() != -1:
                selected_index = gui.channel_list.GetSelection()
                selected_channel = gui.channel_list.GetString(selected_index)
                if selected_channel == message["channel"]:
                    # The upload flag is formatted specifically differently.
                    if "upload" in message["flags"]:
                        lines.append(
                            f"[{strftime('%Y-%m-%d %H:%M:%S')}] User \"{message['username']}\" has uploaded: {message['message']}")
                    else:
                        lines.append(
                            f"[{strftime('%Y-%m-%d %H:%M:%S')}] {message['username']}: {message['message']}")
        if gui:
            for output_line in lines:
                if output_line == "\n":
                    # if it's a newline, print a newline
                    gui.output.Newline()
                else:
                    # if it isn't a new line, write it, then place a newline, then set insertion point at the end.
                    gui.output.WriteText(output_line)
                    gui.output.Newline()
                    gui.output.SetInsertionPointEnd()

    def connectionMade(self):
        self.factory.gui.protocol = self


class ChenCFactory(protocol.ClientFactory):
    def __init__(self, gui, cfg):
        # protocol definition for the factory
        self.protocol = ChenCProtocol
        # GUI insertion
        self.gui = gui
        # CFG insertion
        self.cfg = cfg

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()


def main():
    # provide the directory of the app.py to other files
    base_path = os.path.dirname(os.path.abspath(__file__))
    # load config
    cfg = chen.config.config_setup(base_path)
    # set up logger
    chen.logger.logging_setup(base_path, cfg)
    # set up the app
    app = wx.App(False)
    frame = ChatFrame()
    frame.Show()
    # bind the app to the reactor
    reactor.registerWxApp(app)
    # run the reactor with SSL verification disabled
    reactor.connectSSL("localhost", 4242, ChenCFactory(
        frame, cfg), ssl.CertificateOptions(verify=False))
    reactor.run()


if __name__ == '__main__':
    main()
