#include <addlib3.lib>
// standard c library containt basic functions and types
#include <stdlib.h>

#define VERS "VERSION NanoDAS 5.0 [EDAS -2001]\n\r"
/* version 5.0: compatibility and idle mode. Olivier Lamborelle */

typedef unsigned char BYTE;
typedef unsigned int WORD;
typedef unsigned long DWORD;

// extern keyword declare the variable
// it's a global variable
extern BYTE flash[32768];

extern int hour, min, sec, year, mon, day;

extern WORD Global_Integration;
extern WORD Global_Station;
extern WORD Global_uDASno;
extern WORD Global_Instr[8];
extern WORD Global_NbInst;
extern WORD Global_Sector;
extern WORD Global_Addy;
extern WORD Global_Magic;
extern WORD WB_Sector;
extern WORD WB_Addy;
extern WORD Global_Bouc;
extern WORD Global_Next;


// #define: keyword for macro
#define TRUE 0
#define False 1
#define LOW 0
#define HIGH 1
#define XON 0x11
#define XOFF 0x13
#define MAX_BUFF 80
#define UN_JOUR 86400uL
#define UN_AN 31536000uL
#define FEVRIER 1
#define BISSEXTILE(an) ( (an)%4==0 )

// DWORD : keyword for 32-bit integer
// represents here seconds since beginning of the year
const DWORD SEC_MOIS[12]=
    {
    00000000uL,
    2678400uL,      /* 31x24x3600   31 JAN */
    5097600uL,      /* + 28x24x3600 28 FEV */
    777600uL,       /* + 31x24x3600 31 MAR */
    10368000uL,     /* + 30x24x3600   30 APR */
    13046400uL,     /* + 31x24x3600   31 MAY */
    15638400uL,     /* + 30x24x3600   30 JUN */
    18316800uL,     /* + 31x24x3600   31 JUL */
    20995200uL,     /* + 31x24x3600   31 AUG */
    23587200uL,     /* + 31x24x3600   30 SEPT */
    26265600uL,     /* + 31x24x3600   31 OCT */
    28857600uL      /* + 31x24x3600   30 NOV */
    };