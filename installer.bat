@echo off

echo Welcome to the Yakumo Chat System installer!
echo Please make sure you have Python 3.8 and Build Tools for Visual Studio 2019! These are requirements for the project.
echo A version is provided in "./Dependencies".
echo Python 3.8 is available from: https://www.python.org/downloads/windows/ as "Latest Python 3 Release".
echo Build Tools for Visual Studio 2019 is available from: https://visualstudio.microsoft.com/downloads/ at the bottom of the "Tools for Visual Studio 2019" dropdown category.
echo You will want to select "C++ build tools" from the "Desktop & Mobile" section. This will require approximately ~4.7GiB.
echo.

if /i "%~1"=="/debug" goto Debug else goto Normal

:Normal
pip install ./Packages/ChatClient/
pip install ./Packages/ChatServer/
pip install ./Packages/UploadAPI/
goto End
:Debug
pip install ./Packages/ChatClient/;
pip install ./Packages/ChatServer/;
pip install ./Packages/UploadAPI/;
goto End

:End
echo Installation is now completed!
echo.
echo You may access it with the commands:
echo  * ran
echo  * chen
echo  * yukari