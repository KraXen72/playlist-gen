#file operations
import os
import pathlib
import codecs

#music file metadata reading
from tinytag import TinyTag #add tinytag to readme
import mutagen #file length

#rounding
from decimal import *

#autocomplete
from prompt_toolkit.completion import WordCompleter, FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.validation import Validator, ValidationError

global config
global exts
global useEXTINF
useEXTINF = True
exts = ["mp3"] #extensions to consider as valid
ign = [] #folder names to ignore
naughtylist = [] #songs that i should redownload

import json

#functions

#format song length
def formatSongLength(len):
    # round to 3 decimal spaces and replace the dot with nothing
    bonk = str(Decimal(len).quantize(Decimal('0.001'), ROUND_HALF_UP)).replace(".","")
    return bonk

#get info about a song
def getSongInfo(song, fullpath):
    
    
    #use mutagen for song length, and Tinytag for title and artist
    info = mutagen.File(fullpath)
    output = info

    tag = TinyTag.get(fullpath)
    title = str(tag.title)
    artist = str(tag.artist)

    #print(title + " - "+ artist)
 
    #if there is no artist or title then just put filename as title
    if title == "None" and artist == "None":
        songy = song.rsplit("\\", 1) #remove folder
        if songy.__len__() > 1:
            songy = songy[1]
        else:
            songy = songy[0]
        parts = songy.rsplit('.',1) #remove extension
        title = parts[0]
        artist = "Unknown Artist"

        #add it to naughty list
        suitableForNaughty = True
        """for i in ign:
            if i in song:
                suitableForNaughty = False"""
        if suitableForNaughty == True:
            naughtylist.append(song)
    
    myinfo = {
        "ttitle": title,
        "tartist": artist,
        #"tlength": formatSongLength(int(tag.durations))
        "tlength": formatSongLength(output.info.length)
    }
    extinfo = "#EXTINF:{},{} - {}".format(myinfo["tlength"], myinfo["tartist"], myinfo["ttitle"])
    return extinfo

# generate a playlist for given path
# arguments:
# currpath (str) - the path to generate
# returnInsteadOfWriting (bool) - return an array of the songs instead of making a file
# includePlaylists (bool) - include .m3u playlists as songs
def generatem3u(currpath, includeSongs, returnInsteadOfWriting, includePlaylists): 
    music = [] #valid music files
    listOfFiles = [] #all files for the current directory, with relative path

    #clear arrays for good measure
    music.clear()
    listOfFiles.clear()

    splitpath = currpath.split("\\")
    name = splitpath[-1] #get the parent folder name

    for (dirpath, dirnames, filenames) in os.walk(currpath): #recursively find all files in the folder
        patharr = dirpath.split("\\")
        nameind = patharr.index(name)
        relativepath = "\\".join(patharr[nameind+1:])
        listOfFiles += [os.path.join(relativepath, file).replace("/", "\\") for file in filenames]

    for song in listOfFiles: #check if file is a .mp3
        parts = song.split('.')
        ext = parts[-1]

        #if the file extension is in the 'myext' list, add it to music
        myexts = exts
        if includeSongs == False:
            myexts = []

        if includePlaylists == True:
            myexts.append('m3u')

        if str(ext).lower() in myexts:
            if useEXTINF == True and returnInsteadOfWriting == False and includePlaylists == False:
                music.append(getSongInfo(song, currpath + "\\" + song))
            music.append(song)
    if str(name) in ign: #ingore if on the ignore list
        print("ignoring folder " + name)
    else:
        if music.__len__() > 0: #write mp3 songs to file or return array
            if returnInsteadOfWriting == True:
                return music
            else:
                if useEXTINF == True and returnInsteadOfWriting == False and includePlaylists == False:
                    music.insert(0,'#EXTM3U')
                f = codecs.open(currpath + "\\" + name+".m3u", "w", "utf-8")
                aaa = "\n".join(music)
                f.write(aaa)
                f.close()
                print("generated {}.m3u".format(name))
                music.clear()
                listOfFiles.clear()
        else: #if no valid songs just skip
            print("no mp3 files found for "+ name)

#generate playlists for all folders
def cmdgen(): 
    print("generating for all subfolders..")
    # get the current path using pathlib
    currpath = str(pathlib.Path(__file__).parent.absolute())
    
    #get all subdirectories - x is an array which contains the path as first, and the files as the rest of the array, we only need the path
    dirs = [str(x[0]) for x in os.walk(currpath)] 

    for dir in dirs: #generate for every subdirectory
        generatem3u(dir, True, False, False)
    
    print("done. ")

#print help message
def cmdhelp():
    print("---------- help:")

    hlep = [
        "---------- actions ----------",
        "'gen' - generate m3u playlists for all folders and subfolders. run this every time you add/delete songs.",
        "'new' - make a new playlist by selecting songs and playlists",
        "'com' - make a new playlist from multiple specific playlists (run 'gen' first)",
        "'edit' - edit a playlist, you can add playlists or songs to it.",
        "'re' - remake/recover a playlist make by 'com', if you added songs to the folders"
        " ",
        "---------- other ----------",
        "'prg' - delete all existing .m3u files in the working directory for a clean slate",
        "'naughty' - [EXPERIMENTAL] run this after 'gen' to find songs with bad metadata that you can redownload / fix"
        "'help' - display this message",
        "'exit' or 'quit' - exit this utility",
        " ",
         "---------- setup ----------",
        "'ext' - set the extensions of music files. default: mp3. only some extensions supported.",
        "'ign' - set the folders to ignore in generation. none by default",
        "'plainm3u' - use plain .m3u instead of extended .m3u, faster but may not work on some players."]
    
    print("\n".join(hlep))

#set the extensions considered songs, and print the current ones/
def cmdexts():
    print("---------- ext")
    print("the current extensions considered songs are:")
    print(exts)
    print("----------")
    print("enter the music extensions you use. lowercase. \n if there are more, separate them by , \n example: mp3,flac,ogg \n example2: ogg")
    newexts = input(': ').split(",")
    return newexts

#set the names of ignored folders
def cmdign():
    print("---------- ign")
    print("enter the folder names to ignore. case sensitive. \n if there are more, separate them by , \n example: trash,archive,onHold \n example2:  (empty to not ignore anything)")
    ign = input(': ').split(",")
    print("also ignore subfolders of these? (y/n)")
    ignsubs = input(': ')
    if ignsubs == "y":
        currpath = str(pathlib.Path(__file__).parent.absolute())
        dirs = [f for f in os.listdir(currpath) if os.path.isdir(f)]
        allignore = []

        for dir in dirs:
            if dir in ign:
                for x in os.walk(dir):
                    parts = x[0].split("\\")
                    foldername = parts[-1]
                    allignore.append(foldername)
        ign = allignore
        print("ignoring folders: ")
        print(ign)
        return ign
    else:
        print("ignoring folders: (subfolders are not ignored)")
        print(ign)
        return ign

#purge/delete all m3u playlists
def cmdprg():
    print("---------- prg")
    print("are you sure you want to delete all m3u files from folders and subfolders? (y/n)")
    yorn = input(': ')
    if yorn == "y":
        currpath = str(pathlib.Path(__file__).parent.absolute())
        for (dirpath, dirnames, filenames) in os.walk(currpath):
            for f in filenames:
                myfile = os.path.join(dirpath, f)

                filearr = str(myfile).split(".")
                ext = filearr[-1]

                if ext == "m3u":
                    print("purging: " + str(f))
                    os.remove(myfile)
    else:
        print("purge was cancelled.")

# a playlist picker for playlist editor
def loadPlaylistPicker():
    print("---------- pick a playlist for editing")

    playlists = generatem3u(currpath, False, True, True)

    #set up autocomplete
    class PlaylistValidator(Validator): #autocomplete validator = check if song acutally exists
        def validate(self, document):
            text = document.text
            if text and text not in playlists:
                raise ValidationError(message="this playlist doesen't exist", cursor_position=text.__len__())
    
    playlist_completer = WordCompleter(playlists, ignore_case=True, sentence = True,match_middle=True)
    
    # autocomplete prompt
    playlist = prompt("-> ",completer=playlist_completer,validator=PlaylistValidator(),complete_while_typing=True,validate_while_typing=False)

    #read the file and pass the songs to playlistEditor
    f = codecs.open(playlist, "r", "utf-8")
    unfilteredsongs = f.read().split("\n")
    f.close()
    songs = []

    #filter out m3u comments
    for song in unfilteredsongs:
        if "#EXTINF:" not in song and '#EXTM3U' not in song:
            songs.append(song)

    playlistEditor("edit", songs, playlist)


#create a new playlist by adding songs and playlists together
# a multipurpose manual playlist editor
# mode (str) = mode, "new"|"com"|"add"|"edit"
# loadPlaylist (arr) = a playlist to load, []|array of songs
def playlistEditor(mode, loadPlaylist, filename):
    playlist = []
    commandhistory = []
    
    if mode == "new" or mode == "com":
        print("name your new playlist: ")
        name = input(": ")

    #load all available songs for autocomplete
    if mode == "new":
        allsongs = generatem3u(currpath, True, True, True)
    elif mode == "com":
        allsongs = generatem3u(currpath, False, True, True)
    elif mode == "edit" or mode == "add":
        allsongs = generatem3u(currpath, True, True, True)
        playlist = loadPlaylist
        name = filename

    #set up autocomplete
    class SongValidator(Validator): #autocomplete validator = check if song acutally exists
        def validate(self, document):
            text = document.text
            if text and text not in allsongs and text != "$playlist-done":
                raise ValidationError(message="this song doesen't exist", cursor_position=text.__len__())
    
    done = False
    save = False
    song = ""

    if mode == "new" or mode == "com":
        print("---------- new playlist: {}.m3u".format(name))
    elif mode == "edit":
        print("---------- editing '{}'".format(filename))

    print("search for a song or playlist you want to add (tab to show suggestions)")
    print("if you are done, just type '$playlist-done'")

    #main edit loop - add songs or playlists, TODO: remove songs, not playlists
    while done == False:
        availableSongs = [x for x in allsongs if x not in playlist] #only suggest songs not already in the playlist
        availableSongs.append("$playlist-done")

        #set up completer
        song_completer = WordCompleter(availableSongs, ignore_case=True, sentence = True,match_middle=True)
        # autocomplete prompt
        song = prompt("-> ",completer=song_completer,validator=SongValidator(),complete_while_typing=True,validate_while_typing=False)

        if song != "$playlist-done":
            commandhistory.append(song) #add this song to the command history, so i can print it later
            if ".m3u" in song: # if its a playlist add all its songs
                songParent = song.rsplit("\\", 1)[0]

                
                if songParent[-1] != "\\": #add a slash to the end if there isn't one
                    songParent += "\\"

                #if the playlist is in the topmost directory, the songParent will be the song itself
                if songParent == song + "\\":
                    songParent = ""

                f = codecs.open(currpath + "\\" + song, "r", "utf-8")
                tempcontents = f.read()
                lines = tempcontents.split("\n")
                f.close()

                for line in lines:
                    if songParent + line not in playlist and "#EXTINF:" not in line and '#EXTM3U' not in line: #only add the song if it already isn't in the playlist, to avoid duplicates
                        if useEXTINF == True:
                            print(bull + "parent: " + songParent + " line: " + line)
                            playlist.append(getSongInfo(song, song))
                        playlist.append(song)
            else: #add the song to the playlist
                if useEXTINF == True:
                    playlist.append(getSongInfo(song, song))
                playlist.append(song)
        else: #pause the process
            if mode == "new": #cmdnew, print all the songs
                print("---------- {}.m3u ----------".format(name))
                for ponk in playlist:
                    if "#EXTINF" not in ponk:
                        print(ponk)
            elif mode == "com": #cmdcom, just show the playlists from command history
                print("---------- {}.m3u ----------".format(name))
                for command in commandhistory: 
                    print(bull + " " + command)
            elif mode == "edit":
                print("---------- {} ----------".format(filename))
            
            print("----------")
            print("add more? (a) save to file? (s) cancel? (c)")
            decision = input(": ")

            if decision == "s": #save
                done = True
                save = True
            elif decision == "c": #cancel
                done = True
                save = False
            elif decision == "a":
                print("returned to add mode")
            else: 
                print("'{}' not recognized. returning to add mode".format(decision))

    if save == True:
        #make a config entry, so i can regen this playlist later
        playlistobj = {
            "path": currpath + "\\" + name + ".m3u",
            "playlists": []
        }
        for play in commandhistory:
            playlistobj["playlists"].append(play)
        config["complaylists"][name] = playlistobj
        saveconfig()

        f = codecs.open(currpath + "\\" + name + ".m3u", "w", "utf-8")
        if useEXTINF == True:
            playlist.insert(0,'#EXTM3U')
        f.write("\n".join(playlist))
        f.close()

        print("sucessfully made playlist {}.m3u".format(name))
    elif save == False:
        print("cancelled, notihing saved.")

# disable useEXTINF and use plain m3u
def plainm3u():
    print("---------- plaimm3u")
    print("all playlist operations will now be plain m3u instead of extended m3u.")
    print("---------- what does this mean?")
    print("this omits all #EXTINF lines, as well as #EXTM3U as the first line and is a lot faster.")
    print("however, some players won't recognize plain m3u playlists and refuse to play them.")
    print("this is temporary, next time you run the script, it will still use extended m3u.")
    print("---------- wait no go back i want extended m3u")
    print("if you acidentally ran this command, just exit out of this utility and run it again.")
    print("---------- ok what now")
    print("it is recommended to run 'gen' before anything else so the playlists generate in plain m3u.")

    return False

def saveconfig():
    f = codecs.open(currpath + "\\playlistgen-config.json", "w", "utf-8")
    f.write(json.dumps(config))
    f.close()

currpath = str(pathlib.Path(__file__).parent.absolute())
bull = chr(8226)
print("welcome to playlist generator.")
print("----------")

#load the ignore list if it exists
if os.path.isfile(currpath + "\\playlistgen-config.json"): 
    #load config if it already exists
    f = codecs.open(currpath + "\\playlistgen-config.json", "r", "utf-8")
    configstr = str(f.read())
    config = json.loads(configstr)
    ign = config["ignorelist"]
    f.close()
else: #create config
    config = {
        "ignorelist": [],
        "complaylists": {}
    }
    if os.path.isfile(currpath + "\\gen-ignorelist.txt"):
        f = codecs.open(currpath + "\\gen-ignorelist.txt", "r", "utf-8")
        config["ignorelist"] = f.read().split("\n")
        f.close()
    ign = config["ignorelist"]
    saveconfig()

#print(config["ignorelist"])

while True: #main command loop
    print("\n")
    command = input( bull + ' gen: what would you like to do? ("help" to list all commands): ')

    if command == 'help':
        cmdhelp()
    elif command == 'exit' or command == "quit":
        quit()
    elif command == "plainm3u":
        useEXTINF = plainm3u()
    elif command == 'gen':
        cmdgen()
    elif command == "ext":
        exts = cmdexts()
        print("set extensions to: ")
        print(exts)
    elif command == "ign":
        ign = cmdign()
        config["ignorelist"] = ign
        saveconfig()
        print("disclaimer: if a folder matches the name in the ignored list, it will be ignored.")
    elif command == "prg":
        cmdprg()
    elif command == "com":
        playlistEditor("com", [], "")
    elif command == "new":
        playlistEditor("new", [], "")
    elif command == "edit":
        loadPlaylistPicker()
    elif command == "naughty":
        f = codecs.open(currpath + "\\naughty-list.txt", "w", "utf-8")
        f.write("\n".join(naughtylist))
        f.close()
        print("naughty list written.")
    else:
        print("'{}' is not a command. use 'help' to display all commands.".format(command))
       
"""elif command == "add":
        cmdadd("normal")
    elif command == "add -r":
        cmdadd("rename")"""