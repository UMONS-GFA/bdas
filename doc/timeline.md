# Timeline

## 2015
* May
  * 2015-05-07 - leveled R013 pluviometer and modified outflow tube and conductivity probe (OK)
  * 2015-05-05 - @09:00 UTC - unable to download from serial connection on nanoDAS R009 : "pas de bloc de date" / @09:30 UTC - replaced nanoDAS R009 RTC battery - synchronized RTC and reset (#ZR) nanoDAS R009 / replaced nanoDAS R002 RTC battery / @10:00 UTC - nanoDAS R002 clock reads 10:28:30 - synchronized nanoDAS R002 RTC / Full download from serial connection on nanoDAS R002 : OK / nanoDAS R007 is not responding from serial connection / replaced nanoDAS R007 RTC battery / @10:30 UTC - nanoDAS R001 clock reads 11:12:00 / nanoDAS R001 sends garbage from serial connection with a cut cable (yellow : GND, blue : RTS, brown : TX, red : RX); when GND of cable is disconnected sends a leading 0x00 with every line (e.g. \0x00 !2015 05 05 10 30 21) and sending commands doesn't work / replaced nanoDAS R001 RTC battery
/ replaced nanoDAS R010 RTC battery / replaced nanoDAS R010 RS232 cable to USC / checked connection on edas2 : OK / @13:58 UTC - nanoDAS R010 clock reads 14:45 UTC - synchronized nanoDAS R010 RTC / Ethernet connection - replaced ethernet switch near the Quanterra and ethernet cable in enclosure#06 / replaced ORB RS232-RS422 linked to nanoDAS R001 with USC / connected to edas1 / connected edas1 branch (nanoDAS R009, nanoDAS R001, nanoDAS R002 and nanoDAS R007) to USC connected to nanoDAS R012 / checked communication with nanoDAS R001, nanoDAS R002, nanoDAS R007, nanoDAS R009 and  nanoDAS R012 : OK / replaced nanoDAS R013 RTC battery (OK, CB, AW) / Updated client2.py to allow for 'host' and port arguments (v2.12) (OK) / checked running connection with host on both ports (edas2 on BB : port XXXX1; edas1 on PC with remserial : port XXXX4) : connection on port XXXX1 sucessful, port XXXX4 not opened yet (OK)
* April
  * 2015-04-24 - replaced ORB RS232-RS422 interfaces with USC on nanoDAS R010 / connected nanoDAS R010 to edas2 (AW). To be fixed : Ground cable disconnected from RS232 adaptor.
  * 2015-04-09 - Installed BB in the cave at the end of edas2 RS-485 network (OK, AW) / replaced ORB RS232-RS422 interfaces on nanoDAS R012 and at the end of edas1 with USCs connected to PC running remserial (not connected to the local network yet) / reconditioned nanoDAS R012 (OK)
* January
  * 2015-01-29 - Tested updated BB firmware with USC using raw TCP in BB settings : seems OK, doesn't repeat FF anymore

## 2014
* December
  * 2014-12-09 - Updated Val d'Enfer Pluviometer : installed new cone, air and water temperature sensors | @09:10 UTC - intervention begins / @10:50 UTC - new cone installed / @11:30 UTC - connexions of temperature sensor 0001 (air) and sensor 0002 (water) / @15:50 UTC - air temp measured with Testo probe at probe 0001 level above ground : 7.0°c / 16:00 UTC - serial download of nanoDAS R001    
* November
  * 2014-11-25 - Serial download of nanoDAS R002
  * 2014-11-16 - Updated client2.py to allow for 'sync' command / updated R013Fulldownload.cmd to synchronise DAS clock on server clock after download (OK)
  * 2014-11-15 - Reset nanoDAS R013 / synchronized clock and set integration period to 5 seconds / improved client2.py / created a backup of cronlog to start with a empty log (OK) 
  * 2014-11-12 - Created network edas2 with 2 USC / Replaced the Brainboxes converter BB (RS-485 - Ethernet converter) with a laptop / Reconditionned nanoDAS R013 and connected to edas2 network / Serial download of nanoDAS R007 R009 R010 R013 / Test of download through the network (repeated FF problem) to compare with serial download (OK, AW, CB) / disconnected edas1 network 

* October
  * 2014-10-14 - Checked serial download / tried to isolate RS-422 origin of extra bytes in download / reset nanoDAS R013 / removed 10 Ohms resistance (OK, ND)
  * 2014-10-09 - Replaced ORB RS232-RS422 converter with USCONVERTER RS232-RS485 converter (USC) with a 10 Ohms resistance between R+ and R- on nanoDAS R013 (OK, CB) 
  * 2014-10-01 - Restored remote connection

* September
  * 2014-09-26 - Remote connection interrupted
  * 2014-09-26 - Installed Val d'Enfer Pluviometer / installed nanoDAS R013 + ORB RS232-RS422 interface (OK, AW, CB, AP)
