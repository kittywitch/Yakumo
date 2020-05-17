"""This is the function that sets up the reactor.
"""

from twisted.internet import reactor, ssl
import logging
import os

import ran.protocol


def reactor_setup(main_path, actions, config, users, channels, roles):
    """ Sets up the reactor for the chat server application.
    """
    if config["connection"]["ssl"]["toggle"]:
        logging.info("SSL enabled - loading certificate details")
        # the full path is a total of ./data/keys/ and server.pem
        full_name = config["connection"]["ssl"]["directory"] + \
            "/" + config["connection"]["ssl"]["filename"]
        cert_path = os.path.join(main_path, full_name)
        if os.path.exists(cert_path):
            with open(cert_path) as f:
                cert_data = f.read()
        else:
            logging.error(f"File {cert_path} does not exist.")

        certificate = ssl.PrivateCertificate.loadPEM(cert_data).options()

        logging.info("SSL enabled - beginning SSL reactor")
        reactor.listenSSL(config["connection"]["port"], ran.protocol.RanSFactory(
            main_path, actions, config, users, channels, roles), certificate)
    else:
        logging.info("SSL disabled - beginning TCP reactor")
        reactor.listenTCP(config["connection"]["port"], ran.protocol.RanSFactory(
            main_path, actions, config, users, channels, roles))
    reactor.run()
