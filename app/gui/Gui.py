from tkinter import *
from tkinter.ttk import *
from tkinter.ttk import Style

class Gui:
    def initializeMainWindow(self,w):
        self.initMainWindow(w)

        self._maxColumns = 1000
        self._maxRows = 1000
        self._row = 0
        self.createDeviceWidgets()
        self.createEmulatorButton()

        self._row += 1
        self.createDatFileWidgets()
        
        self._row += 1
        self.createPatternsPanel()

        self._row += 1
        self.createInfoMessagesLabel()

    def initMainWindow(self, mainWindow):
        self.mainWindow = mainWindow
        self.mainWindow.title('Zip Knit')
        self.mainWindow.geometry("600x400")
        self.mainWindow.grid()
        self.mainWindow.grid_columnconfigure(1,weight=10)
        self.mainWindow.grid_columnconfigure(2,weight=1)
        self.mainWindow.resizable(True,True)
        
    def createDeviceWidgets(self):
        label = Label(self.mainWindow, text="Device path (port):")
        label.grid(column=0, row=self._row, sticky='W')
        
        entryText = StringVar()
        self.mainWindow.deviceEntry = Entry(self.mainWindow, textvariable=entryText)
        self.mainWindow.deviceEntry.grid(column=1,row=self._row,sticky='EW')
        self.mainWindow.deviceEntry.entryText = entryText
        
    def createEmulatorButton(self):
        caption = StringVar()
        self.emuButton = Button(self.mainWindow, textvariable = caption, command = self.mainWindow.emuButtonClicked)
        self.emuButton.caption = caption
        self.emuButton.grid(column=2,row=self._row, columnspan=2, sticky='EW')
        self.setEmuButtonStopped()
        
        but = Button(self.mainWindow, text = 'Help...', command = self.mainWindow.helpButtonClicked)
        but.grid(column=4,row=self._row, sticky='E')
        
    def createDatFileWidgets(self):
        label = Label(self.mainWindow, text="Dat file:")
        label.grid(column=0, row=self._row, sticky='W')
        
        entryText = StringVar()
        self.mainWindow.datFileEntry = Entry(self.mainWindow, textvariable=entryText)
        self.mainWindow.datFileEntry.grid(column=1,row=self._row,sticky='EW')
        self.mainWindow.datFileEntry.entryText = entryText

        self.chooseDatFileButton = Button(self.mainWindow, text="...", command = self.mainWindow.chooseDatFileButtonClicked)
        self.chooseDatFileButton.grid(column=2,row=self._row,sticky='W')

        self.reloadDatFileButton = Button(self.mainWindow, text="Reload file", command = self.mainWindow.reloadDatFileButtonClicked)
        self.reloadDatFileButton.grid(column=3,row=self._row,sticky='EW')
        
        but = Button(self.mainWindow, text="Store track", command = self.mainWindow.storeTrackButtonClicked)
        but.grid(column=4,row=self._row,sticky='EW')
        self.storeTrackButton = but
        
    def createInfoMessagesLabel(self):
        labelText = StringVar()
        style = Style()
        style.configure("BW.TLabel", foreground="white", background="blue")

        label = Label(self.mainWindow, anchor="w",style="BW.TLabel",textvariable=labelText)
        label.grid(column=0,row=self._row,columnspan=self._maxColumns,sticky='EW')
        label.caption = labelText
        self.mainWindow.infoLabel = label
        
    def createPatternsPanel(self):
        patternFrame = Frame(self.mainWindow)
        patternFrame.grid(column=0, row=self._row, columnspan = self._maxColumns,sticky='EWNS')
        self.mainWindow.grid_rowconfigure(self._row,weight=1)
        patternFrame.grid_columnconfigure(0,weight=0)
        patternFrame.grid_columnconfigure(1,weight=1)
        patternFrame.grid_rowconfigure(1,weight=1)
        
        listboxFrame = Frame(patternFrame)
        listboxFrame.grid(column=0, row=0, sticky='EWNS', rowspan=self._maxRows)
        scrollbar = Scrollbar(listboxFrame, orient=VERTICAL)
        listvar = StringVar()
        lb = Listbox(listboxFrame, listvariable=listvar, exportselection=0, width=40, yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)
        lb.items = ListboxVar(lb, listvar)
        scrollbar.pack(side=RIGHT, fill=Y)
        lb.pack(side=LEFT, fill=BOTH, expand=1)
        self.mainWindow.patternListBox = lb;

        textvar = StringVar()
        label = Label(patternFrame, anchor="w", textvariable = textvar)
        label.grid(column=1, row=0, sticky='EW')
        label.caption = textvar
        self.mainWindow.patternTitle = label
        
        self.insertBitmapButton = Button(patternFrame, text="Insert bitmap...", command = self.mainWindow.insertBitmapButtonClicked)
        self.insertBitmapButton.grid(column=2,row=0,sticky='EW')

        self.exportBitmapButton = Button(patternFrame, text="Export bitmap...", command = self.mainWindow.exportBitmapButtonClicked)
        self.exportBitmapButton.grid(column=3,row=0,sticky='EW')
        
        pc = ExtendedCanvas(patternFrame, bg='white')
        pc.grid(column=1, row=1, sticky='EWNS', columnspan=3)
        self.mainWindow.patternCanvas = pc
        
    def setEmuButtonStopped(self):
        b = self.emuButton
        b.caption.set("Start emulator...")
        
    def setEmuButtonStarted(self):
        b = self.emuButton
        b.caption.set("...stop emulator")
        
class ExtendedCanvas(Canvas):

    def getWidth(self):
        w = self.winfo_width()
        return w
        
    def getHeight(self):
        h = self.winfo_height()
        return h
        
    def clear(self):
        maxsize = 10000
        self.create_rectangle(0,0,maxsize, maxsize, width=0, fill=self.cget('bg'))
        
class ListboxVar:
    def __init__(self, listbox, stringvar):
        self._stringvar = stringvar
        self._listbox = listbox
        
    def set(self, list):
        self._listbox.delete(0, END)
        for item in list:
            self._listbox.insert(END, item)
