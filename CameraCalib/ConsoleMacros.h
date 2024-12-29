#pragma once



#define ESC "\x1b"
#define CSI "\x1b["

#define COL(col) CSI col "m"
#define COLD CSI "39m"
#define CRC(c) CRP c CSI "0J"
#define CRCD CRC("")
#define CSP CSI "s"
#define CRP CSI "u"
#define CUL(c) CSI "4m" c CSI "24m"