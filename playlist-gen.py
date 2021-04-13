import os
import pathlib
import codecs
import mutagen
from decimal import *
from prompt_toolkit.completion import WordCompleter, FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.validation import Validator, ValidationError

global exts
global useEXTINF
useEXTINF = True
exts = ["mp3"] #extensions to consider as valid
ign = [] #folder names to ignore

#functions

#get info about a song
def getSongInfo(song, currpath):
    if currpath != "": #if currpath is empty, then just put the song by itself
        currpath += "\\"
    info = mutagen.File(currpath + song)
    output = info
    title = ""
    artist = ""

    try:
        artist = output.tags["TPE1"].text[0]
    except:
        artist = "Unknown Artist"

    try:
        title = output.tags["TIT2"].text[0]
    except: 
        title = "Unknown Title"
    
    myinfo = {
        "ttitle": title,
        "tartist": artist,
        "tlength": str(Decimal(output.info.length).quantize(Decimal('0.001'), ROUND_HALF_UP)).replace(".","") # round to 3 decimal spaces and replace the dot with nothing
    }
    extinfo = "#EXTINF:{},{} - {}".format(myinfo["tlength"], myinfo["tartist"], myinfo["ttitle"])
    return extinfo

# generate a playlist for given path
# arguments:
# currpath (str) - the path to generate
# returnInsteadOfWriting (bool) - return an array of the songs instead of making a file
# includePlaylists (bool) - include .m3u playlists as songs
def generatem3u(currpath, returnInsteadOfWriting, includePlaylists): 
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
        if includePlaylists == True:
            myexts.append('m3u')

        if str(ext).lower() in myexts:
            if useEXTINF == True:
                music.append(getSongInfo(song, currpath))
            music.append(song)
    if str(name) in ign: #ingore if on the ignore list
        print("ignoring folder " + name)
    else:
        if music.__len__() > 0: #write mp3 songs to file or return array
            if returnInsteadOfWriting == True:
                return music
            else:
                if useEXTINF == True:
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
        generatem3u(dir, False, False)
    
    print("done. ")

#print help message
def cmdhelp():
    print("---------- help:")
    prn = [
        "---------- setup ----------",
        "'ext' - set the extensions of music files. default: mp3",
        "'ign' - set the folders to ignore in generation. none by default",
        "---------- actions ----------",
        "'gen' - recursively generate m3u playlists for all folders and subfolders",
        "'prg' - delete all existing .m3u files in the working directory for a clean slate",
        "'com' - generate a playlist from multiple specific folders",
        "'add' - add a folder or folders to a playlist made by 'com'. doesen't rename the playlist",
        "'add -r' - same thing as 'add' but appends the folder name to the playlist name. ",
        "'new' - manually make a new playlist by selecting songs and playlists",
        "---------- other ----------",
        "'help' - display this message",
        "'exit' or 'quit' - exit this utility"]
    print("\n".join(prn))

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

#make a playlist out of x folders
def cmdcom():
    print("---------- com")
    print("enter the names of top level folders you want to combine in a playlist separated by a , \n this will create a new playlist, not overwrite the original ones. \n example: grandson,oliver tree")
    plays = input(": ").split(",")
    if plays.__len__() > 1:
        currpath = str(pathlib.Path(__file__).parent.absolute())
        contents = ""
        for p in plays:
            if os.path.isdir(p):
                generatem3u(currpath + "\\" + p, False, False)

                f = codecs.open("{}\\{}\\{}.m3u".format(currpath, p, p), "r", "utf-8")
                tempcontents = f.read()
                lines = tempcontents.split("\n")
                newlines = []
                for line in lines:
                    if useEXTINF == True:
                        newlines.append(getSongInfo(line, p))
                    newlines.append(p + "\\" + line)
                if useEXTINF == True:
                    newlines.insert(0,'#EXTM3U')
                contents += "\n".join(newlines)
                f.close()
            else:
                print("'{}' is not a folder. skipping.".format(p))
        if contents != "":
            f = codecs.open(" + ".join(plays) + ".m3u", "w", "utf-8")
            f.write(contents)
            f.close()
            print("generated '{}.m3u'".format(" + ".join(plays)))
        else:
            print("no valid folders, nothing generated.")
    else:
        print("this requires at least 2 folders to combine")

#add x folders to an existing playlist
# parameters: mode (string) ["normal"|"rename"], rename appends the folders to the playlist name
def cmdadd(mode):
    print("---------- add")
    print("enter the name of the playlist you want add to \n example: grandson + oliver tree.m3u")
    playlist = input(": ")
    if os.path.isfile(currpath + "\\" + playlist):
        print("-----------")
        print("selected playlist '" + playlist + "'")
        print("enter the folder or folders to add to this playlist. if more, separate them by , \n example: grandson,oliver tree")
        folders = input(": ").split(",")

        f = codecs.open(currpath + "\\" + playlist, "r", "utf-8")
        bakcontents = f.read()
        f.close()
        append = "\n"
        for folder in folders:
            f = codecs.open("{}\\{}\\{}.m3u".format(currpath, folder, folder), "r", "utf-8")
            tempcontents = f.read()
            lines = tempcontents.split("\n")
            newlines = []
            for line in lines:
                if useEXTINF == True:
                    newlines.append(getSongInfo(line, folder))
                newlines.append(folder + "\\" + line)
            if useEXTINF == True:
                    newlines.insert(0,'#EXTM3U')
            append += "\n".join(newlines)
            f.close()
        f = codecs.open(currpath + "\\" + playlist, "a", "utf-8")
        f.write(append)
        f.close()
        print("-----------")
        print("added folders:")
        print(folders)
        print("to playlist '{}'".format(playlist))
        if mode == "rename":
            propsedname = playlist[0:-4] + " + " + " + ".join(folders) + ".m3u"
            if propsedname.__len__() > 100:
                newplaylist = propsedname[:89] + ".. and more"
            else:
                newplaylist = propsedname
            os.rename(currpath + "\\" + playlist, newplaylist)
            print("and renamed '{}' to '{}'".format(playlist, newplaylist))
    else:
        print(playlist + " does not exist.")

#create a new playlist by adding songs and playlists together
def cmdnew():
    print("---------- new")
    print("name your new playlist: ")
    name = input(": ")

    allsongs = generatem3u(currpath, True, True)

    #set up autocomplete
    class SongValidator(Validator): #autocomplete validator = check if song acutally exists
        def validate(self, document):
            text = document.text
            if text and text not in allsongs and text != "$playlist-done":
                raise ValidationError(message="this song doesen't exist", cursor_position=text.__len__())
    #set up completer
    done = False
    save = False
    song = ""
    playlist = []
    print("---------- new playlist: {}.m3u".format(name))
    print("search for a song or playlist you want to add (tab to show suggestions)")
    print("if you are done, just type '$playlist-done'")

    while done == False:
        availableSongs = [x for x in allsongs if x not in playlist] #only suggest songs not already in the playlist
        availableSongs.append("$playlist-done")
        song_completer = WordCompleter(availableSongs, ignore_case=True, sentence = True,match_middle=True)
        # autocomplete prompt
        song = prompt("-> ",completer=song_completer,validator=SongValidator(),complete_while_typing=True,validate_while_typing=False)

        if song != "$playlist-done":
            if ".m3u" in song: # if its a playlist add all its songs
                songParent = song.split("\\")[0] 
                # if we are adding a playlist in the same directory, the songparent will be the file itself, so in that case, don't add any parent dir to the song
                if ".m3u" in songParent and os.path.isfile(currpath + "\\" + songParent):
                    songParent = ""
                else:
                    #else append the parent Directory and a backslash to the song
                    songParent += "\\"

                # read the playlist file, get an array of all it's lines
                f = codecs.open(currpath + "\\" + song, "r", "utf-8")
                tempcontents = f.read()
                lines = tempcontents.split("\n")
                f.close()

                for line in lines:
                    if songParent + line not in playlist: #only add the song if it already isn't in the playlist, to avoid duplicates
                        if useEXTINF == True:
                            playlist.append(getSongInfo(line, songParent.replace("\\","")))
                        playlist.append(songParent + line)
            else: #add the song to the playlist
                if useEXTINF == True:
                    playlist.append(getSongInfo(song, ""))
                playlist.append(song)
        else: #pasue the process
            print("---------- {}.m3u ----------".format(name))
            print(playlist)
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
        f = codecs.open(currpath + "\\" + name + ".m3u", "w", "utf-8")
        if useEXTINF == True:
            playlist.insert(0,'#EXTM3U')
        f.write("\n".join(playlist))
        f.close()

        print("sucessfully made playlist {}.m3u".format(name))
    elif save == False:
        print("creating playlist was cancelled, notihing saved.")

currpath = str(pathlib.Path(__file__).parent.absolute())
print("welcome to playlist generator.")
print("----------")

#load the ignore list if it exists
if os.path.isfile(currpath + "\\gen-ignorelist.txt"):
    f = codecs.open(currpath + "\\gen-ignorelist.txt", "r", "utf-8")
    ign = f.read().split("\n")
    f.close()
    print("loaded ignore list from config. now it's:")
    print(ign)

while True: #main command loop
    print("----------")
    command = input('gen: what would you like to do? ("help" to list all commands): ')

    if command == 'help':
        cmdhelp()
    elif command == 'exit' or command == "quit":
        quit()
    elif command == 'gen':
        cmdgen()
    elif command == "ext":
        exts = cmdexts()
        print("set extensions to: ")
        print(exts)
    elif command == "ign":
        ign = cmdign()
        f = codecs.open("gen-ignorelist.txt", "w", "utf-8")
        f.write("\n".join(ign))
        f.close()
        print("disclaimer: if a folder matches the name in the ignored list, it will be ignored.")
    elif command == "prg":
        cmdprg()
    elif command == "com":
        cmdcom()
    elif command == "add":
        cmdadd("normal")
    elif command == "add -r":
        cmdadd("rename")
    elif command == "new":
        cmdnew()
    else:
        print("'{}' is not a command. use 'help' to display all commands.".format(command))
       
