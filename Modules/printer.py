import numpy as np
import pprint
import os,sys
import win32print

pp = pprint.PrettyPrinter()
PrinterName = win32print.GetDefaultPrinter()

LINELEN = 80
PGHEIGHT= 60


class Queue:
    def __init__(self,Channel,Testing = False) -> None:
        self.Channel = Channel
        self.Indent  = 4
        self.Testing = Testing
        self._ResetPage()

    
    def _ResetPage(self):
        self._Page = np.full((PGHEIGHT,LINELEN),' ')
        self._LineHeader = 0
        self._CrntPerson = ""
        self._CrntDate   = ""

        # Add the header
        self._AddToLine(self.Channel.center(LINELEN),Indent=False)

    def _SanatiseText(self,Text):
        CleanText = []
        for Chr in Text:
            if 0 <= ord(Chr) <= 127:
                CleanText.append(Chr)

        return ''.join(CleanText)

    def _CheckAvaliableSpace(self,Space):
        if (self._LineHeader + Space) >= PGHEIGHT:    # If the space needed is too big to fit on page
            self.Print()                    # Then print the print
            self._ResetPage()               # and reset it's contents.
            
    def _AddToLine(self,Text,*,Indent=True):
        if Indent:
            Offset = self.Indent
        else:
            Offset = 0
        
        if self._LineHeader >= PGHEIGHT:    # If the space needed is too big to fit on page
            self.Print()                    # Then print the print
            self._ResetPage()               # and reset it's contents.
        
        if LINELEN < (len(Text) + Offset):
            raise ValueError
        
        for x,Chr in enumerate(list(Text)):
            self._Page[self._LineHeader,x + Offset] = Chr

        self._LineHeader += 1
        


    def Add(self,Text,Time,Author):
        Text = self._SanatiseText(Text)
        
        if not Text:    # If text has zero length
            return      # Then return
        
        if Author != self._CrntPerson:                      # If a different person is talking
                
            if Time.strftime("%m/%d/%Y") != self._CrntDate: # and if the day has changed
                self._CrntDate = Time.strftime("%m/%d/%Y")  # and include the date in the time
                
                self._CheckAvaliableSpace(3)                # Check if there is enough space
                self._AddToLine(self._CrntDate.center(LINELEN),Indent=False)
#                                                           #Then add the date, centered to the page width
            
            DateFormat = '[{Time}] {Author}'            # don't include the date

            Header = (DateFormat.format(                # Otherwise, Create a User header
                Time    = Time.strftime("%H:%M:%S"),    # with the Time,
                Date    = Time.strftime("%m/%d/%Y"),    # Date,
                Author  = Author))                      # and Author

            self._CheckAvaliableSpace(2)                # Check if there isn't enough space
            
            self._AddToLine('',Indent=False)            # Then add a blank line before
            self._AddToLine(Header,Indent=False)        # Add it to the current line
            self._CrntPerson = Author                   # Set the current message holder to the author
            
        if '\n' in Text:                    # If there is a new line
            for Line in Text.split('\n'):   # Split the text into individual lines
                self.Add(Line,Time,Author)  # Then add it each as it's own messsage
            return

        ELength = LINELEN-self.Indent           # Effective Line Length
        if len(Text) > ELength:                 # If text won't fit on page
            Lines = (len(Text) // ELength) + 1  # Calculate how many lines are needed
            Text = list(Text)                   # Convert Text to a list to allow insertions
            for x in range(Lines):              # Then for each of those lines
                Text.insert(ELength*x,'\n')     # Insert a \n where a new line should begin
            self.Add(''.join(Text),Time,Author) # And treat it as a new message,
            return                              # As it should be seperated out by the \n handler

        self._AddToLine(Text)


    def Print(self):
        Text = self._JoinArray()
        
        Bytes = Text.encode()
        
        if self.Testing:
            print('Printing:')
            print(Text)
            return
        
        hPrinter = win32print.OpenPrinter (PrinterName)
        try:
            hJob = win32print.StartDocPrinter (hPrinter, 1, (self.Channel, None, "TEXT"))
            try:
                win32print.StartPagePrinter (hPrinter)
                win32print.WritePrinter (hPrinter, Bytes)
                win32print.EndPagePrinter (hPrinter)
            finally:
                win32print.EndDocPrinter (hPrinter)
        finally:
            win32print.ClosePrinter (hPrinter)
    
    def _JoinArray(self):
        Text = ""
        for y in range(PGHEIGHT):
            for x in range(LINELEN):
                Text += self._Page[y,x]
            Text += '\n'
        return Text
    