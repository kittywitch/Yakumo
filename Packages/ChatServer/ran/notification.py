import http.client
import urllib
import logging
import ran.librarian
import ran.config


def push(message, config_section):
    if config_section["toggle"]:
        client = http.client.HTTPSConnection("api.pushover.net:443")
        client.request(
            "POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": config_section["token"],
                "users": config_section["user"],
                "message": message,
            }), {"Content-type": "application/x-www-form-urlencoded"}
        )
        try:
            response = client.getresponse()
            logging.debug(f"Pushed \"{message}\".")
            logging.debug(response.read().decode("utf-8"))
            return response
        except:
            pass
