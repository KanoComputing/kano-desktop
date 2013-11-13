#!/usr/bin/env python
#
# file: kwififuncs.py
# desc: Common module for wireless support functions
#

import os, time, subprocess, syslog, urllib2
import shlex, json

class IWList():
    def __init__(self, interface):
        self.rawdata = ""
        self.data = None
        self.interface = interface
        self.refresh()

    def refresh(self):
        # Get raw data as a string
        self.rawdata = self.getRawData(self.interface)
        # Parse raw data into a dictionary
        if self.rawdata is not None and len(self.rawdata.strip()):
            self.data = self.parseRawData(self.rawdata)

    def getRawData(self, interface):
        # Runs iwlist and gets WiFi data in a string
        # Developped, tested with Wireless Extension v29 English translation, Nov 2007
        cstring = "iwlist " + interface + " scan 2>/dev/nul"
        return os.popen(cstring).read()

    def parseRawData(self, rawdata):
        # Parses a string containing the data printed by iwlist
        # Pre-condition: rawdata is not empty
        rawdatas = rawdata.split("\n")
        # Strip blanks
        # Let's separate by cells
        cellDataL = []
        #currentCell = None
        for s in rawdatas:
            # If new cell:
            if s.lstrip().startswith("Cell "):
                # log.debug("parseRawData: new cell")
                cellDataL.append([])
            if len(cellDataL)>0 and len(s)>0:
                cellDataL[len(cellDataL)-1].append(s)
        # Data is separated by cells, now we'll parse each cell's data
        parsedCellData = {}
        for s in cellDataL:
            if s is not None:
                (cellNumber, cellData) = self.parseCellData("\n".join(s))
                parsedCellData[cellNumber] = cellData
        #log.debug("parseRawData: parsed "+str(len(cellDataL))+" cells")
        return parsedCellData
        # print self.data

    def printData(self):
        # Debugging print
        for s in self.data:
            print s, self.data[s]

    def parseCellData(self, rawCellData):
        # Parses a string containing raw cell data
        # @return a tuble containing the cell's number and a dictionary with the data
        splitRawData = rawCellData.split("\n")
        cellData = {}
        for s in splitRawData:
            if s.strip().startswith("Cell "):
               cellData["Number"] = self.getCellNumber(s)
               cellData["MAC"] = self.getCellMAC(s)
            if s.strip().startswith("ESSID:\""):
               cellData["ESSID"] = self.getCellESSID(s)
            if s.strip().startswith("Protocol:"):
               cellData["Protocol"] = self.getCellProtocol(s)
            if s.strip().startswith("Mode:"):
               cellData["Mode"] = self.getCellMode(s)
            if s.strip().startswith("Mode:"):
               cellData["Mode"] = self.getCellMode(s)
            if s.strip().startswith("Frequency:"):
               cellData["Frequency"] = self.getCellFrequency(s)
               cellData["Channel"] = self.getCellChannel(s)
            if s.strip().startswith("Quality="):
               cellData["Quality"] = self.getCellQuality(s)
               cellData["Signal"] = self.getCellSignal(s)
               cellData["Noise"] = self.getCellNoise(s)
            if s.strip().startswith("Encryption key:"):
               cellData["Encryption"] = self.getCellEncryption(s)
            #if s.strip().startswith("Bit Rates:"):
            #   cellData["Bit Rates"] = self.getCellBitRates(s, splitRawData)
            # TODO: parse encryption key details and Extra tags
            if s.strip().startswith("Extra:"):
                try:
                    extra = cellData["Extra"]
                except KeyError:
                    extra = []
                extra.append(self.getCellExtra(s))
                cellData["Extra"] = extra
        
        return cellData["Number"], cellData

    def getCellExtra(self, s):
        s = s.split(":")
        if len(s)>2:
            ret = ":".join(s[1:])
            return ret
        else:
            return s[1]
       
    def getCellBitRates(self, s, rawdatas):
        # Pre-condition: s is in rawdatas, and bit rates are described in 3 lines
        ixBitRate = rawdatas.index(s)
        rawBitRate = rawdatas[ixBitRate].split(":")[1].strip() + "; " + rawdatas[ixBitRate+1].strip() + "; " + \
            rawdatas[ixBitRate+2].strip()
        return rawBitRate
    
    def getCellNumber(self, s):
        return s.strip().split(" ")[1]

    def getCellFrequency(self, s):
        s = s.split(":")[1]
        return s.strip().split(" ")[0]

    def getCellChannel(self, s):
        return s.strip().split(" ")[3][0:-1]

    def getCellEncryption(self, s):
        return s.strip().split(":")[1]

    def getCellSignal(self, s):
        s = s.split("Signal level=")[1]
        return s.strip().split(" ")[0]

    def getCellNoise(self, s):
        try:
            s = s.split("Noise level:")[1]
            return s.strip().split(" ")[0]
        except:
            return 0

    def getCellQuality(self, s):
        s = s.split("=")[1]
        return s.strip().split(" ")[0]

    def getCellMAC(self, s):
        return s.strip().split(" ")[4]

    def getCellESSID(self, s):
        return s.strip().split(":\"")[1][0:-1]

    def getCellProtocol(self, s):
        return s.strip().split(":")[1][-1]

    def getCellMode(self, s):
        return s.strip().split(":")[1]

    def getData(self): 
        return self.data

    def sortNetworks(self, adict):
        x,z = adict['quality'].split('/')
        factor = int(x)/float(z)
        return factor

    def getList(self, unsecure=False, first=False):
        '''
        Return a comfortable list of wireless networks 
        sorted by signal strength in descending order
        '''
        self.iwnets = []
        for w in self.data:
            ww = self.data[w]
            try:
                wnet = { 'essid' : ww['ESSID'],
                         'channel' : ww['Channel'],
                         'signal' : ww['Signal'],
                         'quality' : ww['Quality'],
                         'encryption' : ww['Encryption']
                         }
                if unsecure and ww['Encryption'] == 'on':
                    continue
                else:
                    if ww['Encryption'] == 'on':
                        if ww.has_key('Extra'):
                            wnet['encryption'] = 'wpa'
                        else:
                            wnet['encryption'] = 'wep'
                     
                self.iwnets.append (wnet)                

            except:
                pass

        k = sorted (self.iwnets, key=self.sortNetworks, reverse=True)
        self.iwnets = k

        if first and len(self.iwnets) > 1:
            return [ self.iwnets[0] ]
        else:
            return self.iwnets

def remove_pid (filename):
    try:
        os.unlink(filename)
    except:
        pass

def execute(cmdline):
    '''
    Executes command. If it fails with return code an exception is raised.
    If successful returns True
    '''
    args = shlex.split(cmdline)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out,err) = p.communicate()
    rc = p.returncode
    if not rc == 0:
        syslog.syslog('FAIL: "%s" rc=%s, out="%s", err="%s"' % (cmdline, rc, out, err))
        raise Exception (cmdline, 'rc=%s, out="%s", err="%s"' % (rc, out, err))
    else:
        return out, err

def is_device(iface):
    '''
    Returns True if wireless dongle is connected, False otherwise
    '''
    try:
        out,err = execute("iwconfig %s" % iface)
        return True
    except:
        return False

def is_connected(iface):
    '''
    Returns data as returned by <iwconfig device>
    or None if device is not present or non-operative
    '''
    essid = mode = ap = None
    time.sleep(1)
    try:
        out,err = execute("iwgetid %s --raw" % iface)
        essid = out.strip()

        out,err = execute("iwgetid %s --raw --ap" % iface)
        ap = out.strip()

        # mode 2 = Managed
        out,err = execute("iwgetid %s --raw --mode" % iface)
        out = out.strip()
        if out == '2': mode = 'Managed'
        else:
            mode = out

    except:
        pass

    return (essid, mode, ap)

def wpa_conf(essid, psk, confile):
    wpa_conf = '''
      network={
             ssid="%s"
             scan_ssid=1
             key_mgmt=WPA-PSK
             psk="%s"
      }
    ''' % (essid, psk)

    f = open(confile, 'w')
    f.write(wpa_conf)
    f.close()

def connect(iface, essid, encrypt='off', seckey=None):
    '''
    encrypt can either be 'off', 'wep' or 'wpa'
    in the latter 2 cases, seckey should be the encryption key
    of the wireless network AP.
    '''

    time.sleep(1)

    #
    # kill previous connection daemons
    #
    try:
        execute("pkill -f 'dhclient -1 wlan0'")
    except:
        pass

    # and wpa supllicant daemons
    try:
        execute("pkill -f 'wpa_supplicant'")
    except:
        pass

    execute("iwconfig %s mode managed" % iface)
    execute("iwconfig %s essid '%s'" % (iface, essid))

    if encrypt == 'wep':
        syslog.syslog("Setting WEP encryption key for network '%s' to interface %s" % (essid, iface))
        execute("iwconfig %s enc s'%s'" % (iface, seckey))
    elif encrypt == 'wpa':
        syslog.syslog("Starting wpa_supplicant for network '%s' to interface %s" % (essid, iface))
        wpafile = '/etc/kano_wpa_connect.conf'
        wpa_conf(essid, seckey, confile=wpafile)

        try:
            # wpa_supplicant might complain even if it goes ahead doing its job
            execute("wpa_supplicant -t -d -c%s -i%s -f /var/log/kano_wpa.log -B" % (wpafile, iface))
        except:
            pass

    execute("dhclient -1 %s" % iface)
    return True

def disconnect(iface):
    execute ('iwconfig "%s" essid off' % iface)
    execute ('iwconfig "%s" mode managed' % iface)
    time.sleep(3)
    return 

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except:
        pass
        return False


class KwifiCache:
    '''
    Class to manage a cache of the last successful wireless connection.
    Call save() when the connection succeeds, return the True on success.
    Call get(essid) to know if a neighbouring network is cached, returns None otherwise
    Call get_latest() to get currently cached network if any, returns None otherwise

    Data is written in plain json format.
    '''
    def __init__(self, cache_file='/etc/kwifiprompt-cache.conf'):
        self.cache_file = cache_file

    def save (self, essid, encryption, enckey):
        return self.__save_cache__(essid, encryption, enckey)

    def get (self, essid):
        wdata = self.__get_cache__()
        try:
            if wdata['essid'] == essid:
                return wdata
        except:
            return None

    def get_latest (self):
        return self.__get_cache__()

    def __save_cache__ (self, essid, encryption, enckey):
        wdata = json.dumps ({'essid': essid, 'encryption': encryption, 'enckey': enckey}, 
                            sort_keys=True, indent=4, separators=(',', ': '))
        with open(self.cache_file, 'w') as f:
            f.write (wdata)
        return True

    def __get_cache__(self):
        if not os.access(self.cache_file, os.R_OK):
            return None
        with open(self.cache_file, 'r') as f:
            lastknown = f.read()
        wdata = json.loads(lastknown)
        return wdata
