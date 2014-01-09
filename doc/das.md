## DAS documentation


#### DAS specification

* Zilog Z84 processor
* 3V battery
* Schmitt Trigger Philips HEF40106BP
* CMOS memory AMD AM29F032B

#### Hardware requirements
* 1 Das with 1 port DB-9 male and 1 port DB-19 male
* 1 12V power supply
* 1 DB-9 female-female cable
* 1 case with a DB-15 female port

#### DAS command list
  #hE : Help
  #E0 : No Echo
  #E1 : Only Data
  #E2 : Data + Time
  #SD : yyyy mm dd hh nn ss : Set Date + Time
  1SR iiii : Set Integration Period
  #SI nnn : Set Das Number
  #SS ssss : Set Station Number
  #RI : Read Info
  #RL : Read Last Data
  #RM : Read Memory Status
  #ZR ssss nnn iiii s 1111 2222 3333 4444 XX : Reconfig
  #XB : Full Download
  #XP : yyyy mm dd hh ss yyyy mm dd hh nn ss : Partial Download
  #XN : Next Download
  #WB : Write line in workbook
  #RW : Read workbook



#### case specification

yellow : sensor 1
green : sensor 2
green : sensor 3
blue : sensor 1
green : sensor 4

