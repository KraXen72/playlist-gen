import os
import pathlib
import codecs
from prompt_toolkit.completion import WordCompleter, FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.validation import Validator, ValidationError

exts = ["mp3"] #extensions to consider as valid
ign = [] #folder names to ignore

def generatem3u(currpath, returnInsteadOfWriting, includePlaylists): #main generation function - if ret = true then don't write file, only return an array
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
            music.append(song)
    if str(name) in ign: #ingore if on the ignore list
        print("ignoring folder " + name)
    else:
        if music.__len__() > 0: #write mp3 songs to file or return array
            if returnInsteadOfWriting == True:
                return music
            else:
                f = codecs.open(currpath + "\\" + name+".m3u", "w", "utf-8")
                aaa = "\n".join(music)
                f.write(aaa)
                f.close()
                print("generated {}.m3u".format(name))
                music.clear()
                listOfFiles.clear()
        else: #if no valid songs just skip
            print("no mp3 files found for "+ name)

def init(): #main generation init function
    # get the current path using pathlib
    currpath = str(pathlib.Path(__file__).parent.absolute())
    
    #get all subdirectories - x is an array which contains the path as first, and the files as the rest of the array, we only need the path
    dirs = [str(x[0]) for x in os.walk(currpath)] 

    for dir in dirs: #generate for every subdirectory
        generatem3u(dir, False, False)

currpath = str(pathlib.Path(__file__).parent.absolute())
print("welcome to playlist generator.")
print("----------")
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
    elif command == 'exit' or command == "quit":
        quit()
    elif command == 'gen':
        print("generating for all subfolders..")
        init()
        print("done. ")
    elif command == "ext":
        print("---------- ext")
        print("enter the music extensions you use. lowercase. \n if there are more, separate them by , \n example: mp3,flac,ogg \n example2: ogg")
        exts = input(': ').split(",")
        print("set extensions to: ")
        print(exts)
    elif command == "ign":
        print("---------- ign")
        print("enter the folder names to ignore. case sensitive. \n if there are more, separate them by , \n example: trash,archive,onHold \n example2:  (empty to not ignore anything)")
        ign = input(': ').split(",")
        print("also ignore subfolders of these? (y/n)")
        ignsubs = input(': ')
        if ignsubs == "y":
            origign = ign
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
        else:
            print("ignoring folders: (subfolders are not ignored)")
            print(ign)
        f = codecs.open("gen-ignorelist.txt", "w", "utf-8")
        f.write("\n".join(ign))
        f.close()
        print("disclaimer: if a folder matches the name in the ignored list, it will be ignored.")
    elif command == "prg":
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
    elif command == "com":
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
                        newlines.append(p + "\\" + line)
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
    elif command == "add" or command == "add -r":
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
            append = ""
            for folder in folders:
                f = codecs.open("{}\\{}\\{}.m3u".format(currpath, folder, folder), "r", "utf-8")
                tempcontents = f.read()
                lines = tempcontents.split("\n")
                newlines = []
                for line in lines:
                    newlines.append(folder + "\\" + line)
                append += "\n".join(newlines)
                f.close()
            f = codecs.open(currpath + "\\" + playlist, "a", "utf-8")
            f.write(append)
            f.close()
            print("-----------")
            print("added folders:")
            print(folders)
            print("to playlist '{}'".format(playlist))
            if command == "add -r":
                propsedname = playlist[0:-4] + " + " + " + ".join(folders) + ".m3u"
                if propsedname.__len__() > 100:
                    newplaylist = propsedname[:89] + ".. and more"
                else:
                    newplaylist = propsedname
                os.rename(currpath + "\\" + playlist, newplaylist)
                print("and renamed '{}' to '{}'".format(playlist, newplaylist))
        else:
            print(playlist + " does not exist.")
    elif command == "new":
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

                    f = codecs.open(currpath + "\\" + song, "r", "utf-8")
                    tempcontents = f.read()
                    lines = tempcontents.split("\n")
                    f.close()
                    for line in lines:
                        playlist.append(songParent + "\\" + line)
                else: #add the song to the playlist
                    playlist.append(song)
            else: #pasue the process
                print("---------- {}.m3u ----------".format(name))
                print(playlist)
                print("----------")
                print("add more? (a) save to file? (s) cancel? (c)")
                decision = input(": ")

                if decision == "a": #add more
                    # just continue ig
                    done = False
                elif decision == "s": #save
                    done = True
                    save = True
                elif decision == "c": #cancel
                    done = True
                    save = False

        if save == True:
            f = codecs.open(currpath + "\\" + name + ".m3u", "w", "utf-8")
            f.write("\n".join(playlist))
            f.close()

            print("sucessfully made playlist {}.m3u".format(name))
        elif save == False:
            print("creating playlist was cancelled, notihing saved.")
    else:
        print("'{}' is not a command. use 'help' to display all commands.".format(command))
       
