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

/* enums */
enum {PIOA = 0x1c};
enum {PIOB = 0x1e};
enum {DART1 = -2, DART2 = -3};
/* commands codes in hexadecimal */
enum Ordres {E0 = 0x3045, E1 = 0x3145, E2 = 0x3245,
             RI = 0x4952, SD = 0x4453, XB = 0x4258,
             XP = 0x5058, XN = 0x4E58, ZR = 0x525A,
             ZF = 0x465A, HE = 0x4548, WB = 0x4257,
             XS = 0x5358, RM = 0x4D52, EW = 0x5745,
             RW = 0x5752, SR = 0x5253, RL = 0x4C52,
             RV = 0x5652, SI = 0x4953, RL = 0x4C52,
             SH = 0x4853};

/* Assembler Fonctions */
extern int wtsdart1(void);
extern void rd_s232(void);
extern void watch_dog(void);
extern void disable_dog(void);
extern void sr_init(void);
extern void sr_read(void);
extern void sr_write(char *, char, char);
extern void testcts(void);

/* C functions */
void RSHandle(char);
void NMIHandle(void);
void DoItNow(WORD);
void Flash_Erase(void);
void Flash_Write(BYTE, WORD, BYTE);
void Flash_Sector_Erase(BYTE);
DWORD Z80toUnix(int, int, int, int, int, int);
void Read_Config(void);
void Write_Config(void);
BYTE Flash_READ(BYTE, WORD);
BYTE SecFlash_Read(BYTE, WORD);
void Centrage(void);
void Download(DWORD, DWORD);
void Write_Workbook_Event(BYTE);
void DWORD_in_ParamStr(int, DWORD);
void WORD _in_ParamStr(int, WORD);
void Default_Config(void);
void Data_Lost(void);
void Clear_s232(void);
void Sec_Flash_Write(BYTE, WORD, BYTE);
void delay_mus(BYTE);

/* Constants */
const BYTE HEADER_EPROM[] = {"NANODAS ROB-ASO"};

/* Variables [RS-232] */
BYTE combuff_a[MAX_BUFF].combuff_b[MAX_BUFF];
BYTE *s232;

/* Variables [NMI] */
BYTE NMI_i, NMI_j;
WORD NMD_Global_Addy;
WORD NMI_i_w;

/* Variables [Need'em] */
BYTE i,j;
BYTE Erase_Flag, DowLoad_Flag, Centrage_Flag, Flag,
                DLInterrupt_Flag, WriteData_Flag;

BYTE DLStart_Flag;
BYTE NextSector_Flag, RWrite_Flag, NMIoccur_Flag;

/* Variables [System] */
char flpioa, flpiob, cptpup, ctdog, flpout, addis ;
BYTE R_Echo, ValidO;

/* Variables [RSHandle] */
BYTE Order; /* Received RS232 Command */

/* Variables [Acquisition] */
DWORD Chan[4], ChanTmp; /* Channel Values */
BYTE LS590[20]; /* Individual counter values */
DWORD Now_Unix, Log_Unix;
BYTE Now_Byte1, Now_Byte2, Now_Byte3, Now_Byte4;
BYTE LMin, LSec;

/* Variables [Temp & Idle] */
BYTE NMI_Tempo;
BYTE logi_sect;
WORD logi_addy;
WORD Laps;
WORD mode_eveil;
BYTE Useldle_Flag, YetConnect_Flag;
BYTE *ctsval;

/* Variable [Workbook] */
char ParamStr[75];
BYTE ParamSize = 0;



