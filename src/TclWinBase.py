"""My Version of using Tkinter
"""
import tkinter as tki

class TclWinBaseUsageException(BaseException):
    """Exception für Nutzungsfehler dieses Moduls
    """
    def __init__(self, arg):
        self.args = arg


class TclWinBase(tki.Frame):
    """base class for tcl driven windows
    inherit this for your own windows
    """

    def mainloop(self):
        """ Enter the main loop"""
        self.root.mainloop()

    def __init__(self, title):
        #NoDefaultRoot()
        self.root = tki.Tk()   
        super().__init__(self.root, padx=5, pady=5)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(True, True)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.make_gui(title)
        self.loaded()

    def setwintitle(self, title):
        """Sets the title of your main window
        """
        self.root.title(title)

    def loaded(self):
        raise TclWinBaseUsageException("Override me! Always override loaded method")

    def make_gui(self, title):
        raise TclWinBaseUsageException("Override me! Alwaya override make_gui method")

    def maketext(self, lcol=0, lrow=0, erow=0, ecol=1, caption='', width=None, **options):
        """create a multiple single line text widget with a label/caption in another column
        """
        tki.Label(self, text=caption).grid(row=lrow, column=lcol, sticky=NE)
        entry = tki.Text(self, **options)
        if width:
            entry.config(width=width)
    
        entry.grid(row=erow, column=ecol, sticky=W)
        return entry

    def makeentry(self, lcol=0, lrow=0, erow=0, ecol=1, caption='', width=None, **options):
        """create a single line text entry widget with a label"""
        tki.Label(self, text=caption).grid(row=lrow, column=lcol, sticky=tki.E)
        entry = tki.Entry(self, **options)
        if width:
            entry.config(width=width)
    
        entry.grid(row=erow, column=ecol, sticky=tki.W)
        return entry

    def set_entry_text(self, entry, text):
        """Set text in text entry to a given text"""
        entry.delete(0, END)
        entry.insert(END, text)

    def makecheck(self, ecol=0, erow=0, caption='', **options):
        """create a checkbox with a label"""
        cb = tki.Checkbutton(self, text=caption, **options)
        cb.grid(row=erow, column=ecol, sticky=tki.W)
        return cb

    def makebutton(self, erow=0, ecol=0, caption='Button', 
                   width=None, cmd=None, sticky=tki.W, **options):
        """create a button widget"""
        bu = tki.Button(self,
                        text=caption,
                        command=cmd,
                        **options)
        
        bu.grid(row=erow, column=ecol, sticky=sticky)

        return bu

    def makecanvas(self, erow=0, ecol=0, rspan=1, cspan=1, sticky=tki.NSEW, **options):
        """create a canvas widget"""
        ca = tki.Canvas(self, **options)
        ca.grid(row=erow, column=ecol,
                columnspan=cspan, rowspan=rspan, sticky=sticky)

        return ca

    """create a list widgt in the current window"""
    def makelist(self, lcol=0, lrow=0, erow=0, ecol=1, caption='', width=None,
                 scrollvert=True, scrollhor=False,
                 **options):
        
        tki.Label(self, text=caption).grid(row=lrow, column=lcol, sticky=NE)
        
        if scrollvert == True:
            yScroll = tki.Scrollbar(self, orient=VERTICAL)
            yScroll.grid(row=erow, column=ecol+1, sticky=N+S)
            
        if scrollhor == True:
            xScroll = tki.Scrollbar(self, orient=HORIZONTAL)
            xScroll.grid(row=erow+1, column=ecol, sticky=E+W)

        lst = tki.Listbox(self, **options)
        lst.grid(row=erow, column=ecol)
        
        if scrollvert == True:
            lst.config(yscrollcommand=yScroll.set)
            yScroll['command'] = lst.yview

        if scrollhor == True:
            lst.config(xscrollcommand=xScroll.set)
            xScroll['command'] = lst.xview

        if width:
            lst.config(width=width)


        return lst

    def getvar(self, defval):
        t = type(defval)

        if t == str:
            answ = tki.StringVar()
            answ.set(defval)
        elif t == int:
            answ = tki.IntVar()
            answ.set(defval)
        elif t == float:
            answ = tki.DoubleVar()
            answ.set(defval)
        else:
            answ = tki.StringVar()

        return answ    
        

