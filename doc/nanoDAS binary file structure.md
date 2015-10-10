## nanoDAS 4 channels binary file structure

### Structure

#### Header

/xfd x12   (begin message)  
/xff x2    (date block check)  
/xD1 /xD2 /xD3 /xD4 (date block)  
/x00 x6  

#### Measures

/xC1 /xC1 /xC1 /xC2 /xC2 /xC2 /xC3 /xC3 /xC3 /xC4 /xC4 /xC4 (3 bytes by channel for each measurement)  

#### Footer

/xfe x12   (end message)  


Example :
```
FD FD FD FD FD FD FD FD FD FD FD FD 
FF FF 07 DE 05 15 00 00 00 00 00 00
..... MEASURE 1....................
..... MEASURE 2....................
FE FE FE FE FE FE FE FE FE FE FE FE
```


### File size 

Size of a file : 36 bytes + n * 12 bytes
download time ≃ 1kb/sec

For 1 week at 60 sec integration period
n = 7 x 24 x60 = 10080
size = 36 + 10080 * 12 = 120996 bytes   ≃ 118kb
download time  ≃ 118 sec = 2min

For 1 empty file
size = 36 bytes

For 1 file with incorrect date block
size = 70 or 71 bytes ( depending on message)
