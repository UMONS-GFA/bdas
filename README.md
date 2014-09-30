# bdas (v0.4)

Application to interact with a DAS.

### Requirements on server side

* Python 3
* python3-serial

You also need to configure a **settings.py** file (see below)

### Requirements on client side

* Python 3

### Procedure

Launch **simpleDASttytunnel.py** on server then **client2.py** on client for access to a DAS connected by serial on the server(LocalHost).
Launch  **DAStunnel.py** (or **simpleDAStunnel.py** if you do not have access to netcat) on server then **client2.py** on client for access to a DAS on a remote network (RemoteHost) accessible by the server.

**Remark :** Communication between client and local host might be restricted to communications within a private network. In such a case make sure to connect your client through a VPN connection before running client.py.

### Settings configuration (in settings.py):
```

LocalHost = 'IP_ADRESS'
LocalPort = NUM_PORT
RemoteHost = 'IP_ADRESS'
RemotePort = NUM_PORT
DefaultNetid = '255'
DefaultConnectionType = 'Serial'
DefaultConnectionDev = '/dev/ttyUSB0'
EOL = b'\r'

```

### Using a job scheduler like cron

To automate tasks like downloads, one can use a job scheduler like cron to call client2.py. In this case, a command file with commands that client2.py will send to the DAS network should be defined (see example below)
Tasks should then be scheduled within the job scheduler. In case of cron, use **crontab -e** to edit the jobs. Add a line per job, i.e.
```

# m h dom mon dow   command
# _______________________________________________________
# Full downloads - done once a week on saturday or sunday
# _______________________________________________________
0 22 * * 6 python3 /home/user/client2.py "/home/user/DownloadDAS/CommandFiles/FullDownloadDASR001.cmd" >> /home/user/Download/cronlog
0 0 * * 7 python3 /home/user/client2.py "/home/user/DownloadDAS/CommandFiles/FullDownloadDASR002.cmd" >> /home/user/Download/cronlog

```
Note that a log may be kept in a log file (**/home/user/Download/cronlog** in our example). 
