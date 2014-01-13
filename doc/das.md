## DAS documentation


#### DAS specification

Zilog Z84 processor  
3V battery  
Schmitt Trigger Philips HEF40106BP  
CMOS memory AMD AM29F032B  

#### Hardware requirements
1 Das with 1 port DB-9 male and 1 port DB-19 male  
1 12V power supply  
1 DB-9 female-female cable  
1 case with a DB-15 female port   

#### DAS command list

Note : Every data sequence send by a DAS is followed by \n\r (LFCR in this case)
However standard way in ASCII to end a file is \r\n (CRLF)

  #hE : Help  **works**
  #E0 : No Echo  **work**
  #E1 : Only Data **work**
  #E2 : Data + Time
  #SD : yyyy mm dd hh nn ss : Set Date + Time
  #1SR iiii : Set Integration Period
  #SI nnn : Set Das Number
  #SS ssss : Set Station Number  
  #RI : Read Info  **works**
  #RL : Read Last Data  **works**
  #RM : Read Memory Status => Memory used, Memory available  **works**
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

