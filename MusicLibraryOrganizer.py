# Rename by tags redone.

# Imports
import pathlib
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import string
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3

# Global variables
supportedFiletypes = [".flac", ".mp3"]
trackList = []


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
        print(track.track_num[0])
        print(track.artist[0])
        print(track.title[0])
        print(track.album[0])


# Create the filename
def create_filename():
    # Create string based on checkbox values.


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def runProgram():
    # Get current directory
    current_dir = pathlib.Path(folderPath.get())

    # Run the program
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
            # Just print something to visually show somethings happening. can be removed.
            print('FLAC item added!')
        # If ext is .mp3
        elif ext == supportedFiletypes[1]:
            # same as flac section, check comments there.
            metadata = MP3(path)
            trackList.append(Track(path, ext, metadata['title'], metadata['tracknumber'], metadata['artist'], metadata['album']))
            print('MP3 item added!')

    # Testing states of checkboxes, can be removed.
    if checkVarNUM.get() == 1:
        print('NUMBER CHECKED!')
    if checkVarART.get() == 1:
        print('ARTIST CHECKED!')
    if checkVarTIT.get() == 1:
        print('TITLE CHECKED!')


def toggle_state(*_):
    if os.path.isdir(folderPath.get()):
        btnRun.config(state="normal")
    else:
        btnRun.config(state="disabled")


# Create & Configure root
root = Tk()
root.geometry("650x400")
# window title.
root.title("Music Library Organizer")

# Create & Configure frames
sideFrame = Frame(root)
sideFrame.pack(side=LEFT, fill=BOTH)

topFrame = Frame(root)
topFrame.pack(side=TOP, fill=X, padx=(4, 2), pady=(2, 2))
#
bottomFrame = Frame(root)
bottomFrame.pack(side=TOP, fill=BOTH, expand=YES, padx=(4, 4), pady=(0, 4))

folderPath = StringVar()
txtField = Entry(topFrame, textvariable=folderPath)
txtField.pack(side=LEFT, fill=X, expand=YES, padx=(0, 0), pady=(0, 0))

# Browse button.
btnBrowse = ttk.Button(topFrame, text="Browse", command=getFolderPath)
btnBrowse.pack(side=LEFT, padx=(2, 0))

# Include checkboxes
checkVarNUM = IntVar()
checkVarART = IntVar()
checkVarTIT = IntVar()

incLabel = Label(sideFrame, text="Include", font="Arial 10 bold")
incLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox1 = Checkbutton(sideFrame, text="Track Num", variable=checkVarNUM)
checkBox1.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox2 = Checkbutton(sideFrame, text="Artist", variable=checkVarART)
checkBox2.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox3 = Checkbutton(sideFrame, text="Title", variable=checkVarTIT)
checkBox3.pack(anchor=W, side=TOP, padx=(0, 0))

# Language checkboxes
langLabel = Label(sideFrame, text="Language", font="Arial 10 bold")
langLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkVarLANG = IntVar()
checkBoxLANG = Checkbutton(sideFrame, text="Romanji", variable=checkVarLANG, state=DISABLED)
checkBoxLANG.pack(anchor=W, side=TOP, padx=(0, 0))

# Extra function checkboxes
extraLabel = Label(sideFrame, text="Extra", font="Arial 10 bold")
extraLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkVar5 = IntVar()
checkBox5 = Checkbutton(sideFrame, text="Cleanup Title", variable=checkVar5)
checkBox5.pack(anchor=W, side=TOP, padx=(0, 0))

# Click and run program.
btnRun = ttk.Button(topFrame, text="Run", command=runProgram, state="disabled")
btnRun.pack(side=LEFT, padx=(2, 1))

# Temporary buttons for testing
btnTest = ttk.Button(topFrame, text="Test", command=placeholder)
btnTest.pack(side=LEFT, padx=(2, 1))

# check if anything written in entry box.
folderPath.trace_add("write", toggle_state)

# textbox
textbox = Text(bottomFrame, state="disabled")
textbox.pack(side=TOP, fill=BOTH, expand=YES, padx=(0, 0))


# Mainloop
root.mainloop()
