import ran.librarian
import logging
import json


@ran.librarian.add_act("user_list")
def user_list(data, server):
    """Provides the client with a sanitized userlist, removing all of the hashes and so on from the user objects.

    In: {
        "action":"user_list",
        "location":"#lobby"
    }

    Out: {
        "action": "user_list",
        "type": "event",
        "location":"#lobby",
        "user_list": {
            "kat": {
                "uid":"069fd90d-3f9d-44b8-b3ed-50d0fff0d4c5",
                "full_name":"kat witch",
                "email":"kat@kittywit.ch",
                "avatarURL":""
            }
        }
    }
    """
    # Only users in a channel should be able to request the user list of that channel.
    if data["location"] in server.user.channels:
        # This line takes every single user in a channel provided and turns them into a list.
        user_list = [ran.librarian.sanitize_user(self.factory.users[uid]) for (
            uid, client) in self.factory.clients if data["location"] in self.factory.users[uid]["channels"]]
        server.send_wrap({
            "response": "user_list",
            "location": data["location"],
            "type": "event",
            "user_list": json.dumps(user_list)
        })
