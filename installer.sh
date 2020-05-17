#!/bin/sh

echo "Welcome to the Yakumo Chat System installer!"
echo "Please make sure you have Python 3.8! Get it from your distribution's package manager."
echo;


pip install -e ./Packages/ChatClient/;
pip install -e ./Packages/ChatServer/;
pip install -e ./Packages/UploadAPI/;

pip install ./Packages/ChatClient/;
pip install ./Packages/ChatServer/;
pip install ./Packages/UploadAPI/;

echo "Installation is now completed!"
echo;
echo "You may access it with the commands:";
echo " * ran";
echo " * chen";
echo " * yukari";
