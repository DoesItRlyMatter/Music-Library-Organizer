# Rename by tags redone.

# Imports
import pathlib
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3
import threading
import time

# Global variables
supportedFiletypes = [".flac", ".mp3"]
trackList = []
checkBoxStates = []


class chk:

    def __init__(self, id, value):
        self.id = id
        self.value = value


class Track:

    def __init__(self, path, ext, title, tracknumber, artist, album):
        self.path = path
        self.ext = ext
        self.title = title
        self.tracknumber = tracknumber
        self.artist = artist
        self.album = album

    def formatMetadata(self):
        # Return formatted metadata.
        print('formatted metadata.')

    # Return new filename based on metadata. RETURNS FILENAME AS STRING
    def createNewFilename(self, separator, format):
        newFilename = format
        # Check if custom user format contains the replaceable strings
        if '{tracknumber}' in format:
            newFilename = newFilename.replace('{tracknumber}', self.tracknumber)
        if '{artist}' in format:
            newFilename = newFilename.replace('{artist}', self.artist)
        if '{album}' in format:
            newFilename = newFilename.replace('{album}', self.album)
        if '{title}' in format:
            newFilename = newFilename.replace('{title}', self.title)
        return newFilename


# Test function
def renameFiles():
    # Iterate through all the tracks (objects)
    for track in trackList:
        filename = track.createNewFilename(userSeparator.get(), entryFormat.get(), checkBoxStates)
        print(filename)


# do all title formatting here.
def formatTitle():
    print('Hello World!')


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


# ADD TRY CATCH TO APPEND, IT SOMETIMES FAILES AND THROWS ERROR!
def addFiles():
    # Counters
    folders, files, added, skipped, errors = 0, 0, 0, 0, 0
    # Start time.
    startTime = time.perf_counter()
    # Set status text
    statusText.set('Adding files...')
    # Get current directory
    current_dir = pathlib.Path(folderPath.get())
    # Run the program. Create Track obj for every .flac/.mp3 file.
    for path in sorted(current_dir.rglob("*")):
        # Add to file counter.
        files += 1
        # print(pathlib.Path(path).suffix)
        ext = pathlib.Path(path).suffix
        # Check if ext is .flac [0] or .mp3 [1]
        # If ext is .flac
        if ext == supportedFiletypes[0]:
            # get files metadata
            metadata = FLAC(path)
            # Append objects with metadata to tracklist. metadata['xx'] probably wrong. Make it only string.
            try:
                trackList.append(Track(path, ext, metadata['title'][0], metadata['tracknumber'][0], metadata['artist'][0], metadata['album'][0]))
                # add to added counter.
                added += 1
                programOutput(str(path) + '   --> Added')
            except KeyError:
                # add to error and skipped counters
                errors += 1
                skipped += 1
                programOutput(str(path) + '   --> ERROR: Failed to Add. Missing metadata?')
        # If ext is .mp3
        elif ext == supportedFiletypes[1]:
            # same as flac section, check comments there.
            metadata = MP3(path)
            try:
                trackList.append(Track(path, ext, metadata['title'][0], metadata['tracknumber'][0], metadata['artist'][0], metadata['album'][0]))
                # add to added counter.
                added += 1
                programOutput(str(path) + '   --> Added')
            except KeyError:
                # add to error and skipped counters.
                errors += 1
                skipped += 1
                programOutput(str(path) + '   --> ERROR: Failed to Add. Missing metadata?')
        else:
            # Check if path is a folder
            if os.path.isdir(path) is True:
                # add to folder counter, remove one from file counter.
                folders += 1
                files -= 1
                programOutput(str(path))
            else:
                skipped += 1
                programOutput(str(path) + '   --> Skipped')
    # End time.
    endTime = time.perf_counter()
    # Update status text
    # ADD STATISTICS HERE LATER (RUNTIME, FOLDERS, ADDED FILES, SKIPPED FILES)
    statusText.set(f'Folders: {folders}  Files: {files}  Added: {added}  Skipped: {skipped}  Errors: {errors}  Time: {endTime - startTime:0.2f}s')


# Insert text into program window.
def programOutput(text):
    textbox.configure(state="normal")
    textbox.insert(tk.END, " " + text + "\n")
    textbox.yview(tk.END)
    textbox.configure(state="disabled")


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


# Testing changing placeholder text.
# Write logic for this!
def dynamicFormatString(sepa):
    # iterate through checkboxes, add whats checked.
    # Var for checking if its loops first iteration.
    # Check so it doesnt throw variable reference error!
    if any(i.value.get() is True for i in checkBoxStates):
        firstTrue = True
        for i in checkBoxStates:
            if i.value.get() is True:
                # Only do this on first iteration.
                if firstTrue is True:
                    # call addToDynVar to add value of checked checkbox.
                    dynVarStr = addToDynVar(i.id, '')
                    # Var false, we dont want this to run multiple times.
                    firstTrue = False
                # do this on the other iterations.
                else:
                    dynVarStr += sepa
                    dynVarStr = addToDynVar(i.id, dynVarStr)
        # dynVarStr = ''
        # Make var true again else it wont work correctly next time function is called.
        firstTrue = True
        # Set entry box text.
        entryFormat.set(dynVarStr)
    # If no checkboxes checked, placeholdertext defaults to empty. Might Change to something else later.
    else:
        entryFormat.set('{tracknumber}' + sepa + '{artist}' + sepa + '{album}' + sepa + '{title}')


def addToDynVar(id, str):
    # if which ever value id matches to.
    if id == 'chkTracknumber':
        str = '{tracknumber}'
    if id == 'chkArtist':
        str += '{artist}'
    if id == 'chkAlbum':
        str += '{album}'
    if id == 'chkTitle':
        str += '{title}'
    return str


def updateSeparator(*_):
    # run state
    dynamicFormatString(userSeparator.get())


# Create & Configure root
root = tk.Tk()
# root.geometry("650x400")
root.geometry('1280x720')
# Window title and icon
root.title("Music Library Organizer")
root.iconbitmap(default="mlo_icon.ico")

# Create & Configure frames
statusText = tk.StringVar()
statusbar = tk.Label(root, textvariable=statusText, bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusbar.pack(side=tk.BOTTOM, fill=tk.X, padx=(4, 4), pady=(1, 4))

sideFrame = tk.Frame(root)
sideFrame.pack(side=tk.LEFT, fill=tk.BOTH)

topFrame = tk.Frame(root)
topFrame.pack(side=tk.TOP, fill=tk.X, padx=(4, 2), pady=(2, 2))

middleFrame = tk.Frame(root)
middleFrame.pack(side=tk.TOP, fill=tk.X, padx=(4, 4), pady=(0, 2))

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

checkBox1 = tk.Checkbutton(sideFrame, text="Tracknumber", variable=chkVarNum,
                           command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox1.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox2 = tk.Checkbutton(sideFrame, text="Artist", variable=chkVarArt, command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox2.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox3 = tk.Checkbutton(sideFrame, text="Album", variable=chkVarAlb, command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox3.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox4 = tk.Checkbutton(sideFrame, text="Title", variable=chkVarTit, command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
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

# Scan folders and add files.
btnRun = ttk.Button(topFrame, text="Add", command=lambda: threading.Thread(target=addFiles).start(), state="disabled")
btnRun.pack(side=tk.LEFT, padx=(2, 1))

# Rename added files.
btnTest = ttk.Button(topFrame, text="Rename", command=renameFiles)
btnTest.pack(side=tk.LEFT, padx=(2, 1))

# Free naming format
entryFormat = tk.StringVar(root, value='{tracknumber} - {artist} - {album} - {title}')
renameFormat = tk.Entry(middleFrame, textvariable=entryFormat)
renameFormat.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES, padx=(0, 0), pady=(0, 2))

# Separator entry
userSeparator = tk.StringVar(root, value=' - ')
separatorEntry = tk.Entry(middleFrame, textvariable=userSeparator, width=3, justify=tk.CENTER)
separatorEntry.pack(side=tk.LEFT, expand=tk.NO, padx=(0, 5), pady=(0, 2))


# Update renameFormat when separator is changed.
userSeparator.trace_add("write", updateSeparator)

# check if anything written in entry box.
folderPath.trace_add("write", toggleState)

# textbox
textbox = tk.Text(bottomFrame, state="disabled")
textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=(0, 0))

# Mainloop
root.mainloop()
