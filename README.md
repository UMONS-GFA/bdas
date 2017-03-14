# bdas
[![Doc Latest](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](http://bdas.readthedocs.io/en/latest/)

Application to interact with a DAS.

Current release :  [v0.5](https://github.com/UMONS-GFA/bdas/releases/tag/v0.5) (Mars 2016)


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

##### Autorelauch socat 
``socat tcp-l:10004,reuseaddr,fork file:/dev/USBR002,nonblock,raw,echo=0 &``

##### Optionnal: launch socat at startup

With cron

    # crontab -e
    
Add

    socat tcp-l:10004,reuseaddr,fork file:/dev/USBT001,nonblock,raw,echo=0 &


Or with init.d

Create process file in /etc/init.d/

``# nano /etc/init.d/usb-mounting.sh``  

    #!/bin/bash
    # /etc/init.d/usb_mounting.sh
    case "$1" in
    start)
       socat tcp-l:10001,reuseaddr,fork file:/dev/PORTNAME,nonblock,raw,echo=0 &
       socat tcp-l:10002,reuseaddr,fork file:/dev/PORTNAME,nonblock,raw,echo=0 &
    ;;
    stop)
         echo "Stopping socat"
    ;;
    *)
        # echo "Usage: /etc/init.d/usb-mounting.sh {start|stop}"
        # exit 1
    ;;
    esac
    exit 0
    
Install init script  
``update-rc.d usb-mounting.sh defaults``


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

