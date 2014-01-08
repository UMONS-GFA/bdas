# bdas

Application to interact with a DAS.

### Requirements on server side

* Python 3
* python3-serial

You also need to configure a **settings.py** file

### Requirements on client side

* Python 3

### Procedure

Launch **simplenbDASttytunnel.py** on server then **nonblockingsocketclient.py** on client.

Settings configuration:
```
LocalHost = 'IP_ADRESS'
LocalPort = NUM_PORT
```
