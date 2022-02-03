# Rename by tags redone.

# Imports
import pathlib
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import Menu
import tkinter.font as tkf
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3
import threading
import time
import string

# INFO
author = 'DIRM'
version = '0.91'

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

    # Replaces tags with metadata, returns filename string
    def createNewFilename(self, format):
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

    # Make tracknumber 2 digits, remove starting zeros. Not foolproof.
    def formatTracknumber(self):
        loops = 0
        # Remove zeros if more than 2 digits, try 4 times.
        while (len(self.tracknumber) > 2 and loops < 4):
            self.tracknumber = self.tracknumber.lstrip('0')
            loops += 1
        # If less than 2 digits, add zero at start.
        if len(self.tracknumber) < 2:
            self.tracknumber = '0' + self.tracknumber

    # Format rest of metadata. All words start with caps etc.
    def formatRestMeta(self, format):
        if '{artist}' in format:
            self.artist = string.capwords(self.artist)
        if '{album}' in format:
            self.album = string.capwords(self.album)
            # Check if string contains [, capitalize the next letter.
            # Scuffs if there is multiple [... should check if theres multiple.
            try:
                index = self.album.index('[')
                self.album = self.album[:index+1] + self.album[index+1].upper() + self.album[index+2:]
            except ValueError:
                pass
            # Check if string contains (, capitalize the next letter.
            try:
                index = self.album.index('(')
                self.album = self.album[:index+1] + self.album[index+1].upper() + self.album[index+2:]
            except ValueError:
                pass
        if '{title}' in format:
            self.title = string.capwords(self.title)
            # Same as above
            try:
                index = self.title.index('[')
                self.title = self.title[:index+1] + self.title[index+1].upper() + self.title[index+2:]
            except ValueError:
                pass
            # Same as above
            try:
                index = self.title.index('(')
                self.title = self.title[:index+1] + self.title[index+1].upper() + self.title[index+2:]
            except ValueError:
                pass


# Renaming
def renameFiles():
    # Start time
    startTime = time.perf_counter()
    # Update statusbar
    statusText.set(' Renaming files...')
    # Rename counter
    filesRenamed = 0
    # Iterate through all the tracks (objects)
    for track in trackList:
        # Format tracknumbers
        track.formatTracknumber()
        # Format rest of metadata
        track.formatRestMeta(entryFormat.get())
        # Remove illegal symbols from tracknumber, artist, album and title
        track.removeIllegal()
        # Create the filename
        filename = track.createNewFilename(entryFormat.get())
        # Add ext to filename
        filename = filename + track.ext
        # Output
        programOutput(filename, 'added')
        # Rename // This rename line is confusing.
        track.path.rename(pathlib.Path(track.path.parent, filename))
        # Replace old path with new path.
        track.path = pathlib.Path(track.path.parent, filename)
        filesRenamed += 1
    # Check state of clear checkbox
    if checkVarClear.get() == 1:
        # clear all items from tracklist
        clearTracklist()
    # End time.
    endTime = time.perf_counter()
    # Update statusbar
    statusText.set(f' {filesRenamed} files renamed in {endTime - startTime:0.2f}s')


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


# Add
def addFiles():
    # Counters
    folders, files, added, skipped, errors = 0, 0, 0, 0, 0
    # Start time.
    startTime = time.perf_counter()
    # Update statusbar
    statusText.set(' Adding files...')
    # Get current directory
    current_dir = pathlib.Path(folderPath.get())
    # Run the program. Create Track obj for every .flac/.mp3 file.
    for path in sorted(current_dir.rglob("*")):
        files += 1
        ext = pathlib.Path(path).suffix
        # Check if ext is .flac [0] or .mp3 [1]
        if ext == supportedFiletypes[0]:
            # get files metadata
            metadata = FLAC(path)
            # Append objects with metadata to tracklist. metadata['xx']
            try:
                trackList.append(Track(path, ext, metadata['title'][0], metadata['tracknumber'][0], metadata['artist'][0], metadata['album'][0]))
                added += 1
                # Output GREEN
                programOutput('  ' + str(path), 'added')
            except KeyError:
                errors += 1
                skipped += 1
                # Output RED
                programOutput('  ' + str(path) + ' - Error: Failed to Add. Missing metadata?', 'error')
        elif ext == supportedFiletypes[1]:
            metadata = MP3(path)
            try:
                trackList.append(Track(path, ext, metadata['title'][0], metadata['tracknumber'][0], metadata['artist'][0], metadata['album'][0]))
                added += 1
                programOutput('  ' + str(path), 'added')
            except KeyError:
                errors += 1
                skipped += 1
                programOutput('  ' + str(path) + ' - Error: Failed to Add. Missing metadata?', 'error')
        else:
            # Check if path is a folder
            if os.path.isdir(path) is True:
                # add to folder counter, remove one from file counter.
                folders += 1
                files -= 1
                # Output BLACK
                programOutput(str(path), 'folder')
            else:
                skipped += 1
                # Output GREY
                programOutput('  ' + str(path), 'skipped')
    # End time.
    endTime = time.perf_counter()
    # Update statusbar
    statusText.set(f' Folders: {folders}  Files: {files}  Added: {added}  Skipped: {skipped}  Errors: {errors}  Time: {endTime - startTime:0.2f}s')
    # Normalize rename button if tracklist contains items.
    if not len(trackList) == 0:
        btnRename.configure(state="normal")


# Insert text into program window.
def programOutput(text, tags=None):
    textbox.configure(state="normal")
    textbox.insert(tk.END, ' ' + text + '\n', tags)
    textbox.yview(tk.END)
    textbox.configure(state="disabled")


# Toggle Add button state. Check if folderpath is valid folder path.
def toggleState(*_):
    # Add state
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


def dynamicFormatString(sepa):
    # Check if any checkbox is ticked.
    if any(i.value.get() is True for i in checkBoxStates):
        firstIteration = True
        for i in checkBoxStates:
            if i.value.get() is True:
                # Only do this on first iteration.
                if firstIteration is True:
                    # call addToDynVar to add value of checked checkbox.
                    dynVarStr = addToDynVar(i.id, '')
                    firstIteration = False
                # Every other iteration
                else:
                    dynVarStr += sepa
                    dynVarStr = addToDynVar(i.id, dynVarStr)
        # Make var true again else it wont work correctly next time function is called.
        firstIteration = True
        # Set entry box text.
        entryFormat.set(dynVarStr)
    # Default text if no ticked checkbox
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
    dynamicFormatString(userSeparator.get())


# Clear tracklist and disable rename button
def clearTracklist():
    trackList.clear()
    btnRename.configure(state="disabled")


# Create & Configure root
root = tk.Tk()
# root.geometry("650x400")
root.geometry('1280x720')
# Window title and icon
root.title('Music Library Organizer v.' + version)
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

checkVarLANG1 = tk.IntVar()
checkBoxLANG1 = tk.Checkbutton(sideFrame, text="English", font=fontNormal, variable=checkVarLANG1, state=tk.DISABLED)
checkBoxLANG1.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))
checkVarLANG2 = tk.IntVar()
checkBoxLANG2 = tk.Checkbutton(sideFrame, text="Swedish", font=fontNormal, variable=checkVarLANG2, state=tk.DISABLED)
checkBoxLANG2.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))
checkVarLANG3 = tk.IntVar()
checkBoxLANG3 = tk.Checkbutton(sideFrame, text="Finnish", font=fontNormal, variable=checkVarLANG3, state=tk.DISABLED)
checkBoxLANG3.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))
checkVarLANG4 = tk.IntVar()
checkBoxLANG4 = tk.Checkbutton(sideFrame, text="Romanji", font=fontNormal, variable=checkVarLANG4, state=tk.DISABLED)
checkBoxLANG4.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Extra function checkboxes
extraLabel = ttk.Label(sideFrame, text="Metadata", font=fontBold)
extraLabel.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

checkVar5 = tk.IntVar()
checkBox5 = tk.Checkbutton(sideFrame, text="Title", font=fontNormal, variable=checkVar5, state='disabled')
checkBox5.pack(anchor=tk.W, side=tk.TOP, padx=(0, 0))

# Scan folders and add files.
btnRun = ttk.Button(topFrame, text="Add", command=lambda: threading.Thread(target=addFiles).start(), state="disabled")
btnRun.pack(side=tk.LEFT, padx=(2, 1))

# Rename added files.
btnRename = ttk.Button(topFrame, text="Rename", command=lambda: threading.Thread(target=renameFiles).start(), state="disabled")
btnRename.pack(side=tk.LEFT, padx=(2, 1))

# Clear checkbox
checkVarClear = tk.IntVar()
checkBoxClear = tk.Checkbutton(middleFrame, text="Clear list", font=fontNormal, variable=checkVarClear, state=tk.NORMAL)
checkBoxClear.pack(side=tk.RIGHT, padx=(0, 0))

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

# Create menu bar
menubar = Menu(root)
mlo = Menu(menubar, tearoff=0)
mlo.add_command(label='Browse', command=getFolderPath)
mlo.add_command(label='Add', command=lambda: threading.Thread(target=addFiles).start())
mlo.add_command(label='Rename', command=lambda: threading.Thread(target=renameFiles).start())
mlo.add_command(label='Clear Tracklist', command=lambda: clearTracklist())
mlo.add_separator()
mlo.add_command(label='Quit', command=root.quit)
menubar.add_cascade(label="Music Library Organizer", menu=mlo)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label='About', command=lambda: programOutput('\n  Music Library Organizer \n  Author: ' + author + ' \n  Version: ' + version + ' \n'))
helpmenu.add_command(label='Help', command=lambda: programOutput('\n  Checkboxes under Include are used to determine which fields to include in the filename. \n\n' +
                                                                 '  If no checkboxes are ticked a custom format can be specified in the right textbox. The following tags are available: \n\n' +
                                                                 '  {tracknumber}, {artist}, {album} and {title} \n\n' +
                                                                 '  A separator can be specified in the left textbox. The separator will be added between all tags. \n\n' +
                                                                 '  Langauge and Metadata functions currently not available.'))
menubar.add_cascade(label="Help", menu=helpmenu)

# Menu
root.config(menu=menubar)
# Mainloop
root.mainloop()
