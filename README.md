# geth_status_plugin4collectd
A collectd plugin reporting Ethereum geth basic status.  
Tested on RPi 4 with Raspbian.  
Plugin reports (via IPC) **geth service status** (running/stopped), **number of currently connected peers**(nodes), network and local **latest block number** and - based on these two - **sync percentage**.

## quick start
- install collectd  
*raspbian: apt-get install collectd*
- clone the repository  
*git clone https://github.com/ethbian/geth_status_plugin4collectd.git*
- create directory for the plugin  
*mkdir /usr/local/lib/collectd*
- copy the geth_status.py file to the plugin directory  
*cp geth_status.py /usr/local/lib/collectd/*
- update the collectd config file (raspbian: **/etc/collectd/collectd.conf**) by adding to the end of the file:

```
LoadPlugin python
<Plugin python>
    ModulePath "/usr/local/lib/collectd"
    Import "geth_status"
    <Module geth_status>
        Service "geth"
        Binary "/usr/local/bin/geth/geth"
        IPCpath "/mnt/ssd/datadir/geth.ipc"
    </Module>
</Plugin>
```

- restart collectd  
*raspbian: service collectd restart*
- check logfile for possible errors  
*raspbian: service collectd status*  
*raspbian: tail /var/log/syslog*

- options:  
**Service** - service name used with *systemctl* / *service* commands for stopping and starting geth binary  
**Binary** - path to the geth binary  
**IPCpath** - path to the *geth.ipc* file (usually located in the datadir directory)
- pull requests are more than welcome if you're fixing something

