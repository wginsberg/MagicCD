#!/usr/bin/env python

import os
import sys
import shutil
import subprocess
import argparse

import evdev

DEFAULT_LIBRARY_PATH = os.path.join(os.environ["HOME"], ".rfid_library")

def rfid_readings():
    
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    device = devices[0]

    buffer_i = 0
    buffer_length = 18
    buffer = [0] * buffer_length 

    for event in device.read_loop():
            
        if event.type == 4:
            buffer[buffer_i] = str(event.value)
            buffer_i += 1

        if buffer_i == buffer_length:
            yield "".join(buffer)
            buffer_i = 0

def keyboard_readings(n=5):
    for _ in range(1, n):
        yield raw_input("DEBUG MODE: Enter by keyboard\n")

def init(path, debug=False, quiet=False):

    if os.path.exists(path):
        confirmation = raw_input("Library already exists. Overwrite? [y/n]\n")
        if confirmation == "y":
            shutil.rmtree(path)
        else:
            print "Aborting."
            return

    os.mkdir(path)
    print "Library initialized at {}".format(path)


def add_cwd_to_library(path, debug=False, quiet=False):

    print "Waiting for id ..."
    if debug:
        identifier = raw_input("DEBUG MODE: Enter by keyboard\n")
    else:
        identifier = next(rfid_readings())
        print identifier

    playlist_path = os.path.join(path, identifier)
    files = sorted([path for path in os.listdir(".") if not path.startswith(".")])
    playlist = "\n".join([os.path.join(os.getcwd(), _) for _ in  files])
    
    with open(playlist_path, "w") as f:
        f.write(playlist)

    print "Success"


def playback_loop(path, debug=False, quiet=False):
    """
    Runs an infinite loop to listen for readings and play corresponding media.
    Debug mode: Read a finite number of identifiers from stdin.
    """

    playing = None

    if debug:
        readings = keyboard_readings()
    else:
        readings = rfid_readings()

    for identifier in readings:
        
        if not identifier:
            break
        
        print identifier

        playlist = os.path.join(path, identifier)

        if os.path.exists(playlist):
            if playing is not None:
                playing.kill()
            if quiet:
                playing = subprocess.Popen(["cat", playlist])
            else:
                # Play music as a playlist with mplayer
                # For this to work in the background we must direct in /dev/null
                command = ["mplayer", "-playlist", playlist]
                in_file = open(os.devnull, "r")
                playing = subprocess.Popen(command, stdin=in_file)
        else:
            print "Entry {} is not in the library".format(identifier)


def cat(path, debug=False, quite=False):

    with open(path, "r") as f:
        print f.read()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Interact with music library")
    parser.add_argument("-f",
                metavar="LIRBRARY",
                action="store",
                default=DEFAULT_LIBRARY_PATH,
                help="Path to the library file")
    parser.add_argument("-d",
                "--debug",
                action="store_true",
                help="Use keyboard input instead of reader") 
    parser.add_argument("-q",
                "--quiet",
                action="store_true",
                help="Don't actually play anything") 

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i",
               "--init",
               action="store_const",
               dest="action",
               const=init,
               help="Clean initialization of library")
    group.add_argument("-a",
               "--add",
               action="store_const",
               dest="action",
               const=add_cwd_to_library,
               help="Add an entry")
    group.add_argument("-l",
               "--loop",
               action="store_const",
               dest="action",
               const=playback_loop,
               help="Wait for input and playback music in a loop")
    group.add_argument("-s",
               "--show",
               action="store_const",
               dest="action",
               const=cat,
               help="Display contents of the mapping file")
    

    args = parser.parse_args()
    args.action(args.f, args.debug, args.quiet)


