import ran.librarian
import logging
import json


@ran.librarian.add_act("user_message")
def message(data, server):
    """The equivalent of Internet Relay Chat (IRC)'s PRIVMSG.

    Implemented Flags: "sd","upload"
    Planned Flags: "enc"
    Planned Combinations: "sd"+"enc", "sd"+"enc"+"upload", "enc"+"upload", "sd"+"upload"

    In: {
        "action": "user_message", 
        "channel": "#lobby", 
        "timestamp": 1589704617, 
        "flags":[],
        "message": "hi"
    }

    Out: {
        "action": "user_message_out", 
        "username": "kat", 
        "channel": "#lobby", 
        "flags":[],
        "timestamp": 1589704617, 
        "message": "hi"
    }
    """
    # If the first character of the channel name is a & or a #, it is a channel and not a user, therefore it should be treated as if it were a channel message.
    if data["channel"][0] in ["&", "#"]:
        # Obtain the clients in the channel name provided.
        user_list = [client for (uid, client) in server.factory.clients.items(
        ) if data["channel"] in client.user["channels"]]
        for user in user_list:
            # Build a copy of the message to send to the user. This includes the sender of the message also.
            message = {
                "action": "user_message_out",
                "username": server.user["username"],
                "channel": data["channel"],
                "timestamp": data["timestamp"],
                "flags": data["flags"],
                "message": data["message"]
            }

            # Self-destructing messages are special, they have a "duration". Other types can be handled seamlessly by the client alone. e.g. enc, if it were implemented.
            if "sd" in message["flags"]:
                message["duration"] = data["duration"]

            # Send that user a copy of the message.
            user.send_wrap(message)
    # If it isn't a channel, it's a user.
    else:
        # The user who sent the message also needs a copy of the message.
        sender_message = {
            "action": "user_message_out",
            "username": server.user["username"],
            "channel": data["channel"],
            "timestamp": data["timestamp"],
            "flags": data["flags"],
            "message": data["message"]
        }

        # Self-destructing messages are special, they have a "duration". Other types can be handled seamlessly by the client alone. e.g. enc, if it were implemented.
        if sender_message["flags"] == "sd":
            sender_message["duration"] = data["duration"]

        # Here, we get the client related to the user in question through their UID, then send a copy of the message to it.
        recipient_message = {
            "action": "user_message_out",
            "username": server.user["username"],
            "channel": server.user["username"],
            "flags": data["flags"],
            "timestamp": data["timestamp"],
            "message": data["message"]
        }

        # Self-destructing messages are special, they have a "duration". Other types can be handled seamlessly by the client alone. e.g. enc, if it were implemented.
        if "sd" in recipient_message["flags"]:
            recipient_message["duration"] = data["duration"]

        # Send both the sender and the recipient their crafted messages.
        server.send_wrap(sender_message)
        server.factory.clients[server.factory.users[data["channel"]]["uid"]].send_wrap(
            recipient_message)
