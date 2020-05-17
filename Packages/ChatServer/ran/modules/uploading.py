import ran.librarian
import logging
import json


@ran.librarian.add_act("user_upload")
def upload_handler(data, server):
    """Handles a file upload done by a client by taking the URL.

    In {
        "action": "user_upload",
        "channel": "#lobby", 
        "timestamp": 1589660858, 
        "url": "http://localhost/uploads/kat/yakumo-1dd142ed-d1c3-4541-bde1-d6735819604c.md"
    }
    Out {
        "action": "user_message_out", 
        "username": "kat", 
        "timestamp": 1589665273, 
        "channel": "#lobby", 
        "message": "User kat has uploaded a file! http://localhost/uploads/kat/yakumo-cd228df7-97dd-40ab-839d-df9291fb1322.py"
    }
    """
    try:
        if data["channel"][0] in ["&", "#"]:
            user_list = [client for (uid, client) in server.factory.clients.items(
            ) if data["channel"] in client.user["channels"]]
            for user in user_list:
                user.send_wrap({
                    "action": "user_upload_out",
                    "username": server.user["username"],
                    "timestamp": data["timestamp"],
                    "channel": data["channel"],
                    "url": data['url']
                })
        else:
            server.factory.users[data["channel"]].send_wrap({
                "action": "user_upload_out",
                "username": server.user["username"],
                "timestamp": data["timestamp"],
                "channel": data["channel"],
                "url": data['url']
            })
    except:
        server.drop_user("Malformed upload result.")
