#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
from time import sleep
import re
import rospy
import subprocess
from std_msgs.msg import String
from pydub import AudioSegment
from pydub.playback import play



model_path="/home/takoyan/catkin_ws/src/spr"
spr_path="/home/takoyan/catkin_ws/src/spr/script"
signal = spr_path +"/sound.wav"
sound =AudioSegment.from_file(signal, 'wav')


def start_speech(data):
    global start
    start=True
    return 

def restart_speech(data):
    global flag
    flag=True
    return

def get_clean_sent(response):
    if(response==''):
        return
    
    data=''
    if '<RECOGOUT>\n' in response:
        data = response
    elif 'WHYPO WORD=' in response:
        data = data + response
    else:
        data = ""
        
        
    if '</RECOGOUT>' in data:
        text = ""
        line_list = data.split('\n')
        #print line_list
        for line in line_list:
            if 'WHYPO' in line:
                word = re.compile('WORD="((?!").)+"').search(line)
                print word
                if word:
                    text = text + word.group().split('"')[1]
                    #print "a"
                    
        if text is not "":
            return text
                


def talker():
    rospy.init_node('talker', anonymous=True)
    global flag
    global start
    count=0
    flag=True
    start=True
    host="localhost"
    port=10500
    pub=rospy.Publisher('spr', String, queue_size=10)
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    
    while 1:
        try:
            if(start==True):
                if(flag==True):
                    response=client.recv(1024)
                    response=get_clean_sent(response)
                    
                    if str(response)=='タートル':
                        while(1):
                            if(count==0):
                                play(sound)
                                count+=1
                            response=client.recv(1024)
                            response=get_clean_sent(response)
                            print('res:'+str(response))
                            if(response!='' or response!=None):
                                if(response=='タートル' or response==None):
                                    continue
                                pub.publish(response)
                                #count=0
                                continue

                elif(flag==False):
                    print('少々お待ちください')
                    rospy.Subscriber('restart_speech', String, restart_speech)
                    #client.close()
                        



        except KeyboardInterrupt:
            client.close()
            sleep(3)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))


    

if __name__=='__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass









