from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
# import face_recognition
import numpy as np
import os
import shutil
import schedule
import time

#----auto----
def auto_delete():
        #schedule.every(24).hour.do(job)
        
        return schedule.every(30).seconds.do(delete)

def delete():
    dir = 'dataset_temp'

    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
def copy():
    shutil.copyfile('D:\work space\Thun Project\PLASK LONGUNE\classifier_temp.xml', 'D:\work space\Thun Project\PLASK LONGUNE\classifier.xml')