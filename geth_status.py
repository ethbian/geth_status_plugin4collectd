"""
This is a collectd plugin reporting Ethereum geth status.
For more details see https://github.com/ethbian/geth_status_plugin4collectd
"""

import signal
import os
import subprocess

try:
    import collectd
except ImportError:
    raise ImportError('\n\n cannot find Python module: ' +
                      'collectd\n try executing: pip install collectd')

SERVICE = 'geth'
BINARY = '/usr/local/bin/geth'
IPCPATH = '/mnt/ssd/datadir/geth.ipc'

def init():
    """
    This method has been registered as the init callback; this gives the plugin a way to do startup
    actions.
    """
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)

def conf(config):
    """
    This method has been registered as the config callback and is used to parse options from
    given config.
    """
    for key_val in config.children:
        key = key_val.key.lower()
        val = key_val.values[0]
        if key == 'service':
            global SERVICE
            SERVICE = val
        elif key == 'binary':
            global BINARY
            BINARY = val
        elif key == 'ipcpath':
            global IPCPATH
            IPCPATH = val
        else:
            collectd.info('geth_status: Ignoring unknown config key: {}'.format(key))

    collectd.info('geth_status: plugin ready')

def read_geth_stats():
    """
    This method has been registered as the read callback and will be called every polling interval
    to dispatch metrics.
    """
    try:
        geth_service = os.system('systemctl is-active --quiet {}'.format(SERVICE))
    except Exception as exception:
        collectd.warning('Error checking geth service status: {}'.format(exception))
        geth_service = 999

    sync_percent = 0
    binary = True if os.path.exists(BINARY) else False
    ipc = True if os.path.exists(IPCPATH) else False
    if binary and ipc and geth_service == 0:
        try:
            peers = subprocess.check_output('{} {}{} {}'.\
                    format(BINARY, 'attach ipc:', IPCPATH, '--exec net.peerCount'),\
                    shell=True)
            current = subprocess.check_output('{} {}{} {}'.\
                      format(BINARY, 'attach ipc:', IPCPATH, '--exec eth.syncing.currentBlock'),\
                      shell=True)
            highest = subprocess.check_output('{} {}{} {}'.\
                      format(BINARY, 'attach ipc:', IPCPATH, '--exec eth.syncing.highestBlock'),\
                      shell=True)
            if highest != 0 and current != 0:
                sync_percent = float(current)/float(highest)*100
        except Exception as exception:
            collectd.warning('Getting geth stats error: {}'.format(exception))
    else:
        peers = 0
        current = 0
        highest = 0

    collectd.Values(plugin='geth_status',
                    type_instance='service',
                    type='gauge',
                    values=[geth_service]).dispatch()

    collectd.Values(plugin='geth_status',
                    type_instance='peers',
                    type='gauge',
                    values=[peers]).dispatch()

    collectd.Values(plugin='geth_status',
                    type_instance='current',
                    type='gauge',
                    values=[current]).dispatch()

    collectd.Values(plugin='geth_status',
                    type_instance='highest',
                    type='gauge',
                    values=[highest]).dispatch()

    collectd.Values(plugin='geth_status',
                    type_instance='sync',
                    type='gauge',
                    values=[round(sync_percent, 3)]).dispatch()

if __name__ != '__main__':
    collectd.register_init(init)
    collectd.register_config(conf)
    collectd.register_read(read_geth_stats)
else:
    raise SystemExit('Nope - it is a plugin reporting to collected.')
