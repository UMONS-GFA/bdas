# bdas

Application to interact with a DAS.

Current release :  [v0.4.2](https://github.com/UMONS-GFA/bdas/releases/tag/v0.4.2) (June 2015)


### Requirements on server side

* Python 3
* python3-serial

You also need to configure a **settings.py** file (see below)

### Requirements on client side

* Python 3

[Read the wiki](https://github.com/UMONS-GFA/bdas/wiki)

### Procedure

#### With simpleDASttytunnel

Launch **simpleDASttytunnel.py** on server then **client2.py** on client for access to a DAS connected by serial on the server(LocalHost).
Launch  **DAStunnel.py** (or **simpleDAStunnel.py** if you do not have access to netcat) on server then **client2.py** on client for access to a DAS on a remote network (RemoteHost) accessible by the server.

**Remark :** Communication between client and local host might be restricted to communications within a private network. In such a case make sure to connect your client through a VPN connection before running client.py.

#### Or with Socat

Install socat  
``# apt-get install socat``

##### Optionnal : fix USB serial name

List USB devices 
``lsusb``

    Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. 
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. 
    Bus 001 Device 004: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
    Bus 001 Device 012: ID 2341:0043 Arduino SA Uno R3 (CDC ACM)

Example fort the serial port

idVendor is 067b  
idProduct is 2303  

Create a file in /etc/udev/rules.d

`` # nano 99-usb_serial.rules ``

and add the line 
``SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", SYMLINK+="USBT001"``

##### Give rights to the user who will launch socat
``# chown USERNAME: /dev/PORTNAME``



##### Launch socat  
``$ socat TCP4-LISTEN:10001 /dev/PORTNAME,b9600,raw,echo=0 & > /home/USERNAME/log``


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

