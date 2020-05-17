import components.modularity, requests, logging, json

@components.modularity.add("join_channel")
def join_channel(data, server):
    if data["channel"] not in server.factory.channels:
        server.factory.channels[data["channel"]] = [server]
    else:
        server.factory.channels[data["channel"]].append(server)

@components.modularity.add("user_message")
def message_all(data, server):
    print(server.factory.channels[data["channel"]])
    for client in server.factory.channels[data["channel"]]:
        print(client.user["username"])
        #if client is not server:
        client.sendLine(json.dumps({
            "action":"user_message_out",
            "message":data["message"],
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
        }).encode("utf-8"))
    res = requests.post('http://localhost/api/add_message', json={
            "message":data["message"], 
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
    })

@components.modularity.add("user_message_sd")
def message_all_sd(data, server):
    for client in server.factory.channels[data["channel"]]:
        #if client is not server:
        client.sendLine(json.dumps({
            "action":"user_message_sd_out",
            "duration":data["duration"],
            "message":data["message"],
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
        }).encode("utf-8"))

@components.modularity.add("user_upload")
def file_upload_received(data, server):
    for client in server.factory.channels[data["channel"]]:
        #if client is not server:
        client.sendLine(json.dumps({
            "action":"user_upload_out",
            "url":data["url"],
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
        }).encode("utf-8"))