import components.modularity, requests, logging, json

@components.modularity.add("user_message")
def message_all(data, server):
    for client in server.factory.clients:
        #if client is not server:
        client.sendLine(json.dumps({
            "action":"user_message_out",
            "message":data["message"],
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
        }).encode("utf-8"))

@components.modularity.add("user_upload")
def file_upload_received(data, server):
    for client in server.factory.clients:
        #if client is not server:
        client.sendLine(json.dumps({
            "action":"user_upload_out",
            "url":data["url"],
            "channel":data["channel"],
            "username":server.user["username"],
            "timestamp":data["timestamp"]
        }).encode("utf-8"))