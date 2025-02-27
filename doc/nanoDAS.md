## nanoDAS documentation

The jumper reset the DAS !!


#### nanoDAS specification

Zilog Z84 processor  
3V battery  
Schmitt Trigger Philips HEF40106BP  
CMOS memory AMD AM29F032B  

#### Hardware requirements
1 nanoDas with 1 port DB-9 male and 1 port DB-15 male  
1 12V power supply  
1 DB-9 female-female cable  
1 case with a DB-15 female port   

#### NanoDAS + female RS232 

![Female RS232 plug](https://github.com/UMONS-GFA/bdas/blob/master/doc/female-rs232-plug.JPG)

RS232 plug pinout  
Pin 2 : Rx (Red)   ->  Rx du Das  
Pin 3 : Tx (Brown) ->  Tx du Das  
Pin 5: GND (Yellow)  
Pin 7: RTS (Blue)  

![Connection to DAS](https://github.com/UMONS-GFA/bdas/blob/master/doc/nanoDAS-rs232-connection.JPG)

#### NanoDAS + male RS232 

Male RS232 plug

RS232 plug pinout  
Pin 2 : Rx (Brown)   ->  Rx du Das  
Pin 3 : Tx (Red) ->  Tx du Das  
Pin 5: GND (Yellow)  
Pin 7: RTS (Blue)  

Connection to DAS


#### DAS command list

*Note : Every data sequence send by a nanoDAS is followed by \n\r (LFCR in this case)  
However each command end line sent to nanoDAS must  be  \r (CR)*  

  #HE : Help  
  #E0 : No Echo  **Implemented**     
  #E1 : Only Data **Implemented**    
  #E2 : Data + Time  **Implemented**  
  #SD : yyyy mm dd hh nn ss : Set Date + Time **Implemented**    
  #SR iiii : Set Integration Period  **Implemented**    
  #SI nnn : Set Das netID **Implemented**    
  #SS ssss : Set Station Number  
  #RI : Read Info **Implemented**  
  #RL : Read Last Data   
  #RM : Read Memory Status => Memory used, Memory available **Implemented**  
  #RV : Read version   
  #ZR station netId integrationPeriod nbInst sensor1 ... code  
  ( Ex: #ZR 1111 222 3333 4 0001 0002 0003 0004 31): Reconfig  
  #ZF : erase memory and set default configuration **Implemented**   
  #XB : Full Download **Implemented**    
  #XP : yyyy mm dd hh ss yyyy mm dd hh nn ss : Partial Download  
  #XN : Next Download  
  #WB : Write line in workbook  
  #RW : Read workbook
  #EW : Erase workbook


#### Workbook codes  

   Event code   Event  
   1          : #SD oldvalue newvalue  
   2          : #SR oldvalue newvalue  
   3          : #XF  
   4          : #XP  
   5          : #XN start end  
   6          : #ZF  
   7          : #ZM  
   8          : #ZR newconfig  
   9          : start up  
  10          : ?  
  11          : #XS  
  12          : ?  
  13          : ?  
  14          : sizeoftext text  
  15          : #SI oldvalue newvalue  
  16          : #SS oldvalue newvalue  
  
*Note : the date (in seconds after 01/01/1970 01:00:00) leads the event code*

#### Case specification

orange : sensor 1  
yellow : sensor 2  
green : sensor 3   
blue : sensor 4  

