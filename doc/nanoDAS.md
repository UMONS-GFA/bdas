## nanoDAS documentation


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

#### DAS command list

*Note : Every data sequence send by a nanoDAS is followed by \n\r (LFCR in this case)  
However each command end line sent to nanoDAS must  be  \r\n (CRLF)*  

  #HE : Help  
  #E0 : No Echo  **Implemented**     
  #E1 : Only Data **Implemented**    
  #E2 : Data + Time  **Implemented**  
  #SD : yyyy mm dd hh nn ss : Set Date + Time **Implemented**    
  #SR iiii : Set Integration Period  **Implemented**    
  #SI nnn : Set Das netID **Implemented**    
  #SS ssss : Set Station Number  
  #RI : Read Info **Implemented**  
  #RL : Read Last Data   
  #RM : Read Memory Status => Memory used, Memory available **Implemented**  
  #RV : Read version   
  #ZR station netId integrationPeriod nbInst ( Ex: #ZR 1111 222 3333 4): Reconfig   
  #ZF : erase memory and set default configuration **Implemented**   
  #XB : Full Download **Implemented**    
  #XP : yyyy mm dd hh ss yyyy mm dd hh nn ss : Partial Download  
  #XN : Next Download  
  #WB : Write line in workbook  
  #RW : Read workbook  



#### case specification

yellow : sensor 1  
green : sensor 2  
blue : sensor 3   
green : sensor 4  

