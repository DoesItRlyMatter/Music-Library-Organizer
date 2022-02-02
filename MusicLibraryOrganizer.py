# Rename by tags redone.

# Imports
import pathlib
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkf
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3
import threading
import time
import string

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

    def removeIllegal(self):
        # Trans table...i dunno, still cant be arsed to read documentation
        remove = r'"\/:?*<>|'
        # Remove remove illegal
        # Tracknumber
        table = self.tracknumber.maketrans('', '', remove)
        self.tracknumber = self.tracknumber.translate(table)
        # Artist
        table = self.artist.maketrans('', '', remove)
        self.artist = self.artist.translate(table)
        # Album
        table = self.album.maketrans('', '', remove)
        self.album = self.album.translate(table)
        # Title
        table = self.title.maketrans('', '', remove)
        self.title = self.title.translate(table)

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

    def formatTracknumber(self):
        if len(self.tracknumber) < 2:
            self.tracknumber = '0' + self.tracknumber
        # IF TRACKNUMBERING SCUFFS, THIS IS PROBLEM! MAKE LOOP
        if len(self.tracknumber) > 2:
            self.tracknumber = self.tracknumber.lstrip('0')

    def formatRestMeta(self, format):
        if '{artist}' in format:
            self.artist = string.capwords(self.artist)
        if '{album}' in format:
            self.album = string.capwords(self.album)
            try:
                index = self.album.index('[')
                self.album = self.album[:index+1] + self.album[index+1].upper() + self.album[index+2:]
            except ValueError:
                pass
            try:
                index = self.album.index('(')
                self.album = self.album[:index+1] + self.album[index+1].upper() + self.album[index+2:]
            except ValueError:
                pass
        if '{title}' in format:
            self.title = string.capwords(self.title)
            try:
                index = self.title.index('[')
                self.title = self.title[:index+1] + self.title[index+1].upper() + self.title[index+2:]
            except ValueError:
                pass
            try:
                index = self.title.index('(')
                self.title = self.title[:index+1] + self.title[index+1].upper() + self.title[index+2:]
            except ValueError:
                pass


# Renaming
def renameFiles():
    # Iterate through all the tracks (objects)
    for track in trackList:
        # formatMetadata(track, entryFormat.get())
        # Format tracknumbers
        track.formatTracknumber()
        # Format rest of metadata
        track.formatRestMeta(entryFormat.get())
        # Remove illegal symbols from tracknumber, artist, album and title
        track.removeIllegal()
        # Create the filename
        filename = track.createNewFilename(userSeparator.get(), entryFormat.get())
        print(filename)


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
    statusText.set(' Adding files...')
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
                programOutput('  ' + str(path), 'added')
            except KeyError:
                # add to error and skipped counters
                errors += 1
                skipped += 1
                programOutput('  ' + str(path) + ' - Error: Failed to Add. Missing metadata?', 'error')
        # If ext is .mp3
        elif ext == supportedFiletypes[1]:
            # same as flac section, check comments there.
            metadata = MP3(path)
            try:
                trackList.append(Track(path, ext, metadata['title'][0], metadata['tracknumber'][0], metadata['artist'][0], metadata['album'][0]))
                # add to added counter.
                added += 1
                programOutput('  ' + str(path), 'added')
            except KeyError:
                # add to error and skipped counters.
                errors += 1
                skipped += 1
                programOutput('  ' + str(path) + ' - Error: Failed to Add. Missing metadata?', 'error')
        else:
            # Check if path is a folder
            if os.path.isdir(path) is True:
                # add to folder counter, remove one from file counter.
                folders += 1
                files -= 1
                programOutput(str(path), 'folder')
            else:
                skipped += 1
                programOutput('  ' + str(path), 'skipped')
    # End time.
    endTime = time.perf_counter()
    # Update status text
    # ADD STATISTICS HERE LATER (RUNTIME, FOLDERS, ADDED FILES, SKIPPED FILES)
    statusText.set(f' Folders: {folders}  Files: {files}  Added: {added}  Skipped: {skipped}  Errors: {errors}  Time: {endTime - startTime:0.2f}s')
    # Check if tracklist has items
    if not len(trackList) == 0:
        btnRename.configure(state="normal")


# Insert text into program window.
def programOutput(text, tags=None):
    textbox.configure(state="normal")
    textbox.insert(tk.END, ' ' + text + '\n', tags)
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
        firstIteration = True
        for i in checkBoxStates:
            if i.value.get() is True:
                # Only do this on first iteration.
                if firstIteration is True:
                    # call addToDynVar to add value of checked checkbox.
                    dynVarStr = addToDynVar(i.id, '')
                    # Var false, we dont want this to run multiple times.
                    firstIteration = False
                # do this on the other iterations.
                else:
                    dynVarStr += sepa
                    dynVarStr = addToDynVar(i.id, dynVarStr)
        # dynVarStr = ''
        # Make var true again else it wont work correctly next time function is called.
        firstIteration = True
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

# Fonts
fontBold = tkf.Font(family='Arial', size=10, weight='bold')
fontNormal = tkf.Font(family='Arial', size=10, weight='normal')

# Create & Configure frames
statusText = tk.StringVar()
statusbar = tk.Label(root, textvariable=statusText, font=fontNormal, bd=1, relief=tk.SUNKEN, anchor=tk.W)
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
txtField = tk.Entry(topFrame, font=fontNormal, textvariable=folderPath)
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

incLabel = tk.Label(sideFrame, text="Include", font=fontBold)
incLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox1 = tk.Checkbutton(sideFrame, text="Tracknumber", font=fontNormal, variable=chkVarNum,
                           command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox1.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox2 = tk.Checkbutton(sideFrame, text="Artist", font=fontNormal, variable=chkVarArt,
                           command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox2.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox3 = tk.Checkbutton(sideFrame, text="Album", font=fontNormal, variable=chkVarAlb,
                           command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox3.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkBox4 = tk.Checkbutton(sideFrame, text="Title", font=fontNormal, variable=chkVarTit,
                           command=lambda: [toggleFormat(), dynamicFormatString(userSeparator.get())])
checkBox4.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Language checkboxes
langLabel = ttk.Label(sideFrame, text="Language", font=fontBold)
langLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkVarLANG = tk.IntVar()
checkBoxLANG = tk.Checkbutton(sideFrame, text="Romanji", font=fontNormal, variable=checkVarLANG, state=tk.DISABLED)
checkBoxLANG.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Extra function checkboxes
extraLabel = ttk.Label(sideFrame, text="Extra", font=fontBold)
extraLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkVar5 = tk.IntVar()
checkBox5 = tk.Checkbutton(sideFrame, text="Fix Title", font=fontNormal, variable=checkVar5)
checkBox5.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Scan folders and add files.
btnRun = ttk.Button(topFrame, text="Add", command=lambda: threading.Thread(target=addFiles).start(), state="disabled")
btnRun.pack(side=tk.LEFT, padx=(2, 1))

# Rename added files.
btnRename = ttk.Button(topFrame, text="Rename", command=renameFiles, state="disabled")
btnRename.pack(side=tk.LEFT, padx=(2, 1))

# Free naming format
entryFormat = tk.StringVar(root, value='{tracknumber} - {artist} - {album} - {title}')
renameFormat = tk.Entry(middleFrame, textvariable=entryFormat, font=fontNormal,)
renameFormat.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES, padx=(0, 0), pady=(0, 2))

# Separator entry
userSeparator = tk.StringVar(root, value=' - ')
separatorEntry = tk.Entry(middleFrame, textvariable=userSeparator, font=fontNormal, width=3, justify=tk.CENTER)
separatorEntry.pack(side=tk.LEFT, expand=tk.NO, padx=(0, 5), pady=(0, 2))


# Update renameFormat when separator is changed.
userSeparator.trace_add("write", updateSeparator)

# check if anything written in entry box.
folderPath.trace_add("write", toggleState)

# textbox
textbox = tk.Text(bottomFrame, state="disabled")
textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=(0, 0))

# Textbox tags
textbox.tag_configure('folder', foreground='black', font=fontBold)
textbox.tag_configure('error', foreground='red', font=fontNormal)
textbox.tag_configure('skipped', foreground='grey', font=fontNormal)
textbox.tag_configure('added', foreground='green', font=fontNormal)

# Mainloop
root.mainloop()
