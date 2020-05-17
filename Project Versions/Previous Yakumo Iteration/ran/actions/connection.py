import components.modularity, requests, logging, json

@components.modularity.add("auth")
def auth(data, server):
    if "username" in data and "password" in data:
        res = requests.post('http://localhost/api/login', json={
            "username":data["username"], 
            "password":data["password"]
        })
    elif "token" in data:
        res = requests.post('http://localhost/api/login', json={
            "token":data["token"]
        })
    if res.ok:
        result = res.json()
        if result["status"] == "successful":
            server.user = json.loads(result["user"])
            server.sendLine(json.dumps({
                "action":"auth_success", 
                "user":result["user"],
                "token":result["token"]
            }).encode("utf-8"))
            server.authenticated = True