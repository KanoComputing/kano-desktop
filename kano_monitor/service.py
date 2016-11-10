# service.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Memory tracking service.
# * Polls processes to see if they have:
#   * exceeded their arm reservation (individually)
#   * exceeded their gpu reservation (collectively)
#   * died
#
# * If an undebooking has occurred, issues a warning
#    -> Error to kano logs
#    -> if debug is on, displays a graphical warning
#
#  Does not talk to the gpu driver itself, to avoid
#  making an additional connection. Instead the notification tool
#  sends gpu statistics via an api.

# All numbers are in kB

import os

import dbus
import dbus.service
import json
import subprocess

from gi.repository import GObject

from kano.logging import logger

BUS_NAME = 'me.kano.monitor'
MONITOR_OBJECT_PATH = '/me/kano/monitor/memory'
MONITOR_IFACE = 'me.kano.monitor.memory'

MEM_INFO_PATH = "/proc/meminfo"
FUDGE_FACTOR = 9*1024

warnings = {}


def do_warn(code, warning):
    """
    Generate a warning. Because this can be called each poll, we keep 
    a record ('warnings') of warnings already generated and only generate one the first time.
    if kano_logs output_level is debug, we also display a visible indicator.
    """
    global warnings
    print str(warnings)
    if code not in warnings:
        logger.error(warning)
        if logger.get_output_level() == 'debug':
            os.system("kano-start-splash -b 0 /usr/share/linux-story/media/images/rm.png &")

        warnings[code] = 1


def get_arm_mem():
    '''
    Get the total and currently available arm memory
    '''
    total = None
    avail = None
    for line in open(MEM_INFO_PATH).readlines():
        (name, num) = line.split(":")
        num = int(num.lstrip().split(' ', 1)[0])
        if name == 'MemTotal':
            total = num
        elif name == 'MemAvailable':
            avail = num
        if total is not None and avail is not None:
            break
    return total, avail


class pidTrack:
    '''
    Class which represents one process with a reservation
    We know its pid and can check when it has exitted.
    '''
    def __init__(self, pid, gpu_reservation, arm_reservation, name):
        self.pid = pid
        self.gpu_reservation = gpu_reservation
        self.arm_reservation = arm_reservation
        self.name = name
        self.orig_dir = os.getcwd()

        # Obtain a handle on the pid's proc directory so we can check when it
        # has exited
        try:
            self.proc_dir = os.open('/proc/{}'.format(pid), os.O_DIRECTORY)
        except OSError:
            # mark as already exitted
            self.proc_dir = None

    def has_exited(self):
        '''
        Check that a process has exited.
        '''

        # Was it marked as already exited in __init__?
        if not self.proc_dir:
            return True
        # if it might still exist, attempt to change to its proc directory.
        # if that is missing, it has exited
        try:
            os.fchdir(self.proc_dir)
            os.chdir(self.orig_dir)
        except OSError:
            logger.debug("pid {} quit".format(self.pid))
            os.close(self.proc_dir)
            return True
        return False

    def to_dict(self):
        '''
        Convert this obecjt to a dict for use in debugging
        '''
        res = {}
        res['pid'] = self.pid
        res['gpu_reservation'] = self.gpu_reservation
        res['arm_reservation'] = self.arm_reservation
        res['name'] = self.name
        res['rss'] = self.get_mem()
        return res

    def get_mem(self):
        '''
        Get the RSS of this process, if it still exists
        otherwise return -1
        '''
        try:
            stat = open('/proc/{}/stat'.format(self.pid)).read()
            # field 23 of proc stat is rss, which is in 4kb pages
            rss = int(stat.split(' ')[23]) * 4
        except:
            logger.warn("error parsing stat file for {}".format(self.pid))
            rss = -1
        return rss

    def check_arm_mem(self):
        '''
        Check that the arm memory used by this process is less than
        its reservation
        '''
        rss = self.get_mem()
        if rss > self.arm_reservation:
            warning = " {} (pid {}) using more than allocated {} > {}".format(
                self.name, self.pid, rss, self.arm_reservation)
            do_warn('arm {}'.format(self.pid), warning)


class MonitorService(dbus.service.Object):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/monitor and
    its interface to me.kano.monitor.memory

    """

    def __init__(self, bus_name):
        '''
        Initialise dbus service
        Start tracking job (via gtk timer)        
        '''
        dbus.service.Object.__init__(self, bus_name, MONITOR_OBJECT_PATH)

        self.MONITOR_POLL_RATE = 1000 * 5
        self.current_gpu_reloc_free = 99*1024   # Should be overridden
        self.current_gpu_reloc_total = 99*1024  # Should be overridden
        self.current_gpu_reserved = 0

        self.get_arm_mem_info()
        self.current_arm_reserved = 0

        self.tracking_pids = []

        GObject.threads_init()
        GObject.timeout_add(self.MONITOR_POLL_RATE, self._monitor_thread)

    def get_arm_mem_info(self):
        '''
        Capture arm memory stats
        '''
        try:
            (total, avail) = get_arm_mem()
            self.current_arm_free = avail
            self.current_arm_total = total
        except:
            logger.error("error reading arm mem info")

    def check_gpu_mem(self):
        '''
        Check that all gpu usage is captured in reservations
        '''
        reservation_gpu_total = 0
        for pid in self.tracking_pids:
            reservation_gpu_total = reservation_gpu_total + pid.gpu_reservation

        if reservation_gpu_total != self.current_gpu_reserved:
            do_warn('intmem', "Internal error in gpumem calc")

        gpu_used = self.current_gpu_reloc_total - self.current_gpu_reloc_free

        if reservation_gpu_total < gpu_used:
            warning = "More GPU used than reserved: {} > {}\n".format(gpu_used,
                                                                      reservation_gpu_total)
            warning = warning + self.status() + '\n'
            try:
                gpu_procs = subprocess.check_output('lsof /dev/vchiq')
                warning += gpu_procs
            except:
                pass
            do_warn('res: {}'.format(reservation_gpu_total), warning)

    def _monitor_thread(self):
        """
         Perform all checking
        """
        try:
            self.get_arm_mem_info()
            self.check_pids()

            self.check_gpu_mem()

        finally:
            return True  # keep calling this method indefinitely

    def check_pids(self):
        '''
        Check the pids we are tracking 
        * have they died?
        * ar they using too much memory?
        '''
        i = 0
        while i < len(self.tracking_pids):
            if self.tracking_pids[i].has_exited():
                logger.debug("Died, so freeing {} (pid {})".format(
                    self.tracking_pids[i].name,
                    self.tracking_pids[i].pid))
                self.free_reservation_accounting(self.tracking_pids[i])
                del self.tracking_pids[i]
            else:
                self.tracking_pids[i].check_arm_mem()
                i = i + 1

    def free_reservation_accounting(self, pidtrack):
        '''
        Helper to remove reservation accounting for one process
        '''
        self.current_gpu_reserved -= pidtrack.gpu_reservation
        self.current_arm_reserved -= pidtrack.arm_reservation


###################################################################################
#
#  DBus APIs
#
###################################################################################


    @dbus.service.method(MONITOR_IFACE, in_signature='ii', out_signature='')
    def set_current_gpu_reloc_free(self, gpu_reloc_free, gpu_reloc_total):
        '''
        This is called by the GPU monitor in kano-notifications-daemon to inform
        us of the current free gpu memory. We also set the total every time (alhough
        it doesn't change) because this is more robust to the startup sequence of 
        the different daemons.
        '''
        try:
            self.current_gpu_reloc_free = gpu_reloc_free
            self.current_gpu_reloc_total = gpu_reloc_total - FUDGE_FACTOR
            logger.debug('Free reloc: {} Total: {} '.format(gpu_reloc_free,
                                                            gpu_reloc_total))

        except Exception as e:
            # Catch any exceptions, as otherwise it is sent to caller
            logger.error("Exception in  call to set_current_gpu_reloc_free ",
                         exception=e)

    @dbus.service.method(MONITOR_IFACE, in_signature='iiis', out_signature='b')
    def query(self, pid, gpu_reservation, arm_reservation, name):
        '''
        Check whether a reservation level is okay.
        Doesn't actually do the reservation
        '''
        try:
            predicted_gpu_free = self.current_gpu_reloc_total - self.current_gpu_reserved

            if (gpu_reservation > predicted_gpu_free or
                gpu_reservation > self.current_gpu_reloc_free):
                    logger.warn("Failed reservation: {}(pid {}) wanted GPU mem {} "
                                   "current free {} predicted free {}".format(name,
                                                                              pid,
                                                                              gpu_reservation,
                                                                              self.current_gpu_reloc_total,
                                                                              predicted_gpu_free))
                    return False

            predicted_arm_free = self.current_arm_total - self.current_arm_reserved
            if (arm_reservation > predicted_arm_free or
                arm_reservation > self.current_arm_free):
                    logger.warn("Failed reservation: {}(pid {}) wanted ARM mem {} "
                                   "current free {} predicted free {}".format(name,
                                                                              pid,
                                                                              arm_reservation,
                                                                              self.current_arm_total,
                                                                              predicted_arm_free))
                    return False

            return True
        except Exception as e:
            # Catch any exceptions, as otherwise it is sent to caller
            logger.error("Exception in  call to reserve", exception=e)

    @dbus.service.method(MONITOR_IFACE, in_signature='iiis', out_signature='b')
    def reserve(self, pid, gpu_reservation, arm_reservation, name):
        '''
        Reserve memory for a PID
        Returns false if too much memory has already been reserved
        '''
        try:
            logger.debug("reserving {} gpu {} arm for {} (pid {}) ".format(gpu_reservation,
                                                                           arm_reservation,
                                                                           name,
                                                                           pid))

            okay = self.query(pid, gpu_reservation, arm_reservation, name)
            if not okay:
                return False

            self.tracking_pids.append(pidTrack(pid,
                                               gpu_reservation,
                                               arm_reservation,
                                               name))
            self.current_gpu_reserved += gpu_reservation
            self.current_arm_reserved += arm_reservation
            return True
        except Exception as e:
            # Catch any exceptions, as otherwise it is sent to caller
            logger.error("Exception in  call to reserve", exception=e)

    @dbus.service.method(MONITOR_IFACE, in_signature='i', out_signature='')
    def free(self, pid):
        try:
            logger.debug("free called for {}".format(pid))
            i = 0
            while i < len(self.tracking_pids):
                if self.tracking_pids[i].pid == pid:
                    logger.debug("freeing {} (pid {})".format(self.tracking_pids[i].name, pid))
                    self.free_reservation_accounting(self.tracking_pids[i])
                    del self.tracking_pids[i]
                else:
                    i = i + 1
        except Exception as e:
            # Catch any exceptions, as otherwise it is sent to caller
            logger.error("Exception in  call to free", exception=e)

    @dbus.service.method(MONITOR_IFACE, in_signature='', out_signature='s')
    def status(self):
        try:
            res = {}
            res['current_gpu_reloc_free'] = self.current_gpu_reloc_free
            res['current_gpu_reloc_total'] = self.current_gpu_reloc_total
            res['current_gpu_reserved'] = self.current_gpu_reserved
            res['current_arm_free'] = self.current_arm_free
            res['current_arm_total'] = self.current_arm_total
            res['current_arm_reserved'] = self.current_arm_reserved
            res['processes'] = []
            for tp in self.tracking_pids:
                res['processes'].append(tp.to_dict())
            return json.dumps(res)

        except Exception as e:
            # Catch any exceptions, as otherwise it is sent to caller
            logger.error("Exception in  call to status", exception=e)

