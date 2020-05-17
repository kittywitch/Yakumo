import ran.librarian
import logging
import json
import uuid


@ran.librarian.add_act("auth")
def authenticate(data, server):
    # try:
    desired_user = server.factory.users[data["username"]]
    if desired_user["hash"] == data["hash"]:
        server.user = desired_user
        server.factory.clients[server.user["uid"]] = server
        server.authenticated = True
        server.send_wrap({
            "action": "auth_success",
            "user": {
                "username": server.user["username"],
                "full_name": server.user["full_name"],
                "email": server.user["email"],
                "uid": server.user["uid"],
                "channels": server.user["channels"],
                "avatarURL": server.user["avatarURL"]
            }
        })
    # except:
    #    server.drop_user("Malformed authentication attempt.")


@ran.librarian.add_act("register")
def register(data, server):
    try:
        new_user = {
            "uid": uuid.uuid4(),
            "username": data["username"],
            "full_name": data["full_name"],
            "email": data["email"],
            "hash": data["hash"],
            "channels": [],
            "avatarURL": ""
        }
        server.factory.users[data["username"]] = new_user
        with open(os.path.join(server.factory.main_path, "./data/users.json"), "w") as userfile:
            json.dump(self.factory.users, userfile)
        self.user = desired_user
        self.authenticated = True
        server.send_wrap({
            "action": "register_success",
            "user": {
                "username": self.user["username"],
                "full_name": self.user["full_name"],
                "email": self.user["email"],
                "uid": self.user["uid"],
                "channels": self.user["channels"],
                "avatarURL": self.user["avatarURL"]
            }
        })
    except:
        server.drop_user("Malformed registration attempt.")


@ran.librarian.add_act("change_identity")
def change_identity(data, server):
    pass
