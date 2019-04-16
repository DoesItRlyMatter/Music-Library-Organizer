# Created by Anton Kerke
# Last updated 13/4/19
# Version 1.0

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3 as MP3
import pathlib
import csv
import datetime
import os
import string

# global variables.
old_titles = []
new_titles = []

# Create & Configure root
root = Tk()
root.geometry("650x400")
# window title.
root.title("Rename By Tracknumber & Title")

# Create & Configure frames
topFrame = Frame(root)
topFrame.pack(side=TOP, fill=X, padx=(4, 2), pady=(2, 2))
#
bottomFrame = Frame(root)
bottomFrame.pack(side=TOP, fill=BOTH, expand=YES, padx=(4, 4), pady=(0, 4))


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def renameFiles():
    # variables.
    supported_filetypes = [".flac", ".mp3"]
    # original file data.
    og_file_info = []
    err_count = 0
    rename_count = 0
    # dict for storing old & new filenames
    global old_titles
    global new_titles
    current_dir = pathlib.Path(folderPath.get())
    # run rename
    for path in sorted(current_dir.rglob("*")):
        flag = 0
        og_file_info = get_ext(path.name)
        # check if one of supported filetypes / this step is probly not needed in this version
        if og_file_info[1] in supported_filetypes:
            # get metadata.
            if og_file_info[0] == "vorbis":
                try:
                    ret_tags = get_vorbis(path, "tracknumber", "title")
                except:
                    # print(" " + colored(path.name, "red", attrs=["bold"]) + " Error: File could not be renamed, check title & tracknumber.")
                    # textbox.insert(INSERT, path.name[:50].ljust(50) + " - Failed \n")
                    insText(path.name[:50].ljust(50) + " - Failed")
                    old_titles.append(path.name)
                    new_titles.append(
                        "Error: File could not be renamed, check title & tracknumber.")
                    flag += 1
                    err_count += 1
            elif og_file_info[0] == "ID3":
                try:
                    ret_tags = get_id3(path, "tracknumber", "title")
                except:
                    # print(" " + colored(path.name, "red", attrs=["bold"]) + " Error: File could not be renamed, check title & tracknumber.")
                    # textbox.insert(INSERT, path.name[:50].ljust(50) + " - Failed \n")
                    insText(path.name[:50].ljust(50) + " - Failed")
                    old_titles.append(path.name)
                    new_titles.append("Error: File could not be renamed, check title & tracknumber.")
                    flag += 1
                    err_count += 1
                # if data retrieved successfully.
            if flag == 0:
                rename_count += 1
                filename_str = " - ".join(ret_tags)
                # clean up formatting, add ext & rename.
                filename_str = cleanup(filename_str)
                filename_str += og_file_info[1]
                path.rename(pathlib.Path(path.parent, filename_str))
                # print old & new name.
                # print(" " + path.name[:50].ljust(50) + colored("   -->   ", "green") + filename_str[:50].ljust(50))
                # PRINT CHANGES HERE!!
                insText(filename_str[:70].ljust(70) + " - Done")
                # add old/new names to arrays
                old_titles.append(path.name)
                new_titles.append(filename_str)
        # update textbox.
        bottomFrame.update()
    # enable csv button.
    btnCsv.config(state="normal")


# return files metadata type and extension.
def get_ext(f_name):
    r_ext = []
    if f_name.endswith(".flac"):
        r_ext.append("vorbis")
        r_ext.append(".flac")
        return r_ext
    elif f_name.endswith(".ogg"):
        r_ext.append("vorbis")
        r_ext.append(".ogg")
        return r_ext
    elif f_name.endswith(".mp3"):
        r_ext.append("ID3")
        r_ext.append(".mp3")
        return r_ext
    else:
        r_ext.append("None")
        r_ext.append("None")
        return r_ext


# return vorbis data from flac files (tracknumber, title)
def get_vorbis(f_path, f_num, f_title):
    r_data = []
    data = FLAC(f_path)
    r_data.extend(data[f_num])
    r_data.extend(data[f_title])
    return r_data


# return id3 data from mp3 files (tracknumber, title)
def get_id3(f_path, f_num, f_title):
    r_data = []
    data = MP3(f_path)
    r_data.extend(data[f_num])
    r_data.extend(data[f_title])
    return r_data


# clean up string, mostly numbering
def cleanup(f_fn):
    # trans table stuff, couldnt be arsed to read documentation properly but it works.
    inp = ""
    out = ""
    remove = r'"\/:?*<>|'
    # remove forbidden characters
    table = f_fn.maketrans(inp, out, remove)
    f_fn = f_fn.translate(table)
    # correct numbering
    f_fn = f_fn.lstrip("0")
    # capitalize first char in each word.
    f_fn = string.capwords(f_fn)
    if f_fn[0].isdigit() and f_fn[1].isdigit():
        return f_fn
    else:
        f_fn = "0" + f_fn
        return f_fn


def makeCsv():
    # date variables
    try:
        now = datetime.datetime.now()
        with open("placeholder.csv", "w", newline="", encoding="utf-8") as f:
            headers = ["Old Filename", "New Filename"]
            thewriter = csv.DictWriter(f, fieldnames=headers)
            thewriter.writeheader()
            if len(old_titles) == len(new_titles):
                for i, items in enumerate(old_titles):
                    thewriter.writerow({"Old Filename": old_titles[i], "New Filename": new_titles[i]})
        # rename created file.
        csv_filename = "rename-info-" + str(now)[:16] + ".csv"
        csv_filename = csv_filename.replace(" ", "-").replace(":", "")
        os.rename("placeholder.csv", csv_filename)
        insText(csv_filename)
    except:
        insText("Failed to generate csv file.")
    btnCsv.config(state="disabled")


def insText(text):
    textbox.configure(state="normal")
    textbox.insert(END, " " + text + "\n")
    textbox.yview(END)
    textbox.configure(state="disabled")


def toggle_state(*_):
    if folderPath.get():
        btnRename.config(state="normal")
    else:
        btnRename.config(state="disabled")


def typeWarningsAndCredits():
    textbox.configure(state="normal")
    # INSERTS HERE!
    textbox.configure(state="disabled")


# Folder field, updates automatically.
folderPath = StringVar()
txtField = Entry(topFrame, textvariable=folderPath)
txtField.pack(side=LEFT, fill=X, expand=YES)

# Browse button.
btnBrowse = ttk.Button(topFrame, text="Browse", command=getFolderPath)
btnBrowse.pack(side=LEFT, padx=(2, 0))

# Click and run program.
btnRename = ttk.Button(topFrame, text="Rename", command=renameFiles, state="disabled")
btnRename.pack(side=LEFT, padx=(2, 0))

# check if anything written in entry box.
folderPath.trace_add("write", toggle_state)

# csv button, Greyed out until program has finished running.
btnCsv = ttk.Button(topFrame, text="Save Csv", command=makeCsv, state=DISABLED)
btnCsv.pack(side=LEFT, padx=(2, 1))

# textbox
textbox = Text(bottomFrame, state="disabled")
textbox.pack(side=LEFT, fill=BOTH, expand=YES)

# mainloop
root.mainloop()
