# Rename by tags redone.

# Imports
import pathlib
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3

# Global variables
supportedFiletypes = [".flac", ".mp3"]
trackList = []
checkBoxStates = []


class chk:

    def __init__(self, id, value):
        self.id = id
        self.value = value


class Track:

    def __init__(self, path, ext, title, track_num, artist, album):
        self.path = path
        self.ext = ext
        self.title = title
        self.track_num = track_num
        self.artist = artist
        self.album = album


# Test function
def placeholder():
    # Iterate through all the tracks (objects)
    for track in trackList:
        # 0 to only get content.
        # print(track.track_num[0])
        # print(track.artist[0])
        # print(track.title[0])
        # print(track.album[0])
        createFilename(track)

    print(placeholderText.get())


# Create the filename
def createFilename(track):
    # Create string based on checkbox value or entry string.
    # Check which method to use.
    # if any checkbox checked, do this.
    if any(i.value.get() is True for i in checkBoxStates):
        # variable for storing string (title)
        # interate thought checkboxes, add whats checked.
        # Var for checking if its loops first iteration.
        firstTrue = True
        for j in checkBoxStates:
            if j.value.get() is True:
                # Only do this on first iteration.
                if firstTrue is True:
                    # call addToString to add value of checked checkbox.
                    titleStr = addToString(j.id, '')
                    # Var false, we dont want this to run multiple times.
                    firstTrue = False
                # do this on the other iterations.
                else:
                    titleStr += ' - '
                    titleStr = addToString(j.id, titleStr)
        print(titleStr)
        titleStr = ''
        # Make var true again else it wont work correctly next time function is called.
        firstTrue = True
    # else if no checkbox checked, do this.
    else:
        print('No checkboxes checked.')
        print('Functionality not implemented.')


# Add checked checkbox value to string.
def addToString(id, str):
    # if which ever value id matches to.
    if id == 'chkTracknumber':
        str = '00'
    if id == 'chkArtist':
        str += 'Artist'
    if id == 'chkAlbum':
        str += 'Album'
    if id == 'chkTitle':
        str += 'Title'
    return str


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def runProgram():
    # Get current directory
    current_dir = pathlib.Path(folderPath.get())
    # Run the program. Create Track obj for every .flac/.mp3 file.
    for path in sorted(current_dir.rglob("*")):
        # print(pathlib.Path(path).suffix)
        ext = pathlib.Path(path).suffix
        # Check if ext is .flac [0] or .mp3 [1]
        # If ext is .flac
        if ext == supportedFiletypes[0]:
            # get files metadata
            metadata = FLAC(path)
            # Append objects with metadata to tracklist.
            trackList.append(Track(path, ext, metadata['title'], metadata['tracknumber'], metadata['artist'], metadata['album']))
        # If ext is .mp3
        elif ext == supportedFiletypes[1]:
            # same as flac section, check comments there.
            metadata = MP3(path)
            trackList.append(Track(path, ext, metadata['title'], metadata['tracknumber'], metadata['artist'], metadata['album']))
        print('Item of class track created and added to list.')


# Toggle run button state. Check if folderpath is valid folder path.
def toggleState(*_):
    # run state
    if os.path.isdir(folderPath.get()):
        btnRun.config(state="normal")
    else:
        btnRun.config(state="disabled")


def toggleFormat():
    # Check if any of the checkboxes are checked. If one or more checked disable renameformat entry.
    if any(i.value.get() is True for i in checkBoxStates):
        renameFormat.config(state="disabled")
    else:
        renameFormat.config(state="normal")


# Create & Configure root
root = tk.Tk()
root.geometry("650x400")
# Window title and icon
root.title("Music Library Organizer")
root.iconbitmap(default="mlo_icon.ico")

# Create & Configure frames
sideFrame = tk.Frame(root)
sideFrame.pack(side=tk.LEFT, fill=tk.BOTH)

topFrame = tk.Frame(root)
topFrame.pack(side=tk.TOP, fill=tk.X, padx=(4, 2), pady=(2, 2))
#
bottomFrame = tk.Frame(root)
bottomFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=(4, 4), pady=(0, 4))

folderPath = tk.StringVar()
txtField = tk.Entry(topFrame, textvariable=folderPath)
txtField.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=(0, 0), pady=(0, 0))

# Browse button.
btnBrowse = ttk.Button(topFrame, text="Browse", command=getFolderPath)
btnBrowse.pack(side=tk.LEFT, padx=(2, 0))

# Include checkboxes
chkVarNum = tk.BooleanVar()
checkBoxStates.append(chk('chkTracknumber', chkVarNum))
chkVarArt = tk.BooleanVar()
checkBoxStates.append(chk('chkArtist', chkVarArt))
chkVarAlb = tk.BooleanVar()
checkBoxStates.append(chk('chkAlbum', chkVarAlb))
chkVarTit = tk.BooleanVar()
checkBoxStates.append(chk('chkTitle', chkVarTit))

incLabel = tk.Label(sideFrame, text="Include", font="Arial 10 bold")
incLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox1 = tk.Checkbutton(sideFrame, text="Tracknumber", variable=chkVarNum, command=lambda: toggleFormat())
checkBox1.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox2 = tk.Checkbutton(sideFrame, text="Artist", variable=chkVarArt, command=lambda: toggleFormat())
checkBox2.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox3 = tk.Checkbutton(sideFrame, text="Album", variable=chkVarAlb, command=lambda: toggleFormat())
checkBox3.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox4 = tk.Checkbutton(sideFrame, text="Title", variable=chkVarTit, command=lambda: toggleFormat())
checkBox4.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Language checkboxes
langLabel = ttk.Label(sideFrame, text="Language", font="Arial 10 bold")
langLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkVarLANG = tk.IntVar()
checkBoxLANG = tk.Checkbutton(sideFrame, text="Romanji", variable=checkVarLANG, state=tk.DISABLED)
checkBoxLANG.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Extra function checkboxes
extraLabel = ttk.Label(sideFrame, text="Extra", font="Arial 10 bold")
extraLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkVar5 = tk.IntVar()
checkBox5 = tk.Checkbutton(sideFrame, text="Fix Title", variable=checkVar5)
checkBox5.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Click and run program.
btnRun = ttk.Button(topFrame, text="Run", command=runProgram, state="disabled")
btnRun.pack(side=tk.LEFT, padx=(2, 1))

# Temporary buttons for testing
btnTest = ttk.Button(topFrame, text="Test", command=placeholder)
btnTest.pack(side=tk.LEFT, padx=(2, 1))

# Free naming format
placeholderText = tk.StringVar(root, value='{Tracknumber} - {Artist} - {Album} - {Title}')
renameFormat = tk.Entry(bottomFrame, textvariable=placeholderText)
renameFormat.pack(side=tk.TOP, fill=tk.X, expand=tk.NO, padx=(0, 0), pady=(0, 2))

# check if anything written in entry box.
folderPath.trace_add("write", toggleState)

# textbox
textbox = tk.Text(bottomFrame, state="disabled")
textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=(0, 0))


# Mainloop
root.mainloop()
