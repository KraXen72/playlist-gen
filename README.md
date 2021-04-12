# playlist-gen
  
This is a small utility in python that i made to generate ``.m3u`` playlists if you have your music sorted into folders. example:  
![ex1](https://cdn.discordapp.com/attachments/704792091955429426/813334438322765864/playlist_gen.png)
  
## Setup
requirements:
- python3
- python libraries (should be already installed by default with python):
    - os
    - pathlib
    - codecs
  
## Install
1. Clone this repo
2. run ``pip install prompt-toolkit`` anywhere
3. copy ``playlist-gen.py`` to the folder with all your music
4. run ``python playlist-gen.py`` or just ``playlist-gen.py`` in the folder with all your music. clicking on it should also run it.

## How to use
Available commands:
- ``ext`` - set the extensions of music files. default: mp3
- ``ign`` - set the folders to ignore in generation. none by default
- ``gen`` - recursively generate m3u playlists for all folders and subfolders
- ``prg`` - delete all existing .m3u files in the working directory for a clean slate
- ``com`` - generate a playlist from multiple specific folders
- ``add`` - add a folder or folders to a playlist made by ``com``. doesen't rename the playlist
- ``add -r`` - same thing as ``add`` but appends the folder name to the playlist name. 
- ``new`` - manually make a new playlist by selecting songs and playlists
- ``help`` - display this message
- ``exit`` or ``quit`` - exit this utility
  
to bring up this list just type ``help`` in the uitility

all commands have explanations and examples right in the utility.

for any questions contact me on discord ``KraXen72#9190``