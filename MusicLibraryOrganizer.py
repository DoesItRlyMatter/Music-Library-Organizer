# Rename by tags redone.

# Imports
import pathlib
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import string

# Global variables
supportedFiletypes = [".flac", ".mp3"]
trackList = []


class Track:

    def __init__(self, path, ext, title, track_num, artist):
        self.path = path
        self.ext = ext
        self.title = title
        self.track_num = track_num
        self.artist = artist


def placeholder():
    print("Hello World!")


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def runProgram():
    # Counting vars
    flac = 0
    mp3 = 0
    # Get current directory
    current_dir = pathlib.Path(folderPath.get())

    # Run the program
    for path in sorted(current_dir.rglob("*")):
        # print(pathlib.Path(path).suffix)
        ext = pathlib.Path(path).suffix
        # Check if ext is .flac [0] or .mp3 [1]
        if ext == supportedFiletypes[0]:

            # count flacs
            flac += 1
        elif ext == supportedFiletypes[1]:
            # count mp3s
            mp3 += 1

    print(flac)
    print(mp3)


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
checkVar1 = IntVar()
checkVar2 = IntVar()
checkVar3 = IntVar()

incLabel = Label(sideFrame, text="Include", font="Arial 10 bold")
incLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox1 = Checkbutton(sideFrame, text="Track Num", variable=checkVar1)
checkBox1.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox2 = Checkbutton(sideFrame, text="Artist", variable=checkVar2)
checkBox2.pack(anchor=W, side=TOP, padx=(0, 0))

checkBox3 = Checkbutton(sideFrame, text="Title", variable=checkVar3)
checkBox3.pack(anchor=W, side=TOP, padx=(0, 0))

# Language checkboxes
langLabel = Label(sideFrame, text="Language", font="Arial 10 bold")
langLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkVar4 = IntVar()
checkBox4 = Checkbutton(sideFrame, text="Romanji", variable=checkVar4)
checkBox4.pack(anchor=W, side=TOP, padx=(0, 0))

# Extra function checkboxes
extraLabel = Label(sideFrame, text="Extra", font="Arial 10 bold")
extraLabel.pack(anchor=W, side=TOP, padx=(0, 0))

checkVar5 = IntVar()
checkBox5 = Checkbutton(sideFrame, text="Cleanup Title", variable=checkVar5)
checkBox5.pack(anchor=W, side=TOP, padx=(0, 0))

# Click and run program.
btnRun = ttk.Button(topFrame, text="Run", command=runProgram, state="disabled")
btnRun.pack(side=LEFT, padx=(2, 1))

# check if anything written in entry box.
folderPath.trace_add("write", toggle_state)

# textbox
textbox = Text(bottomFrame, state="disabled")
textbox.pack(side=TOP, fill=BOTH, expand=YES, padx=(0, 0))


# Mainloop
root.mainloop()
