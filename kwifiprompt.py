#!/usr/bin/env python
#
#  This script is a guided, interactive step-by-step process to connect to a wireless network.
#  Sets return code to 0 if connected, anything else meaning an error occured.
#
#  Exit codes:
#
#   1 need root privileges
#   2 no wifi dongle connected
#   3 a connection attempt is already in progress 
#

import os, sys
import subprocess

sys.path.append('/usr/sbin')
from kwififuncs import IWList, is_device, is_connected, connect, disconnect, KwifiCache

NUM_NETWORKS=5

if __name__  ==  '__main__':

    wificache = KwifiCache()

    selected = online = None
    wiface = 'wlan0'

    #
    #  We first need to do some environment sanity checks
    #

    if not os.getuid() == 0:
        subprocess.call(['typewriter_echo', 'You need root privileges to start this app. Please try sudo', '2', '1'])
        sys.exit (1)

    # FIXME!!! This is randomly returning None when dongle plugged in indeed.
    if not is_device(wiface):
        subprocess.call(['typewriter_echo', 'First, plug in your wifi piece. If you don\'t want to use WiFi, press [ENTER]', '2', '1'])
        # Wait for input or hardware reboot
        var = raw_input ()
        sys.exit(2)

    if os.access('/var/run/kanoconnect.py', os.R_OK):
        subprocess.call(['typewriter_echo', 'An instance of Kanoconnect.py is running.', '2', '1'])
        subprocess.call(['typewriter_echo', 'Please wait a few seconds and try again', '2', '1'])

        sys.exit(3)

    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        a,_,_ = is_connected(wiface)
        if not a:
            subprocess.call(['typewriter_echo', 'wireless network is not connected', '1', '2'])
        else:
            msg = 'wireless network is connected to: %s' % (a)
            subprocess.call(['typewriter_echo', msg, '1', '2'])
        sys.exit(0)

    #
    #  Start the walkthrough process to get connected
    #
    subprocess.call(['typewriter_echo', 'Help me find the signal.', '0', '2'])
    subprocess.call(['typewriter_echo', 'Choose a network:', '0', '2'])

    iwl = IWList(wiface).getList(unsecure=False)
    iwl = IWList(wiface).getList(unsecure=False)
    iwl = IWList(wiface).getList(unsecure=False)
    totalNetworks = 0
    for idx, netw in enumerate(iwl):
        enctxt = 'Open'
        if netw['encryption'] != 'off':
            enctxt = 'Protected'

        print '%2d - %s - %s' % (idx + 1, netw['essid'], enctxt)
        if (idx + 1 == NUM_NETWORKS):
            break
        totalNetworks += 1
    print ' s - Skip'
    print ''
    
    if totalNetworks == 0:
        subprocess.call(['typewriter_echo', 'I can\'t find any wireless signals. Don\'t worry, we can still play.', '1', '2'])
        sys.exit(0)

    while not online:
        while selected == None:
            msg = 'Choose with (1-%d)' % (idx+1)
            subprocess.call(['typewriter_echo', msg, '0', '2'])
            var = raw_input ()
            if var.isdigit() and (int(var) >= 1 and int(var) <= idx+1):
                selected = int(var)-1
            else:
                if var in ('s', 'S'):
                    sys.exit(1)

        essid =  (iwl[selected]['essid'])
        encryption = (iwl[selected]['encryption'])
	enckey = None
        if encryption in ('wep', 'wpa'):
            msg = 'What\'s the password?'
            subprocess.call(['typewriter_echo', msg, '0', '1'])
	    enckey = raw_input ()

        msg = 'Trying %s, please stand by...' % essid
        subprocess.call(['typewriter_echo', msg, '0', '2'])
        try:
            connect(wiface, essid, encryption, enckey)
            online = True
            subprocess.call(['typewriter_echo', 'Great! You are online!', '1', '2'])
        except:
            msg = 'Couldn\'t connect to %s. Was the password correct?' % essid
            subprocess.call(['typewriter_echo', msg, '1', '2'])
            selected = None

    if online:
        wificache.save(essid, encryption, enckey)

    sys.exit(0)
