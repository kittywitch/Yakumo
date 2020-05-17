import components.pushover, components.protocol, components.modularity, components.config
from twisted.internet import reactor, ssl
import os, logging, sys, coloredlogs, threading, socket

def intro():
    print("")
    print("$$$$$$$\\                      ")
    print("$$  __$$\\                     ")
    print("$$ |  $$ | $$$$$$\\  $$$$$$$\\  ")
    print("$$$$$$$  | \\____$$\\ $$  __$$\\") 
    print("$$  __$$<  $$$$$$$ |$$ |  $$ |")
    print("$$ |  $$ |$$  __$$ |$$ |  $$ |")
    print("$$ |  $$ |\\$$$$$$$ |$$ |  $$ |")
    print("\\__|  \\__| \\_______|\\__|  \\__|")
    print("")
    print("The chat protocol server of the Yakumo System.")
    print("")

def main():
    # Show an intro message about the program.
    intro()

    # Set up logging.
    ## Sets up a debug level logger that overwrites the file
    logging.basicConfig(level=logging.DEBUG,filemode="w")
    logFormatter = logging.Formatter("[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    ## Remove the default logger.
    rootLogger.handlers = []
    ## Hook the logger up to the file "server.log"
    fileHandler = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "data/server.log"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    ## Hook the logger up to the console
    coloredlogs.install(level='DEBUG',fmt="[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s")

    # Establish the location of main.py
    components.modularity.base_path = os.path.dirname(os.path.abspath( __file__ ))
    logging.info(f"Running from {components.modularity.base_path}.")
    
    # SSL
    certpath = os.path.join(components.modularity.base_path, "data/keys/server.pem")
    if os.path.exists(certpath):
        with open(certpath) as f:
            certData = f.read()
    else:
        logging.error("File {certpath} does not exist.")
    certificate = ssl.PrivateCertificate.loadPEM(certData).options()

    # Load config
    components.config.init()

    # Load actions from actions/
    components.modularity.import_dir(os.path.join(components.modularity.base_path, "actions"))
    logging.info(f"Loaded {len(components.modularity.actions)} actions: {', '.join(components.modularity.actions.keys())}.")

    # Start the server and reactor, do a push notification.
    components.pushover.push(f"Yakumo/Yukari - Running on {socket.gethostname()}")
    reactor.listenSSL(components.config.config.port, components.protocol.RanSFactory(components.modularity.actions), certificate)
    reactor.run()

if __name__ == "__main__":
    main()
