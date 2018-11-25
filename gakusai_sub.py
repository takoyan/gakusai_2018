#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
import re
import numpy as np
import math
import sys
from time import sleep
from janome.tokenizer import Tokenizer
import subprocess
from pydub import AudioSegment
from pydub.playback import play



model_path="/home/takoyan/catkin_ws/src/spr"
spr_path="/home/takoyan/catkin_ws/src/spr/script"
signal = spr_path +"/sound.wav"
sound =AudioSegment.from_file(signal, 'wav')



#rate = rospy.Rate(10)

t = Tokenizer()
qa_dict = {}

def get_Cos_up(v1, v2):
    sum=0
    for word in v1:
        if word in v2:
            sum += 1
    return sum


def get_Cos_under(list):
    return math.sqrt(len(list))


def get_Cos_sim(v1, v2):
    return float(get_Cos_up(v1, v2)/get_Cos_under(v1)*get_Cos_under(v2))


def get_Surface(words):
    surface=[]
    for word in words:
        surface.append(word.surface)
    return surface




def jtalk(t):
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed=['-r','1.0']
    outwav=['-ow','open_jtalk.wav']
    cmd=open_jtalk+mech+htsvoice+speed+outwav
    c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    c.stdin.write(t)
    c.stdin.close()
    c.wait()
    aplay = ['aplay','-q','open_jtalk.wav']
    wr = subprocess.Popen(aplay)


    
def callback(data):
    rospy.init_node('listener', anonymous=True)
    rate = rospy.Rate(10)
    if(data.data != ''):
        response=data.data
        print(response)
        word_surface=get_Surface(t.tokenize(response.decode('utf-8')))
        
        max=0
        ans=0

        for q, a in qa_dict.items():
            q_surface=get_Surface(t.tokenize(q))
            score=get_Cos_sim(word_surface, q_surface)

            if(score>max and score>=0.5):
                max=score
                ans=a
        if ans is not 0:
            print ans
            print('\n')
            jtalk(ans.encode('utf-8'))
            restart_speech=rospy.Publisher('restart_speech', String, queue_size=10)
            rospy.sleep(13)#適宜調整
            restart_speech.publish('restart')
            play(sound)


        else:
            print'答えはみつかりません'
            jtalk('ごめんなさい.わかりません')
            print('\n')
            restart_speech=rospy.Publisher('restart_speech', String, queue_size=10)
            rospy.sleep(5)
            restart_speech.publish('restart')
            play(sound)


            

        

def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber('spr', String, callback)
    #spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

    
def please_speak(data):
   return  

    
    
qa_dict={}
que=[]
qa_list=[]


if __name__ == '__main__':
    with open('/home/takoyan/catkin_ws/src/gakusai/school_festival.csv', 'r')as quize:
        qa_list=quize.readlines()
        for qa in qa_list:
            qa=qa.rstrip().decode('utf-8').split(';')
            qa_dict[qa[0]]=qa[1]
        listener()
