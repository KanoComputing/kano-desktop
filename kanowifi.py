#!/usr/bin/env python
#
# file: kanowifi.py
# desc: curses console based app to interactively connect to wireless networks
#

import curses
import time
import traceback
import thread, threading
import os
import sys
import atexit

sys.path.append('/usr/sbin')
from kanoconnect import is_device, IWList, connect, disconnect

# filename to keep our process semaphore
pidfile = '/var/run/kanowifi.py'

# global space
WIRELESS_REFRESH_SECONDS=5
NUMBER_OF_NETWORKS=15
GLOBAL_STATUS='idle'
CONNECTING=False
ABORT=False

# A list to save the last scanned wireless networks.
# a thread semaphore to coordinate access
giwlist = []
giwlock = threading.Lock()

def mainScreen(win, iface):

    win.erase()
    win.addstr(1, 1,"Kanux wireless connection program", curses.A_BOLD)
    win.addstr(2, 1, "%d closest networks are scanned every %d seconds" \
               % (NUMBER_OF_NETWORKS, WIRELESS_REFRESH_SECONDS))

    win.refresh()
    time.sleep (2)

    y = 10 + NUMBER_OF_NETWORKS
    win.move (y, 1)
    win.addstr ("Press any network letter to join it - Q to quit", curses.A_BOLD)
    
    win.refresh()

def thr_update_status(win):
    global ABORT
    while not ABORT == True:
        win.move (3,1)
        win.clrtoeol()
        win.addstr(3, 1, '%s' % (time.ctime()))

        win.move(6,1)
        win.clrtoeol()
        win.addstr("Status: %s" % GLOBAL_STATUS)

        win.refresh()
        time.sleep(1)

def update_iface_status(win, iface):
    global ABORT

    (essid, mode, ap) = is_device(iface)
    win.move (5, 1)
    if essid == None:
        ABORT=True
        win.addstr('Network: Error accessing wireless device - is it unplugged?')
    elif essid == '' or ap == '00:00:00:00:00:00':
        win.addstr('Network: The wireless device is not associated')
    else:
        win.addstr('Network: Wireless device is associated to: ')
        win.addstr('%-20s' % essid, curses.A_BOLD)

def thr_update_wifi(win, iface):

    global GLOBAL_STATUS, CONNECTING, ABORT
    global giwlist, giwlock
    initial_y = 8

    while not ABORT == True:
        y = initial_y

        if CONNECTING == False:
            GLOBAL_STATUS = 'Scanning...'
            iwl = IWList(iface).getList(unsecure=False)
            update_iface_status(win, iface)
            if not iwl or len(iwl) == 0:
                GLOBAL_STATUS = 'No wireless networks could be found.'
            else:
                # display networks in a tabbed list
                win.addstr(y, 3, '    Network Name             Quality     Encrypted', curses.A_BOLD)
                y += 1
                giwlock.acquire()
                giwlist = {}
                for idx, netw in enumerate(iwl):
                    win.clrtoeol()
                    if netw['encryption'] == 'off':
                        encrypted = 'no'
                        color = curses.color_pair(1)
                    else:
                        color = curses.color_pair(2)
                        encrypted = 'yes'

                    iwl[idx]['letter'] = chr (64 + (y-8))
                    win.addstr (y, 3, '%c   %-20s   %7s       %s' % \
                                (netw['letter'], netw['essid'], netw['quality'], encrypted), color)

                    giwlist[iwl[idx]['letter']] = iwl[idx]

                    if y == initial_y + NUMBER_OF_NETWORKS:
                        break
                    else:
                        y += 1

                giwlock.release()

                win.refresh()
                GLOBAL_STATUS = 'Idle'

        time.sleep(WIRELESS_REFRESH_SECONDS)

def mainloop(win, iface):

    global GLOBAL_STATUS, ABORT, CONNECTING, giwlist

    win.nodelay(1)  # disable getch() blocking

    # thread to update time and status
    GLOBAL_STATUS = 'Starting up...'
    thrstatus = threading.Thread(target=thr_update_status, args=(win,))
    thrstatus.daemon = True
    thrstatus.start()

    # draw the main display template
    mainScreen(win, iface)

    # thread to update  neighbouring wireless networks
    thrwifi = threading.Thread(target=thr_update_wifi, args=(win,iface,))
    thrwifi.daemon = True
    thrwifi.start()

    # run until the user wants to quit
    while 1:
        # check for keyboard input
        inch = win.getch()
        # getch() will return -1 if no character is available
        if inch != -1:
            # see if inch is really a character
            try:
                instr = str(chr(inch))
            except:
                # just ignore non-character input
                pass
            else:
                if instr.upper() == 'Q':
                    ABORT=True
                    thrstatus.join()
                    thrwifi.join()
                    break
                if instr.upper() in ('ABCDEFGHIJKLMNO'):
                    if CONNECTING == True:
                        pass
                    else:
                        CONNECTING = True

                        giwlock.acquire()
                        essid = giwlist [ instr.upper() ] ['essid']
                        GLOBAL_STATUS = 'Connecting to %s...' % essid
                        try:
                            connect(iface, essid)
                            GLOBAL_STATUS = 'Idle'
                        except:
                            GLOBAL_STATUS = 'Could not connect to network %s' % essid
                        giwlock.release()
                        CONNECTING = False

        #writeDateTime(win)
        #getDataVals()
        #writeDataVals(win)

        if ABORT == True:
            break

        time.sleep(0.5)

def startup(iface):
    # borrowed the idea of using a try-except wrapper around the
    # initialization from David Mertz.
    try:
        # Initialize curses
        stdscr = curses.initscr()
        stdscr.border(1)
        curses.start_color()

        # define colors for open and secure networks
        # TODO: Find out how to replace COLOR_BLACK with transparency attribute
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        mainloop(stdscr, iface)                # Enter the main loop

        # Set everything back to normal
        curses.echo()
        curses.curs_set(0) # hide cursor
        curses.nocbreak()

        curses.endwin()                 # Terminate curses
    except:
        # In event of error, restore terminal to sane state.
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception

def remove_pid ():
    try:
        os.unlink(pidfile)
    except:
        pass

if __name__=='__main__':

    if not os.getuid() == 0:
        print 'You need root privileges to start this app. Please try sudo'
        sys.exit (1)

    if len(sys.argv) < 2:
        print 'syntax: kanowifi.py <iface>'
        sys.exit(1)
    else:
        iface = sys.argv[1]

    # if kanoconnect is running we can't proceed.
    # we can't run more than 1 instance of kanowifi.
    # otherwise register our pid file so we don't clash and go ahead.
    if os.access('/var/run/kanoconnect.py', os.R_OK) == True:
        print 'It seems Kanoconnect.py is running, searching for a wireless connection.'
        print 'Please wait a few seconds and run kanowifi.py again.'
        sys.exit(1)
    else:
        if os.access(pidfile, os.R_OK) == True:
            print 'An instance of Kanowifi.py is already running.'
            sys.exit(1)
        else:
            atexit.register(remove_pid)
            frun = open (pidfile, 'w')
            frun.write (str(os.getpid()))
            frun.close()

    # make sure the device name is available before proceeding
    (essid, mode, ap) = is_device(iface)
    if essid==None:
        print 'Device %s is not present or active' % (iface)
        sys.exit(1)

    # main curses app flow
    startup(iface)
