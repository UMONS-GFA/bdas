# bdas

Application to interact with a DAS.

Current release :  [v0.4.1](https://github.com/UMONS-GFA/bdas/releases/tag/v0.4.1) (October 2014)


### Requirements on server side

* Python 3
* python3-serial

You also need to configure a **settings.py** file (see below)

### Requirements on client side

* Python 3
* 

[(https://github.com/UMONS-GFA/bdas/wiki)Read the wiki]

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

A typical command file i.e. **FullDownloadDASR001.cmd**:
```

-001
#E0
#RI
#XB
R001full
5400
```

line 1 : activate DAS number 001
line 2 : quiet mode
line 3 : read info from DAS 001
line 4 : full download
line 5 : filename part
line 6 : max expected download time (to avoid blocking downloads)

A typical extract of the log file **cronlog**:
```

____________
UTC time : 2014 06 03 18:27
Trying to connect...
Socket connected
____________
UTC time : 2014 06 03 18:27
Sending command -001 ...
Expected response: b'!HI'
Response to command -001 received
!HI 0000 001 0060 4 0001 0002 0003 0004 007390 133256 

*2014 06 03 18 26 00 041869.0508 000000.0000 000000.0000 002640.5667 

Next command...
____________
UTC time : 2014 06 03 18:27
Sending command #E0 ...
Expected response: b'!E0'
Response to command #E0 received
!E0 [Echo Disabled]

Next command...
____________
UTC time : 2014 06 03 18:27
Sending command #RI ...
Expected response: b'!RI'
Response to command #RI received
!RI Station:0000 DasNo:001 Integration:0060 I1:0001 I2:0002 I3:0003 I4:0004 221721 3997696 1401819300

Next command...
____________
UTC time : 2014 06 03 18:27
Sending command #XB ...
Expected response: b'\xfd'
Response to command #XB received
*** Downloading data ... ***
Saving results in /home/user/DownloadDAS/R001Full_20140603_1827.bin
*** Download complete! ***
Next command...
Ending at UTC time : 2014 06 03 18:30
____________
```

