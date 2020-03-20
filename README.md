# shitty-steam-util

## Command line tool used to easily copy CSGO settings between profiles.
## Can also be used as a profile manager use 'help login' for more details.
#### use the 'help' command for list of commands & 'help help' to see how to use the command
#### <a href="https://www.mediafire.com/file/a16mnono6936cj5/sutil.exe/file">Compiled SUTIL</a>

How to setup:

```
  >>> set steam_path "C:\Program Files (x86)\Steam"
  >>> init
  0  Added: 'fucking weaboo'
  1  Added: 'Slumpp'
  Added 2 users to the profile list
  
  0  Backing up: C:\Program Files (x86)\Steam\userdata\1010605382
  1  Backing up: C:\Program Files (x86)\Steam\userdata\1016722479
  Backed up 2 profiles.
  >>> profs
  1010605382      0 : fucking weaboo
  1016722479      1 : Slumpp

  >>> set master "fucking weaboo"
  >>> copy * master
  1 profiles inherited settings from Slumpp
  
  >>> profs
  1010605382      0 : fucking weaboo
  1016722479      1 : Slumpp
  >>> add "fucking weaboo" <account_name> <password>
  >>> kill // This will kill Steam.exe and its processes
  >>> set login 1 // sets a master login var, this var points to the 'master' var
  >>> login 1 // this will login to the account associated with the username "fucking weaboo"
  
  
```
