# shitty-steam-util

## Command line tool used to easily copy CSGO settings between profiles.
#### use the 'help' command for list of commands & 'help help' to see how to use the command

Example set up: 

>>> set steam_path "C:\Program Files (x86)\Steam"
>>> init
0  Added: 'profile1'
1  Added: 'profile2'

Added 10 users to the profile list
0  Backing up: C:\Program Files (x86)\Steam\userdata\1010605382
1  Backing up: C:\Program Files (x86)\Steam\userdata\1016722479

Backed up 10 profiles.
>>> profs
1010605382      0 : profile1
1016722479      1 : profile2

>>> set master profile1
>>> copy * master
1 profiles inherited settings from profile1


