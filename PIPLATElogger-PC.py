"""
File: PIPLATElogger.py
Author: Jerry Wasinger
Date: December 13th, 2025
Description: Windows based data logger the interfaces to Pi-Plates through the BRIDGEplate
Dependent on packages pyserial, Pmw
"""

import time
import re
import datetime
import os
import subprocess
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import sys
from tkinter import *
import webbrowser

try:
    import Pmw
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pmw"])
        print(f"You need to restart the program")
        sys.exit()
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Pmw: {e}")
        sys.exit()

try:
    import serial
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
        print(f"You need to restart the program")
        sys.exit()
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pySerial: {e}")
        sys.exit()
    
import serial.tools.list_ports
    
Version = "BP-1.0"

def extract_vid_pid_from_hwid(hwid):
    """Extract VID and PID from hardware ID string"""
    if not hwid:
        return None, None
    # Look for VID pattern
    vid_match = re.search(r'VID_([0-9A-Fa-f]{4})', hwid)
    vid = vid_match.group(1).upper() if vid_match else None
    # Look for PID pattern
    pid_match = re.search(r'PID_([0-9A-Fa-f]{4})', hwid)
    pid = pid_match.group(1).upper() if pid_match else None
    return vid, pid

def find_ports_by_vid_pid(target_vid, target_pid):
    """Find COM ports by VID and PID combination"""
    matching_ports = []
    
    try:
        available_ports = serial.tools.list_ports.comports()    
        for port in available_ports:
            vid = None
            pid = None
            # Try to get VID/PID directly from pyserial
            if hasattr(port, 'vid') and port.vid is not None:
                vid = f"{port.vid:04X}"
            if hasattr(port, 'pid') and port.pid is not None:
                pid = f"{port.pid:04X}"
            # If not available directly, parse from hardware ID
            if not vid or not pid:
                if port.hwid:
                    parsed_vid, parsed_pid = extract_vid_pid_from_hwid(port.hwid)
                    if parsed_vid and not vid:
                        vid = parsed_vid
                    if parsed_pid and not pid:
                        pid = parsed_pid
            
            # Check if this port matches the target VID/PID
            if vid == target_vid.upper() and pid == target_pid.upper():
                matching_ports=port.device 
    except Exception as e:
        print(f"Error searching COM ports: {e}") 
    return matching_ports

def CMD(cmd):
    global ser
    cmd+="\n"							#add newline character
    ser.write(cmd.encode('utf-8'))
    xresp = str(ser.read_until(),'utf-8')
    xresp2=xresp.replace("\r", "")		#strip off CR if present
    xresp3=xresp2.replace("\n", "")		#strip off LF if present
    return xresp3


################################################################################
############### Start Program! #################################################
################################################################################
   

# define options for opening or saving a log file
newlogfile_opt = options = {}
options['defaultextension'] = '.csv'
options['filetypes'] = [('log files', '.csv')]
options['title'] = 'Open new log file'

# define options for opening or saving an existing log file
xlogfile_opt = options = {}
options['defaultextension'] = '.csv'
options['filetypes'] = [('log files', '.csv')]
options['title'] = 'Open existing log file'

# define options for opening or saving a setup file
setupfile_opt = options = {}
options['defaultextension'] = '.stp'
options['filetypes'] = [('setup files', '.stp')]
options['title'] = 'Open setup file'


def NewLogFile():
    global logFile, lfOpen, fName
    if (Logging==False):
        fName=''
        fName=asksaveasfile(mode='w',**newlogfile_opt)
        if ((fName!=None) and ('.csv' in fName.name)):
            lfOpen=True   

def NewSetupFile():
    suFilename=asksaveasfile(mode='w',**setupfile_opt)
    if ((suFilename!=None) and ('.stp' in suFilename.name)):
        sufile=open(suFilename.name,'w')
        desc=range(8)
        setup=''
        for i in range(8):
            if (DAQCpresent[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'
        for i in range(8):
            if (DAQC2present[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'
        for i in range(8):
            if (THERMOpresent[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'    
        for i in range(8):
            if (CURRENTpresent[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'          
        for i in range(8):
            if (ADCpresent[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'              
        for i in range(8):
            if (DAQCpresent[i]==1):
                desc=DAQCo[i].a2dGetLabels()
                for k in range(8):
                    setup= setup+desc[k]+','
                desc=DAQCo[i].dinGetLabels()
                for k in range(8):
                    setup = setup+desc[k]+','
                desc=DAQCo[i].a2dGetStates()
                for k in range(8):
                    setup= setup+str(desc[k])+','
                desc=DAQCo[i].dinGetStates()
                for k in range(8):
                    setup = setup+str(desc[k])+','         
        for i in range(8):
            if (DAQC2present[i]==1):
                desc=DAQC2o[i].a2dGetLabels()
                for k in range(8):
                    setup= setup+desc[k]+','
                desc=DAQC2o[i].dinGetLabels()
                for k in range(8):
                    setup = setup+desc[k]+','
                desc=DAQC2o[i].a2dGetStates()
                for k in range(8):
                    setup= setup+str(desc[k])+','
                desc=DAQC2o[i].dinGetStates()
                for k in range(8):
                    setup = setup+str(desc[k])+',' 
        desc=range(12)
        for i in range(8):
            if (THERMOpresent[i]==1):
                desc=THERMOo[i].TGetLabels()
                for k in range(12):
                    setup= setup+desc[k]+','
                desc=THERMOo[i].TGetStates()
                for k in range(12):
                    setup = setup+str(desc[k])+',' 
        desc=range(8)                    
        for i in range(8):
            if (CURRENTpresent[i]==1):
                desc=CURRENTo[i].IGetLabels()
                for k in range(8):
                    setup= setup+desc[k]+','
                desc=CURRENTo[i].IGetStates()
                for k in range(8):
                    setup = setup+str(desc[k])+','
        desc=range(12)
        desc2=range(4)                                     
        for i in range(8):
            if (ADCpresent[i]==1):
                desc=ADCo1[i].a2dGetLabels()
                for k in range(12):
                    setup= setup+desc[k]+','
                desc2=ADCo2[i].dinGetLabels()
                for k in range(4):
                    setup = setup+desc2[k]+','
                desc2=ADCo2[i].IGetLabels()
                for k in range(4):
                    setup = setup+desc2[k]+','                
                desc=ADCo1[i].a2dGetStates()
                for k in range(12):
                    setup= setup+str(desc[k])+','
                desc2=ADCo2[i].dinGetStates()
                for k in range(4):
                    setup = setup+str(desc[k])+','      
                desc2=ADCo2[i].IGetStates()
                for k in range(4):
                    setup = setup+str(desc[k])+','   
                    
        # setup = setup + str(AoutSignal.get()) + ',' + str(DoutSignal.get())+ ','
        setup = setup + SampleCount.get() + ',' + SamplePeriod.get()
        sufile.write(setup)
        sufile.write('\n')      
        sufile.close()


def OpenSetupFile():
    suFilename = askopenfile(**setupfile_opt)
    if ((suFilename != None) and ('.stp' in suFilename.name)):    
        sufile=open(suFilename.name,'r')
        setup=''
        setup=sufile.read()
        sufile.close()
        setup=setup[:-1]
        setupList=setup.split(",")
        N=40
        current=list(range(N))
        for i in range(8):
            if (DAQCpresent[i]==1):
                current[i]=str(i)
            else:
                current[i]='X'  
        for i in range(8):
            if (DAQC2present[i]==1):
                current[i+8]=str(i)
            else:
                current[i+8]='X'  
        for i in range(8):
            if (THERMOpresent[i]==1):
                current[i+16]=str(i)
            else:
                current[i+16]='X'   
        for i in range(8):
            if (CURRENTpresent[i]==1):
                current[i+24]=str(i)
            else:
                current[i+24]='X'     
        for i in range(8):
            if (ADCpresent[i]==1):
                current[i+32]=str(i)
            else:
                current[i+32]='X'
                
        setup=setupList[0:N]
        if (setup != current):
            messagebox.showwarning('Load Setup','Setup file does NOT match your hardware.')
        else:
            k=N
            dBlock=range(8)
            for i in range(8):
                if (DAQCpresent[i]==1):
                    sBlock=setupList[k:k+8]
                    DAQCo[i].a2dSetLabels(sBlock)        
                    sBlock=setupList[k+8:k+16]
                    DAQCo[i].dinSetLabels(sBlock)
                    sBlock=setupList[k+16:k+24]
                    DAQCo[i].a2dSetStates(sBlock)        
                    sBlock=setupList[k+24:k+32]
                    DAQCo[i].dinSetStates(sBlock)                
                    k+=32
            for i in range(8):
                if (DAQC2present[i]==1):
                    sBlock=setupList[k:k+8]
                    DAQC2o[i].a2dSetLabels(sBlock)        
                    sBlock=setupList[k+8:k+16]
                    DAQC2o[i].dinSetLabels(sBlock)
                    sBlock=setupList[k+16:k+24]
                    DAQC2o[i].a2dSetStates(sBlock)        
                    sBlock=setupList[k+24:k+32]
                    DAQC2o[i].dinSetStates(sBlock)                
                    k+=32  
            for i in range(8):
                if (THERMOpresent[i]==1):
                    sBlock=setupList[k:k+12]
                    THERMOo[i].TSetLabels(sBlock)        
                    sBlock=setupList[k+12:k+24]
                    THERMOo[i].TSetStates(sBlock)                  
                    k+=24
            for i in range(8):
                if (CURRENTpresent[i]==1):
                    sBlock=setupList[k:k+8]
                    CURRENTo[i].ISetLabels(sBlock)        
                    sBlock=setupList[k+8:k+16]
                    CURRENTo[i].ISetStates(sBlock)                  
                    k+=16
            for i in range(8):
                if (ADCpresent[i]==1):
                    sBlock=setupList[k:k+12]
                    ADCo1[i].a2dSetLabels(sBlock)
                    sBlock=setupList[k+12:k+16]
                    ADCo2[i].dinSetLabels(sBlock)
                    sBlock=setupList[k+16:k+20]
                    ADCo2[i].ISetLabels(sBlock)
                    sBlock=setupList[k+20:k+32]
                    ADCo1[i].a2dSetStates(sBlock)
                    sBlock=setupList[k+32:k+36]
                    ADCo2[i].dinSetStates(sBlock)                    
                    sBlock=setupList[k+36:k+40]
                    ADCo2[i].ISetStates(sBlock)                      
                    k+=40
            SampleCount.set(setupList[k])
            SamplePeriod.set(setupList[k+1]) 
            
def StartLog():
    global logFile, lfOpen, Logging, fName, SampleC, logHeader, DAQC2o, THERMOo
    if ((lfOpen) and  (Logging==False)):
        root.wm_title("Pi-Plates Data Logger - LOGGING")

        Header="Date/Time,"
        for i in range(8):
            if (DAQC2present[i]==1):
                desc=['','','','','','','','']
                desc=DAQC2o[i].a2dDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC2-'+str(i)+'-'+desc[k]+','
                desc=['','','','','','','','']
                desc=DAQC2o[i].dinDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC2-'+str(i)+'-'+desc[k]+','         
        for i in range(8):
            if (DAQCpresent[i]==1):
                desc=['','','','','','','','']
                desc=DAQCo[i].a2dDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC-'+str(i)+'-'+desc[k]+','
                desc=['','','','','','','','']
                desc=DAQCo[i].dinDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC-'+str(i)+'-'+desc[k]+','                       
        for i in range(8):
            if (THERMOpresent[i]==1):
                desc=['','','','','','','','','','','','']
                desc=THERMOo[i].TDescriptors()
                for k in range(12):
                    if (desc[k] != ''):
                        Header= Header+'THERMO-'+str(i)+'-'+desc[k]+','

        for i in range(8):
            if (CURRENTpresent[i]==1):
                desc=['','','','','','','','']
                desc=CURRENTo[i].IDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'CURRENT-'+str(i)+'-'+desc[k]+','
        for i in range(8):
            if (ADCpresent[i]==1):
                desc=['','','','','','','','','','','','']
                desc=ADCo1[i].a2dDescriptors()
                for k in range(12):
                    if (desc[k] != ''):
                        Header= Header+'ADC-'+str(i)+'-'+desc[k]+','
                desc=['','','','']
                desc=ADCo2[i].dinDescriptors()
                for k in range(4):
                    if (desc[k] != ''):
                        Header= Header+'ADC-'+str(i)+'-'+desc[k]+','
                desc=['','','','']
                desc=ADCo2[i].IDescriptors()
                for k in range(4):
                    if (desc[k] != ''):
                        Header= Header+'ADC-'+str(i)+'-'+desc[k]+','                        

        Header = Header[:-1] 
        logHeader=Header
        if (lfOpen):
            logFile=open(fName.name,'w')
            logFile.write(Header)
            logFile.write('\n')    
        Logging=True   
        SampleC=int(SampleCount.get())
    else:
        messagebox.showerror(
            "Logging",
            "You must specify a log file before you can start logging"
        )
    
def StopLog():
    global logFile, lfOpen, Logging
    if (Logging):
        Logging=False
        root.wm_title("Pi-Plates Data Logger")
        if (lfOpen):
            logFile.close()
            lfOpen=False
    
def About():
    Pmw.aboutversion(str(Version))
    Pmw.aboutcopyright('Copyright Wallyware, inc 2026\nAll rights reserved')
    Pmw.aboutcontact(
        'For help with this application contact:\n' +
        'support@pi-plates.com'
    )
    about = Pmw.AboutDialog(root, applicationname = 'PIPLATElogger')
    about.withdraw()
    root.eval(f'tk::PlaceWindow {str(about)} center')
    about.show() 

def Docs():   
    webbrowser.open("PIPLATElogger-Documentation-v2.0.pdf")

def License():   
    webbrowser.open("GNUpublicLicense.pdf")
    
def shutDown():
    global lfOpen, Logging
    StopLog()
    if (lfOpen):
        logFile.close()   
    root.destroy()

    
#Configure: Dialog box to get sampling parameters that holds focus until closed.    
def Configure():
    global icon
    if (Logging==False):
        cBox=Toplevel()    
        cBox.transient(master=root)
        cBox.wm_title("Logging Setup")   
        cBox.wm_iconphoto(False, icon)
        cBox.focus_set()

        sP=Label(cBox,text='Sample Period in Seconds (Minimum is '+str(round(SampleTmin,4))+'):', padx=2, pady=2)
        sP.grid(row=0,column=0,sticky="e")
        sPval=Entry(cBox,width=8,textvariable=SamplePeriod)
        sPval.grid(row=0,column=1,sticky="w")
        
        sC=Label(cBox,text="Sample Count:", padx=2, pady=2)
        sC.grid(row=1,column=0,sticky="e")
        sCval=Entry(cBox,width=8,textvariable=SampleCount)
        sCval.grid(row=1,column=1,sticky="w")

        sD1=Label(cBox,text="Log Duration in seconds = ", pady=20)
        sD1.grid(row=2,column=0,sticky="e")
        sD2=Label(cBox,textvariable=sDval, pady=20)
        sD2.grid(row=2,column=1,sticky="w")
    
        sB=Button(cBox, text='Close', command=cBox.destroy)
        sB.grid(row=3, columnspan=2, pady=4)
        
        cBox.grab_set()
        center(cBox)
        root.wait_window(cBox)

#doUpdates: a recurring routine to update the value of the displayed test duration value
def doUpdates():
    root.after(500,doUpdates)   
    try:
        sDval.set(str(round(float(SamplePeriod.get())*float(SampleCount.get()),2)))
    except ValueError:
        sDval.set('0')    

#ViewLog: Functions for providing different methods of examining data        
def ViewLog():
    global Logging, fName 

    def vPlot():
        pFile=getFile()
        if (pFile==''):
            return
        else:
            os.system('python loggerPLOT.py ' + pFile)
            vBox.destroy()
          
    def vFile():
        pFile=getFile()
        if (pFile==''):
            return
        else:
            os.system('notepad.exe ' + pFile)
            vBox.destroy()
            
    def vSpreadsheet():  
        pFile=getFile()
        if (pFile==''):
            return
        else:
            webbrowser.open(pFile)
            vBox.destroy()
            
    def getFile():
        global Logging, fName
        # define options for opening an existing log file
        xlogfile_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('log files', '.csv')]
        options['title'] = 'Open existing log file'
        fLoop=True
        while (fLoop):
            xfName=''
            xfName=askopenfile(**xlogfile_opt)
            #xfName=xfName.name
            if ((xfName.name=='') or (xfName==None)):
                fLoop=False
                xfName=''
            else:
                if ((fName==xfName.name) and lfOpen):
                    messagebox.showerror('Log File','Viewing currently open log file is not allowed')
                else:
                    fLoop=False
                xfName=xfName.name
        return xfName
                  
    # define options for opening or saving a setup file
    viewWarning_opt = options = {}
    if (Logging==True):
        reply = messagebox.showwarning('Warning', 'Some viewing features may affect logging.',**viewWarning_opt)        
        #reply = askquestion('Warning', 'Some viewing features may affect logging.',**viewWarning_opt)
        if (reply=='cancel'):
            return

    vBox=Toplevel()    
    vBox.transient(master=root)
    vBox.wm_title("View")   
    vBox.focus_set()
    fBut=Button(vBox, text='View Log File', command=vFile)
    fBut.pack(fill=X, padx=4, pady=3)
    eBut=Button(vBox, text='Open Log File in Spreadsheet', command=vSpreadsheet)
    eBut.pack(fill=X, padx=4, pady=3)
    vBox.grab_set()
    vBox.wm_iconphoto(False, icon)
    root.eval(f'tk::PlaceWindow {str(vBox)} center')
    root.wait_window(vBox) 
  
    
def task():
    global logFile, lfOpen, Logging, fName, SampleC, SampleT, logHeader
    global theta, dnum
    try:
        SampleT=float(SamplePeriod.get())
        if (SampleT<SampleTmin):
            SampleT=SampleTmin
    except ValueError:
        SampleT=SampleTmin
    root.after(int(SampleT*1000),task)   
    logString=''
    dTypes=''
    #j=0
    # a=setCMD("Mp.toggleLED()")
    for i in range (0,8): #for DAQC2plates 0 through 7
        a2dvals=range(8)
        dinvals=range(8)
        if (DAQC2present[i]==1):
            #Retrieve and plot  values
            a2dvals=DAQC2o[i].a2dupdate() 
            dinvals=DAQC2o[i].dinupdate()          
            #Convert data to strings for log
            for k in range(8):
                if (a2dvals[k] != ''):
                    logString=logString+str(a2dvals[k])+','
                    #aChannelCount += 1
                    dTypes = dTypes+'a,'
            for k in range(8):
                if (dinvals[k] != ''):
                    logString=logString+str(dinvals[k])+','
                    #dChannelCount += 1
                    dTypes = dTypes+'d,'

    for i in range (0,8): #for DAQCplates 0 through 7
        a2dvals=range(8)
        dinvals=range(8)
        if (DAQCpresent[i]==1):
            #Retrieve and plot  values
            a2dvals=DAQCo[i].a2dupdate() 
            dinvals=DAQCo[i].dinupdate()          
            #Convert data to strings for log
            for k in range(8):
                if (a2dvals[k] != ''):
                    logString=logString+str(a2dvals[k])+','
                    #aChannelCount += 1
                    dTypes = dTypes+'a,'
            for k in range(8):
                if (dinvals[k] != ''):
                    logString=logString+str(dinvals[k])+','
                    #dChannelCount += 1
                    dTypes = dTypes+'d,'

    for i in range (0,8): #for THERMOplates 0 through 7
        tvals=range(12)
        if (THERMOpresent[i]==1):
            #Retrieve and plot  values
            tvals=THERMOo[i].Tupdate() 
         
            #Convert data to strings for log
            for k in range(12):
                if (tvals[k] != ''):
                    logString=logString+str(tvals[k])+','
                    #tChannelCount += 1
                    dTypes = dTypes+'t,'

    for i in range (0,8): #for CURRENTplates 0 through 7
        ivals=range(8)
        if (CURRENTpresent[i]==1):
            #Retrieve and plot  values
            ivals=CURRENTo[i].Iupdate() 
         
            #Convert data to strings for log
            for k in range(12):
                if (ivals[k] != ''):
                    logString=logString+str(ivals[k])+','
                    #tChannelCount += 1
                    dTypes = dTypes+'i,'

    for i in range (0,8): #for ADCplates 0 through 7
        a2dvals=range(12)
        dinvals=range(4)
        ivals=range(4)
        if (ADCpresent[i]==1):
            #Retrieve and plot  values
            a2dvals=ADCo1[i].a2dupdate() 
            ivals=ADCo2[i].Iupdate()
            dinvals=ADCo2[i].dinupdate()          
            #Convert data to strings for log
            for k in range(12):
                if (a2dvals[k] != ''):
                    logString=logString+str(a2dvals[k])+','
                    #aChannelCount += 1
                    dTypes = dTypes+'a,'
            for k in range(4):
                if (dinvals[k] != ''):
                    logString=logString+str(dinvals[k])+','
                    #dChannelCount += 1
                    dTypes = dTypes+'d,'
            for k in range(4):
                if (ivals[k] != ''):
                    logString=logString+str(ivals[k])+','
                    #dChannelCount += 1
                    dTypes = dTypes+'i,'         
                    
    for i in range (0,8): #for DIGIplates 0 through 7
        dvals=range(8)
        if (DIGIpresent[i]==1):
            #Retrieve and plot  values
            dvals=DIGIo[i].dinupdate()
            #Convert data to strings for log
            for k in range(8):
                if (dvals[k] != ''):
                    logString=logString+str(dvals[k])+','
                    #tChannelCount += 1
                    dTypes = dTypes+'d,'

    dtypes = dTypes[:-1]
    logString = logString[:-1]    
    logString = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+','+logString
    if (Logging and lfOpen):
        logFile.write(logString)
        logFile.write('\n')            
    if (Logging):
        SampleC -= 1
        root.wm_title("Pi-Plate Data Logger - LOGGING - "+str(SampleC)+" Samples and "+str(round(SampleT*SampleC,2))+" Seconds Remaining")
        if (SampleC==0):
            StopLog()
            messagebox.showinfo("Logging","Logging Complete")     
            
class daqcDASH:
    def __init__(self,frame,addr,type):
        self.a2d=range(8)
        self.din=range(8)    
        
        def deSelect():
            for i in range(0,8):
                self.a2d[i].deSelect()
                self.din[i].deSelect()
                
        def selectAll():
            for i in range(0,8):        
                self.a2d[i].Select()
                self.din[i].Select()
            
        self.addr=addr
        self.root=frame
        self.type=type
        
        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        
        self.a2d=list(range(8))
        self.din=list(range(8))

        for i in range(0,8):
            self.a2d[i]=ADC(self.root,self.addr,i,self.type)
            self.din[i]=DIN(self.root,self.addr,i,self.type)      
    
    def a2dupdate(self):
        vals=['','','','','','','','']
        for i in range(0,8):          
            vals[i]=self.a2d[i].update()
        return vals

    def dinupdate(self):
        vals=['','','','','','','','']
        for i in range(0,8):          
            vals[i]=self.din[i].update()
        return vals   

    def a2dDescriptors(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].descriptors()
        return vals   
        
    def dinDescriptors(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].descriptors()
        return vals   
        
    def a2dGetLabels(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].getLabel()
        return vals   
        
    def dinGetLabels(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].getLabel()
        return vals   

    def a2dGetStates(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].getState()
        return vals   
        
    def dinGetStates(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].getState()
        return vals     

    def a2dSetLabels(self,labels):
        self.vals=labels
        for i in range(0,8):
            self.a2d[i].setLabel(self.vals[i])
        return   
        
    def dinSetLabels(self,labels):
        self.vals=labels
        for i in range(0,8):    
            self.din[i].setLabel(self.vals[i])
        return   

    def a2dSetStates(self,states):
        self.vals=states
        for i in range(0,8):
            self.a2d[i].setState(self.vals[i])
        return   
        
    def dinSetStates(self,states):
        self.vals=states
        for i in range(0,8):    
            self.din[i].setState(self.vals[i])
        return               

class thermoDASH:
    def __init__(self,frame,addr,type):
        self.T=list(range(12))
        self.scale=StringVar()
        def deSelect():
            for i in range(0,12):
                self.T[i].deSelect()
                #self.dT[i].deSelect()
                
        def selectAll():
            for i in range(0,12):        
                self.T[i].Select()
        
        def setScale(val):
            self.scale.set(val)
        
        self.addr=addr
        self.root=frame
        self.type=type
        self.v = IntVar()
        self.scale=StringVar(self.root,'c')
        self.scale.set('c')

        v=IntVar()       

        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        #self.s1=Radiobutton(self.mFrame,text=u'\u00b0'+'C',variable=v, value=1 ,command=setScale('C'))
        self.s1=Radiobutton(self.mFrame,text=u'\u00b0'+'C',variable=self.scale, value='c')
        self.s1.grid(row=0, column=2, padx=4,pady=5)
        self.s2=Radiobutton(self.mFrame,text=u'\u00b0'+'F',variable=self.scale, value='f')
        self.s2.grid(row=0, column=3, padx=4,pady=5)        
        self.s3=Radiobutton(self.mFrame,text=u'\u00b0'+'K',variable=self.scale, value='k')
        self.s3.grid(row=0, column=4, padx=4,pady=5) 
        self.s1.select()
        self.s2.deselect()
        self.s3.deselect()
      
        self.T=list(range(12))

        for i in range(0,12):
            self.T[i]=TEMP(self.root,self.addr,i,self.type)
    
    def Tupdate(self):
        vals=['','','','','','','','','','','','']
        lscale=self.scale.get()
        for i in range(0,12):          
            vals[i]=self.T[i].update(lscale)
        return vals

    def TDescriptors(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.T[i].descriptors()
        return vals   
        #return vals   
        
    def TGetLabels(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.T[i].getLabel()
        return vals   

    def TGetStates(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.T[i].getState()
        return vals   

    def TSetLabels(self,labels):
        self.vals=labels
        for i in range(0,12):
            self.T[i].setLabel(self.vals[i])
        return   

    def TSetStates(self,states):
        self.vals=states
        for i in range(0,12):
            self.T[i].setState(self.vals[i])
        return          

class currentDASH:
    def __init__(self,frame,addr,type):
        self.I=list(range(8))
        self.scale=StringVar()
        def deSelect():
            for i in range(0,8):
                self.I[i].deSelect()
                
        def selectAll():
            for i in range(0,8):        
                self.I[i].Select()
        
        def setScale(val):
            self.scale=val
        
        self.addr=addr
        self.root=frame
        self.type=type        
        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='Black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)       
       
        self.I=list(range(8))

        for i in range(0,8):
            self.I[i]=AMPS(self.root,self.addr,i,type)
    
    def Iupdate(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,8):          
            vals[i]=self.I[i].update()
        return vals

    def IDescriptors(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,8):
            vals[i]=self.I[i].descriptors()
        return vals   
        
    def IGetLabels(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,8):
            vals[i]=self.I[i].getLabel()
        return vals   

    def IGetStates(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,8):
            vals[i]=self.I[i].getState()
        return vals   

    def ISetLabels(self,labels):
        self.vals=labels
        for i in range(0,8):
            self.I[i].setLabel(self.vals[i])
        return   

    def ISetStates(self,states):
        self.vals=states
        for i in range(0,8):
            self.I[i].setState(self.vals[i])
        return          

class adc1DASH:
    def __init__(self,frame,addr,type):
        self.a2d=range(12)
        
        def deSelect():
            for i in range(0,12):
                self.a2d[i].deSelect()
                
        def selectAll():
            for i in range(0,12):        
                self.a2d[i].Select()
            
        self.addr=addr
        self.root=frame
        self.type=type
        
        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        
        self.a2d=list(range(12))

        for i in range(0,12):
            self.a2d[i]=ADC(self.root,self.addr,i,self.type)    
    
    def a2dupdate(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):          
            vals[i]=self.a2d[i].update()
        return vals

    def a2dDescriptors(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.a2d[i].descriptors()
        return vals       
        
    def a2dGetLabels(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.a2d[i].getLabel()
        return vals   

    def a2dGetStates(self):
        vals=['','','','','','','','','','','','']
        for i in range(0,12):
            vals[i]=self.a2d[i].getState()
        return vals   
  
    def a2dSetLabels(self,labels):
        self.vals=labels
        for i in range(0,12):
            self.a2d[i].setLabel(self.vals[i])
        return   

    def a2dSetStates(self,states):
        self.vals=states
        for i in range(0,12):
            self.a2d[i].setState(self.vals[i])
        return   
        

class adc2DASH:
    def __init__(self,frame,addr,type):
        self.I=range(4)
        self.din=range(4)    
        
        def deSelect():
            for i in range(0,4):
                self.I[i].deSelect()
                self.din[i].deSelect()
                
        def selectAll():
            for i in range(0,4):        
                self.I[i].Select()
                self.din[i].Select()
            
        self.addr=addr
        self.root=frame
        self.type=type
        
        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        
        self.I=list(range(4))
        self.din=list(range(4))

        for i in range(0,4):
            self.I[i]=AMPS(self.root,self.addr,i,self.type)
            self.din[i]=DIN(self.root,self.addr,i,self.type)      
    
    def Iupdate(self):
        vals=['','','','']
        for i in range(0,4):          
            vals[i]=self.I[i].update()
        return vals

    def IDescriptors(self):
        vals=['','','','']
        for i in range(0,4):
            vals[i]=self.I[i].descriptors()
        return vals   
        return vals   
        
    def IGetLabels(self):
        vals=['','','','']
        for i in range(0,4):
            vals[i]=self.I[i].getLabel()
        return vals   

    def IGetStates(self):
        vals=['','','','']
        for i in range(0,4):
            vals[i]=self.I[i].getState()
        return vals   

    def ISetLabels(self,labels):
        self.vals=labels
        for i in range(0,4):
            self.I[i].setLabel(self.vals[i])
        return   

    def ISetStates(self,states):
        self.vals=states
        for i in range(0,4):
            self.I[i].setState(self.vals[i])
        return              
    
    def dinupdate(self):
        vals=['','','','']
        for i in range(0,4):          
            vals[i]=self.din[i].update()
        return vals   
        
    def dinDescriptors(self):
        vals=['','','','']
        for i in range(0,4):    
            vals[i]=self.din[i].descriptors()
        return vals            
        
    def dinGetLabels(self):
        vals=['','','','']
        for i in range(0,4):    
            vals[i]=self.din[i].getLabel()
        return vals   
        
    def dinGetStates(self):
        vals=['','','','']
        for i in range(0,4):    
            vals[i]=self.din[i].getState()
        return vals     
        
    def dinSetLabels(self,labels):
        self.vals=labels
        for i in range(0,4):    
            self.din[i].setLabel(self.vals[i])
        return    
        
    def dinSetStates(self,states):
        self.vals=states
        for i in range(0,4):    
            self.din[i].setState(self.vals[i])
        return

class digiDASH:
    def __init__(self,frame,addr,dtype):
        self.din=range(8)    
        
        def deSelect():
            for i in range(0,8):
                self.din[i].deSelect()
                
        def selectAll():
            for i in range(0,8):        
                self.din[i].Select()
            
        self.addr=addr
        self.root=frame
        self.type=dtype
        
        BG='#888FFF888'
        off=0
        self.mFrame=Frame(self.root,bg='black',bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        
        self.din=list(range(8))

        for i in range(0,8):
            self.din[i]=DIN(self.root,self.addr,i+1,self.type)      

    def dinupdate(self):
        vals=['','','','','','','','']
        for i in range(0,8):          
            vals[i]=self.din[i].update()
        return vals   
        
    def dinDescriptors(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].descriptors()
        return vals   
        
    def dinGetLabels(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].getLabel()
        return vals   
        
    def dinGetStates(self):
        vals=['','','','','','','','']
        for i in range(0,8):    
            vals[i]=self.din[i].getState()
        return vals     
        
    def dinSetLabels(self,labels):
        self.vals=labels
        for i in range(0,8):    
            self.din[i].setLabel(self.vals[i])
        return   
        
    def dinSetStates(self,states):
        self.vals=states
        for i in range(0,8):    
            self.din[i].setState(self.vals[i])
        return               
    
class ADC:
    def __init__(self,root,addr,channel,atype):
        self.addr=addr
        self.root=root
        self.chan=channel
        self.type=atype
        self.var=IntVar()   #This is the select button for each channel
        self.var.set(0)
        self.val=DoubleVar()
        self.color=PALETTE[channel%8]
        mheight=SLICE
        if(self.type==3):
            self.val.set(float(CMD("ADC.getADC("+str(self.addr)+','+str(self.chan)+')')))
            mheight=SLICE+13
        elif (self.type==2):
            self.val.set(float(CMD("DAQC2.getADC("+str(self.addr)+','+str(self.chan)+')')))
        else:
            self.val.set(float(CMD("DAQC.getADC("+str(self.addr)+','+str(self.chan)+')')))
        self.valstring=StringVar()
        #self.valstring.set(str(self.val.get()))
        self.valstring.set('off')        
        off=H-2-17*SLICE+self.chan*mheight
        BG='#000000000'
        #self.CWidth=int(.85*W+14)
        self.CWidth=int(.84*W+8)
        self.a2df=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.a2df.place(x=0,y=off,width=W,height=mheight)
        self.a2dc=Checkbutton(self.a2df,fg="Black",bg=BG,variable=self.var,onvalue = 1, offvalue = 0,command=self.cb)
        self.a2dc.grid(row=0,column=0,sticky="w")
        #self.var.set(0)
        if (self.type==3):
            if (self.chan<8):
                lString="SE Channel "
            else:
                lString="DE Channel "
        else:
            lString="A Channel "
        if (self.type==3 and self.chan>7):         
            self.a2dl = StringVar(root, value=lString+str(self.chan-8)+":")
        else:
            self.a2dl = StringVar(root, value=lString+str(self.chan)+":")
        self.a2dt = Label(self.a2df,textvariable=self.valstring,fg="White",bg=BG,width=5).grid(row=0,column=2,sticky="w")
        self.a2dtxt=Entry(self.a2df,textvariable=self.a2dl,fg="White",bg=BG,bd=0,relief="flat",borderwidth=0,highlightthickness=0,width=12)
        self.a2dtxt.grid(row=0,column=1,sticky="w")
        self.a2dcanvas=Canvas(self.a2df,bg=BG,width=self.CWidth,height=mheight,bd=0,relief="flat")
        self.a2dcanvas.grid(row=0,column=3,sticky="e")
        self.maxrange=self.CWidth
        self.log=list(range(self.maxrange))
        for i in range(self.maxrange):
            self.log[i]=0.0
        self.nextPtr=0

        
    def cb(self):
        if (self.var==1):
            a=1
            
    def deSelect(self):
        self.a2dc.deselect()

    def Select(self):
        self.a2dc.select()
        
        
    def update(self):
        if (self.var.get()==1):
            if (self.type==3):
                self.val.set(float(CMD("ADC.getADC("+str(self.addr)+','+str(self.chan)+')')))
            elif (self.type==2):
                self.val.set(float(CMD("DAQC2.getADC("+str(self.addr)+','+str(self.chan)+')')))
            else:
                self.val.set(float(CMD("DAQC.getADC("+str(self.addr)+','+str(self.chan)+')')))
            self.valstring.set(str("{:5.3f}".format(self.val.get())))
            self.log[self.nextPtr]=self.val.get()
            self.nextPtr=(self.nextPtr+1)%self.maxrange
            self.plot()
            return self.val.get()
        else:
            return ''

    def descriptors(self):
        if (self.var.get()==1):
            return self.a2dl.get()
        else:
            return ''

    def getLabel(self):
        return self.a2dl.get()

    def setLabel(self,label):
        self.a2dl.set(label)        
        
    def getState(self):
        return self.var.get()        
 
    def setState(self,state):
        if (state=='1'):
            self.a2dc.select()
        else:
            self.a2dc.deselect()
            
    def plot(self):
        points=list(range(2*self.CWidth))
        for i in range(self.CWidth):
            j=(self.nextPtr-1+self.CWidth+i)%self.CWidth
            if (self.type==2 or self.type==3):
                lval=int((self.log[j]+12)/24*(SLICE-2))
            else:
                lval=int(self.log[j]*(SLICE-2)/4.096)
            points[2*i]=i
            points[2*i+1]=SLICE-1-lval
        self.a2dcanvas.delete("all")
        self.a2dcanvas.create_line(points, fill=self.color,width=2)       
        
class DIN:
    def __init__(self,root,addr,channel,dtype):
        self.root=root
        self.addr=addr
        self.type=dtype
        self.chan=channel
        self.var=IntVar()
        self.var.set(0)    
        self.val=IntVar()
        self.color=PALETTE[channel%8]       
        if (self.type==4):
            #self.chan = self.chan+1
            self.val.set(int(CMD("DIGI.getDINbit("+str(self.addr)+','+str(self.chan)+')')))        
        elif (self.type==3):
            self.val.set(int(CMD("ADC.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
        elif (self.type==2):
            self.val.set(int(CMD("DAQC2.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
        else:
            self.val.set(int(CMD("DAQC.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
        self.valstring=StringVar()
        self.valstring.set('off')
        if (self.type == 4):
            mheight=DSLICE
            off=H-2-17*SLICE+(self.chan-1)*DSLICE
            #off=H-2-9*DSLICE+self.chan*DSLICE
        elif (self.type==3):
            off=H-2-9*SLICE+self.chan*ISLICE 
            mheight=ISLICE
        else:
            off=H-2-9*SLICE+self.chan*SLICE
            mheight=SLICE
        BG='#000000000'
        #self.CWidth=int(.85*W+14)  
        self.CWidth=int(.84*W+8)        
        self.dinf=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.dinf.place(x=0,y=off,width=W,height=mheight)
        self.dinc=Checkbutton(self.dinf,fg="Black",bg=BG,variable=self.var,command=self.cb)
        self.dinc.grid(row=0,column=0,sticky="w")
        self.dinl = StringVar(root, value="D Channel "+str(self.chan)+":")
        self.dint = Label(self.dinf,textvariable=self.valstring,fg="White",bg=BG,width=5)
        self.dint.grid(row=0,column=2,sticky="w")
        self.dintxt=Entry(self.dinf,textvariable=self.dinl,fg="White",bg=BG,bd=0,relief="flat",borderwidth=0,highlightthickness=0,width=12)
        self.dintxt.grid(row=0,column=1,sticky="w")
        self.dincanvas=Canvas(self.dinf,bg=BG,width=self.CWidth,height=mheight,bd=0,relief="flat")
        self.dincanvas.grid(row=0,column=3,sticky="e")
        self.maxrange=self.CWidth
        self.log=list(range(self.maxrange))
        for i in range(self.maxrange):
            self.log[i]=0.0
        self.nextPtr=0
        
    def cb(self):
        if (self.var==1):
            a=1  

    def deSelect(self):
        self.dinc.deselect()

    def Select(self):
        self.dinc.select()  
        
    def update(self):
        if (self.var.get()==1):
            if (self.type==4):
                self.val.set(int(CMD("DIGI.getDINbit("+str(self.addr)+','+str(self.chan)+')')))              
            elif (self.type==3):
                self.val.set(int(CMD("ADC.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
            elif (self.type==2):
                self.val.set(int(CMD("DAQC2.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
            else:
                self.val.set(int(CMD("DAQC.getDINbit("+str(self.addr)+','+str(self.chan)+')')))
            self.valstring.set(str(self.val.get()))
            self.log[self.nextPtr]=self.val.get()
            self.nextPtr=(self.nextPtr+1)%self.maxrange
            self.plot()
            return self.val.get()
        else:
            return ''

    def descriptors(self):
        if (self.var.get()==1):
            return self.dinl.get()
        else:
            return ''            

    def getLabel(self):
        return self.dinl.get()

    def setLabel(self,label):
        self.dinl.set(label)         

    def getState(self):
        return self.var.get()  

    def setState(self,state):
        if (state=='1'):
            self.dinc.select()
        else:
            self.dinc.deselect()
            
    def plot(self):
        points=list(range(2*self.CWidth))
        for i in range(self.CWidth):
            j=(self.nextPtr-1+self.CWidth+i)%self.CWidth
            lval=int(self.log[j]*(SLICE-3))
            points[2*i]=i
            points[2*i+1]=SLICE-1-lval
        self.dincanvas.delete("all")
        self.dincanvas.create_line(points, fill=self.color,width=2)

class TEMP:
    def __init__(self,root,addr,channel,type):
        self.addr=addr
        self.root=root
        self.chan=channel+1
        self.type=type
        self.var=IntVar()   #This is the select button for each channel
        self.var.set(0)
        self.val=DoubleVar()
        self.val.set(float(CMD('THERMO.getTEMP('+str(self.addr)+','+str(self.chan)+',"c")')))
        self.val.set(0)
        self.valstring=StringVar()
        self.valstring.set('off')
        self.color=PALETTE[channel%8]
        #self.valstring.set(str("{:4.3f}".format(self.val.get())))
        off=H-2-17*SLICE+(self.chan-1)*TSLICE
        BG='#000000000'
        #self.CWidth=int(.85*W+8)
        self.CWidth=int(.84*W+8)
        self.tf=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.tf.place(x=0,y=off,width=W,height=TSLICE)
        self.tc=Checkbutton(self.tf,fg="Black",bg=BG,variable=self.var,onvalue = 1, offvalue = 0,command=self.cb)
        self.tc.grid(row=0,column=0,sticky="w")
        self.var.set(0)
        self.tl = StringVar(root, value="T Channel "+str(self.chan)+":")
        self.tt = Label(self.tf,textvariable=self.valstring,fg="White",bg=BG,width=7).grid(row=0,column=2,sticky="w")
        self.ttxt=Entry(self.tf,textvariable=self.tl,fg="White",bg=BG,bd=0,relief="flat",borderwidth=0,highlightthickness=0,width=11)
        self.ttxt.grid(row=0,column=1,sticky="w")
        self.tcanvas=Canvas(self.tf,bg=BG,width=self.CWidth,height=TSLICE,bd=0,relief="flat")
        self.tcanvas.grid(row=0,column=3,sticky="e")
        self.maxrange=self.CWidth
        self.log=list(range(self.maxrange))
        for i in range(self.maxrange):
            self.log[i]=0.0
        self.nextPtr=0
        
    def cb(self):
        if (self.var==1):
            a=1
            
    def deSelect(self):
        self.tc.deselect()

    def Select(self):
        self.tc.select()              
        
    def update(self,scale):
        if (self.var.get()==1):
            self.val.set(float(CMD('THERMO.getTEMP('+str(self.addr)+','+str(self.chan)+',"'+scale+'")')))
            self.valstring.set(str("{:4.3f}".format(self.val.get())))
            self.log[self.nextPtr]=self.val.get()
            self.nextPtr=(self.nextPtr+1)%self.maxrange
            self.plot(scale)
            return self.val.get()
        else:
            return ''

    def descriptors(self):
        if (self.var.get()==1):
            return self.tl.get()
        else:
            return ''

    def getLabel(self):
        return self.tl.get()

    def setLabel(self,label):
        self.tl.set(label)        
        
    def getState(self):
        return self.var.get()        
 
    def setState(self,state):
        if (state=='1'):
            self.tc.select()
        else:
            self.tc.deselect()
            
    def plot(self,scale):
        points=list(range(2*self.CWidth))
        for i in range(self.CWidth):
            j=(self.nextPtr-1+self.CWidth+i)%self.CWidth
            if (scale=='c'):
                lval=int((self.log[j]+55)/180*(TSLICE-2))
            elif (scale=='f'):
                lval=int((self.log[j]+67)/325*(TSLICE-2))
            else:
                lval=int((self.log[j]-218)/180*(TSLICE-2))
            #lval=int(self.log[j]*(TSLICE-2)/4.096)
            points[2*i]=i
            points[2*i+1]=TSLICE-1-lval
        self.tcanvas.delete("all")
        self.tcanvas.create_line(points, fill=self.color,width=2)

class AMPS:
    def __init__(self,root,addr,channel,type):
        self.addr=addr
        self.root=root
        self.chan=channel+1
        self.type=type
        self.color=PALETTE[channel%8]
        self.var=IntVar()   #This is the select button for each channel
        self.var.set(0)
        self.val=DoubleVar()
        if (self.type==3):
            self.val.set(float(CMD("ADC.getADC("+str(self.addr)+','+str(self.chan)+')')))
        else:
            self.val.set(float(CMD("CURRENT.getI("+str(self.addr)+','+str(self.chan)+')')))
        self.val.set(0)
        self.valstring=StringVar()
        self.valstring.set('off')
        off=H-2-17*SLICE+(self.chan-1)*ISLICE
        BG='#000000000'
        #self.CWidth=int(.85*W+14)
        self.CWidth=int(.84*W+8)
        self.tf=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.tf.place(x=0,y=off,width=W,height=ISLICE)
        self.tc=Checkbutton(self.tf,fg="Black",bg=BG,variable=self.var,onvalue = 1, offvalue = 0,command=self.cb)
        self.tc.grid(row=0,column=0,sticky="w")
        self.var.set(0)
        self.tl = StringVar(root, value="4-20mA "+str(self.chan)+":")
        self.tt = Label(self.tf,textvariable=self.valstring,fg="White",bg=BG,width=5)
        self.tt.grid(row=0,column=2,sticky="w")
        self.ttxt=Entry(self.tf,textvariable=self.tl,fg="White",bg=BG,bd=0,relief="flat",borderwidth=0,highlightthickness=0,width=12)
        self.ttxt.grid(row=0,column=1,sticky="w")
        self.icanvas=Canvas(self.tf,bg=BG,width=self.CWidth,height=ISLICE,bd=0,relief="flat")
        self.icanvas.grid(row=0,column=3,sticky="e")
        self.maxrange=self.CWidth
        self.log=list(range(self.maxrange))
        for i in range(self.maxrange):
            self.log[i]=0.0
        self.nextPtr=0
        
    def cb(self):
        if (self.var==1):
            a=1
            
    def deSelect(self):
        self.tc.deselect()

    def Select(self):
        self.tc.select()              
        
    def update(self):
        if (self.var.get()==1):
            if (self.type==3):
                self.val.set(float(CMD("ADC.getADC("+str(self.addr)+','+str(self.chan)+')')))
            else:
                self.val.set(float(CMD("CURRENT.getI("+str(self.addr)+','+str(self.chan)+')')))
            self.valstring.set(str("{:4.3f}".format(self.val.get())))
            self.log[self.nextPtr]=self.val.get()
            self.nextPtr=(self.nextPtr+1)%self.maxrange
            self.plot()
            return self.val.get()
        else:
            return ''

    def descriptors(self):
        if (self.var.get()==1):
            return self.tl.get()
        else:
            return ''

    def getLabel(self):
        return self.tl.get()

    def setLabel(self,label):
        self.tl.set(label)        
        
    def getState(self):
        return self.var.get()        
 
    def setState(self,state):
        if (state=='1'):
            self.tc.select()
        else:
            self.tc.deselect()
          
    def plot(self):
        points=list(range(2*self.CWidth))
        for i in range(self.CWidth):
            j=(self.nextPtr-1+self.CWidth+i)%self.CWidth
            lval=int(self.log[j]*(ISLICE-2)/20.0)
            points[2*i]=i
            points[2*i+1]=ISLICE-1-lval
        self.icanvas.delete("all")
        self.icanvas.create_line(points, fill=self.color,width=2)  
        
def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


SampleT=0.2
theta=[0,0,0,0,0,0,0,0]  
dnum=[0,0,0,0,0,0,0,0]
SampleC=0
logFile=0
lfOpen=False
streamOpen=False
Logging=False
logHeader=''
streamer=0
fName=''

vid="2E8A"
pid="10E3"
matches = find_ports_by_vid_pid(vid,pid)
if (matches):
    ser = serial.Serial(matches, 115200, timeout=20) # Open port at 115200 baud, with a 20-second timeout (for slow sample rates)
else:
    print ("No COM port found with attached BRDGEplate.")
    print("Exiting program...")
    sys.exit(0)

ser.flush()
ser.reset_input_buffer()

root = Tk()
root.resizable(0,0)
icon = PhotoImage(file="icon32X32.png")
root.wm_iconphoto(False, icon)


menu=Menu(root)
root.wm_title("Pi-Plates Data Logger")

W=1280
H=720
SLICE=40
TSLICE=54
ISLICE=80
DSLICE=80

PALETTE=['#FFFFFF','#A52A2A','#FF0000','#FFA500','#FFFF00','#00FF00','#0000FF','#9400D3']
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
x = w/2 - W/2
y = h/2 - H/2
root.geometry("%dx%d+%d+%d" % (W,H,x, y))

center(root)

root.config(menu=menu)
filemenu = Menu(menu,tearoff=0)
menu.add_cascade(label="FILE", foreground='black',font="-weight bold", menu=filemenu)
filemenu.add_command(label="Save Setup", command=NewSetupFile)
filemenu.add_command(label="Load Setup", command=OpenSetupFile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=shutDown)

setupmenu = Menu(menu,tearoff=0)
menu.add_cascade(label="LOG SETUP", foreground='#8000FF',font="-weight bold", menu=setupmenu)
setupmenu.add_command(label="Open New File for Logging", command=NewLogFile)
setupmenu.add_command(label="Set Logging Parameters", command=Configure)

#menu.add_command(label="LOG SETUP",foreground='#8000FF',font="-weight bold", command=Configure)
menu.add_command(label="START", foreground='green',font="-weight bold", command=StartLog)
menu.add_command(label="STOP", foreground='red',font="-weight bold",command=StopLog)
menu.add_command(label="VIEW", foreground='blue',font="-weight bold",command=ViewLog)
helpmenu = Menu(menu,tearoff=0)
menu.add_cascade(label="HELP", foreground='black',font="-weight bold", menu=helpmenu)
helpmenu.add_command(label="Documentation", command=Docs)
helpmenu.add_command(label="Usage License", command=License)
helpmenu.add_command(label="About", command=About)

#def callback():
#    print ("click!")

notebook = Pmw.NoteBook(root,borderwidth=2,pagemargin=2)
notebook.pack(fill = 'both', expand = 1)

SampleTmin=0.01
focusSet=False
print()
print('Identifying and initializing Pi-Plates...')

DAQC2present=8*[False]
DAQC2o=list(range(8))
DAQC2FoundCount=0
for i in range (0,8):
    resp=CMD("DAQC2.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        DAQC2present[i]=True
        DAQC2FoundCount+=1     
        page = notebook.add('DAQC2-'+str(i))
        if (focusSet==False):
            notebook.tab('DAQC2-'+str(i)).focus_set()
            focusSet=True
        DAQC2o[i]=daqcDASH(page,i,2)
        SampleTmin+=0.15

DAQCpresent=8*[False]
DAQCo=list(range(8))
DAQCFoundCount=0
for i in range(8):
    resp=CMD("DAQC.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        DAQCpresent[i]=True
        DAQCFoundCount+=1   
        page = notebook.add('DAQC-'+str(i))
        if (focusSet==False):
            notebook.tab('DAQC-'+str(i)).focus_set()
            focusSet=True
        DAQCo[i]=daqcDASH(page,i,1)
        SampleTmin+=0.2

THERMOpresent=8*[False]
THERMOo=list(range(8))
THERMOFoundCount=0
for i in range (0,8):
    resp=CMD("THERMO.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        THERMOpresent[i]=True
        THERMOFoundCount+=1   
        page = notebook.add('THERMO-'+str(i))
        if (focusSet==False):
            notebook.tab('THERMO-'+str(i)).focus_set()
            focusSet=True
        THERMOo[i]=thermoDASH(page,i,1)
        SampleTmin+=0.15

CURRENTpresent=8*[False]
CURRENTo=list(range(8)) 
CURRENTFoundCount=0
for i in range (0,8):
    resp=CMD("CURRENT.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        CURRENTpresent[i]=True
        CURRENTFoundCount+=1   
        page = notebook.add('CURRENT-'+str(i))
        if (focusSet==False):
            notebook.tab('CURRENT-'+str(i)).focus_set()
            focusSet=True
        CURRENTo[i]=currentDASH(page,i,1)
        SampleTmin+=0.15

DIGIpresent=8*[False]
DIGIo=list(range(8)) 
DIGIFoundCount=0
for i in range (0,8):
    resp=CMD("DIGI.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        DIGIpresent[i]=True
        DIGIFoundCount+=1   
        page = notebook.add('DIGI-'+str(i))
        if (focusSet==False):
            notebook.tab('DIGI-'+str(i)).focus_set()
            focusSet=True
        DIGIo[i]=digiDASH(page,i,4)
        SampleTmin+=0.15

ADCpresent=8*[False]
ADCo1=list(range(8))
ADCo2=list(range(8)) 
ADCFoundCount=0
for i in range (0,8):
    resp=CMD("ADC.getADDR("+str(i)+")")
    if (resp[0]==str(i)):
        ADCpresent[i]=True
        resp=CMD("ADC.initADC("+str(i)+")")
        page1 = notebook.add('ADC-'+str(i)+'/1')
        page2 = notebook.add('ADC-'+str(i)+'/2')
        if (focusSet==False):
            notebook.tab('ADC-'+str(i)+'/1').focus_set()
            focusSet=True
        ADCo1[i]=adc1DASH(page1,i,3)
        ADCo2[i]=adc2DASH(page2,i,3)
        arg=(CMD("ADC.setMODE("+str(i)+",slow)"))
        SampleTmin+=0.15
        

      
if (SampleTmin>0):
    SampleT=SampleTmin
else:
    SampleT=0.2

SamplePeriod=StringVar()
SamplePeriod.set(str(round(SampleT,3)))

SampleCount=StringVar()
SampleCount.set('1000')

sDval=StringVar()
sDval.set(str(float(SamplePeriod.get())*float(SampleCount.get())))
    
notebook.setnaturalsize() 
root.wm_deiconify() #bring window to the front
root.after(int(SampleT*1000),task) 

root.after(500,doUpdates) 
print ()
print ("Running...")  
root.protocol("WM_DELETE_WINDOW", shutDown)
root.mainloop() 
