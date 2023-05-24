import sys
# from tkinter.font import ROMAN
from django.conf import settings
from django import http


class ErrHandle:
    """Error handling"""

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self):
        # Initialize a local error stack
        self.loc_errStack = []

    # ----------------------------------------------------------------------------------
    # Name :    Status
    # Goal :    Just give a status message
    # History:
    # 6/apr/2016    ERK Created
    # ----------------------------------------------------------------------------------
    def Status(self, msg):
        """Put a status message on the standard error output"""

        print(msg, file=sys.stderr)

    # ----------------------------------------------------------------------------------
    # Name :    DoError
    # Goal :    Process an error
    # History:
    # 6/apr/2016    ERK Created
    # ----------------------------------------------------------------------------------
    def DoError(self, msg, bExit = False):
        """Show an error message on stderr, preceded by the name of the function"""

        # Append the error message to the stack we have
        self.loc_errStack.append(msg)
        # get the message
        sErr = self.get_error_message()
        # Print the error message for the user
        print("Error: {}\nSystem:{}".format(msg, sErr), file=sys.stderr)
        # Is this a fatal error that requires exiting?
        if (bExit):
            sys.exit(2)
        # Otherwise: return the string that has been made
        return "<br>".join(self.loc_errStack)

    def get_error_message(self):
        """Retrieve just the error message and the line number itself as a string"""

        arInfo = sys.exc_info()
        if len(arInfo) == 3 and arInfo[0] != None:
            sMsg = str(arInfo[1])
            if arInfo[2] != None:
                sMsg += " at line " + str(arInfo[2].tb_lineno)
            return sMsg
        else:
            return ""

    def get_error_stack(self):
        return " ".join(self.loc_errStack)


class RomanNumbers:

    def romanToInt(self, sRomNum):
        """Convert roman (string) into number (int)"""

        # Initializations
        dic_roman = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000,
                     'IV':4,'IX':9,'XL':40,'XC':90,'CD':400,'CM':900}
        i = 0
        num = 0
        rom_size = 0

        # Change 'U' into 'V'
        sRomNum = sRomNum.replace("U", "V")

        while i < len(sRomNum):
            if i+1<len(sRomNum) and sRomNum[i:i+2] in dic_roman:
                num += dic_roman[sRomNum[i:i+2]]
                rom_size = 2
            else:
                num += dic_roman[sRomNum[i]]
                rom_size = 1
            i += rom_size

        # REturn the value that we found
        return num

    def intToRoman(self, num):
        """Convert number (int) into roman (string)"""

        val = [ 1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1 ]
        syb = [ "M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I" ]
        sRomNum = ''
        i = 0
        while  num > 0:
            for _ in range(num // val[i]):
                sRomNum += syb[i]
                num -= val[i]
            i += 1

        # Return the Roman Number string that has been built
        return sRomNum

