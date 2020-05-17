import ran.librarian
import logging
import json


@ran.librarian.add_act("abandon_channel")
def channel_abandon(data, server):
    if data["channel"][0] in ["&", "#"]:
        the_channel = server.factory.channels[data["channel"]]
        abandoner = the_channel["owner"]
        if the_channel["owner"] == data["response"]:
            the_channel["owner"] = None
            the_channel["registered"] = False
            server.send_wrap({
                "action": "abandoned_channel",
                "channel": data["channel"]
            })
        user_list = [
            client for client in server.factory.clients if data["channel"] in client.channels]
        for user in user_list:
            user.send_wrap({
                "action": "channel_abandoned",
                "channel": data["channel"],
                "abandoner": abandoner
            })


@ran.librarian.add_act("join_channel")
def join_channel(data, server):
    """Joins a user into the channel and vice versa.

    In: {
        "action": "join_channel",
        "channel": "#lobby"
    }
    Out: {
        "action":"join_channel",
        "channel":"#lobby",
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
    server.user["channels"].append(data["channel"])
    server.factory.channels[data["channel"]]["users"].append(server.user)
    user_list = []
    for user in server.factory.channels[data["channel"]]["users"]:
        user_list.append(ran.librarian.sanitize_user(user))

    server.send_wrap({
        "action": "join_channel",
        "channel": data["channel"],
        "user_list": user_list
    })


@ran.librarian.add_act("part_channel")
def part_channel(data, server):
    """Parts a user from the channel and vice versa.

    In: {
        "action": "part_channel",
        "channel": "#lobby"
    }
    Out: {
        "action":"part_channel"
        "channel":"#lobby",
    }
    """
    server.user["channels"].remove(data["channel"])
    server.factory.channels[data["channel"]]["users"].remove(server.user)
    for user in server.factory.channels[data["channel"]]["users"]:
        user.send_wrap({
            "action": "other_part_channel",
            "channel": data["channel"],
            "username": server.user["username"]
        })
    server.send_wrap({
        "action": "part_channel",
        "channel": data["channel"]
    })


@ran.librarian.add_act("change_topic")
def topic_channel(data, server):
    pass
