import http.client, urllib, logging, components.modularity

def push(msg):
    client = http.client.HTTPSConnection("api.pushover.net:443")
    client.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": components.config.config.pushover["token"],
        "user": components.config.config.pushover["user"],
        "message": msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    try:
        response = client.getresponse()
        logging.info(f"Pushed \"{msg}\".")
        logging.debug(response.read().decode("utf-8"))
        return response
    except:
        return None