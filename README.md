# bdas (v0.3)

Application to interact with a DAS.

### Requirements on server side

* Python 3
* python3-serial

You also need to configure a **settings.py** file

### Requirements on client side

* Python 3

### Procedure

Launch **simpleDASttytunnel.py** on server then **client.py** on client for access to a DAS connected by serial on the server(LocalHost).  
Launch  **simpleDASttytunnel.py** on server then **client.py** on client for access to a DAS on a remote network (RemoteHost) accessible by the server.


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
