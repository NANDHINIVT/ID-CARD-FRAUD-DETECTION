from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import math
from datetime import datetime
from datetime import date
import datetime
import random
from random import seed
from random import randint
from flask_mail import Mail, Message
from flask import send_file
import smtplib
import socket
import pytesseract

import numpy as np
from matplotlib import pyplot as plt
import cv2
import threading
import os
import time
import shutil
import hashlib
import imagehash
import PIL.Image
from PIL import Image, ImageDraw, ImageFilter
import piexif

import urllib.request
import urllib.parse
from urllib.request import urlopen
import webbrowser

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="idcard"
)


app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####
##email
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "stegofaceidissuer@gmail.com",
    "MAIL_PASSWORD": "pwxzxzkmnyygrakr"
}

app.config.update(mail_settings)
mail = Mail(app)
#######
@app.route('/',methods=['POST','GET'])
def index():
    cnt=0
    act=""
    msg=""
    ff=open("det.txt","w")
    ff.write("")
    ff.close()
    if request.method == 'POST':
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM sf_admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            result="Your logged in fail!!!"
        

    return render_template('index.html',msg=msg,act=act)

@app.route('/login',methods=['POST','GET'])
def login():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM sf_register where uname=%s && pass=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            result=" Your Logged in sucessfully**"
            return redirect(url_for('home'))
            
        else:
            result="Your logged in fail!!!"
    return render_template('login.html',msg=msg,act=act)



@app.route('/register',methods=['POST','GET'])
def register():
    result=""
    act=""
    mycursor = mydb.cursor()
    
    
    if request.method=='POST':
        
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        ctype=request.form['ctype']
       
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        #mycursor.execute("SELECT count(*) FROM sf_files where uname=%s",(uname, ))
        #cnt = mycursor.fetchone()[0]
        #if cnt==0:
        mycursor.execute("SELECT max(id)+1 FROM sf_files")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO sf_files(id, uname, mobile, email, rdate, ctype) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid, name, mobile, email, rdate, ctype)
        act="success"
        mycursor.execute(sql, val)
        mydb.commit()            
        print(mycursor.rowcount, "record inserted.")
        if ctype=="Aadhar":
            return redirect(url_for('upload',fid=maxid))
        elif ctype=="Pancard":
            return redirect(url_for('upload2',fid=maxid))
        elif ctype=="Certificate":
            return redirect(url_for('upload3',fid=maxid))
            
        #else:
        #    act="wrong"
        #    result="Reg No. Already Exist!"
    return render_template('register.html',act=act,result=result)

@app.route('/add_verifier',methods=['POST','GET'])
def add_verifier():
    result=""
    act=""
    mycursor = mydb.cursor()
    
    
    if request.method=='POST':
        
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        uname=request.form['uname']
        pass1=request.form['pass']
       
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM sf_register where uname=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM sf_register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO sf_register(id, name, mobile, email, uname, pass) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (maxid, name, mobile, email, uname, pass1)
            act="success"
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            message="Dear "+name+", Document Identity Verifier account - Username:"+uname+", Password:"+pass1
            url="http://iotcloud.co.in/testmail/sendmail.php?email="+email+"&message="+message
            webbrowser.open_new(url)
            return redirect(url_for('add_verifier',fid=maxid))
                
        else:
            act="wrong"
            result="Already Exist!"

    mycursor.execute("SELECT * FROM sf_register")
    value = mycursor.fetchall()
    
    return render_template('add_verifier.html',act=act,value=value)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    s1=""
    ctype=""
    value=[]
    uname=""
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    act = request.args.get('act')
    
    mycursor = mydb.cursor()

    if request.method=='POST':
        
        ctype=request.form['ctype']
        mycursor.execute("SELECT count(*) FROM sf_files where ctype=%s",(ctype,))
        cc = mycursor.fetchone()[0]
        if cc>0:
            s1="1"
            mycursor.execute("SELECT * FROM sf_files where ctype=%s",(ctype,))
            value = mycursor.fetchall()
    
    if act=="del":
        did = request.args.get('did')
        mycursor.execute("delete from sf_files where id=%s",(did, ))
        mydb.commit()
        return redirect(url_for('admin'))
  
        
    return render_template('admin.html',value=value,s1=s1,ctype=ctype)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    uname=""
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    fid = request.args.get('fid')
    
    mycursor = mydb.cursor()
    

    #mycursor.execute("SELECT max(id)+1 FROM sf_files")
    #maxid = mycursor.fetchone()[0]
    #if maxid is None:
    #    maxid=1
                        
    if request.method=='POST':
        
        file = request.files['file']
        file2 = request.files['file2']
        print(file.filename)
        
        fn=file.filename
        fnn="F"+fid+fn

        fn2=file2.filename
        fnn2="B"+fid+fn2
        #fnn = secure_filename(fn1)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn2))
        print("upload")
        filename2 = 'static/upload/'+fnn
        
        
        mycursor.execute("update sf_files set filename=%s,filename2=%s where id=%s", (fnn,fnn2,fid))
        mydb.commit()

        ###RPN Face Detection
        
        ##
        # Detect the faces
        image = cv2.imread("static/upload/"+fnn)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw the rectangle around each face
        j = 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rectface="R"+fnn
            cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+rectface)
            
            j += 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #rectface="S"+fnn
            #cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+fnn)
            cropped = image[y:y+h, x:x+w]
            gg="C"+fnn
            cv2.imwrite("static/upload/"+gg, cropped)
            

        msg2="Uploaded Success"
        return redirect(url_for('process1',fid=fid))
        #except:
        #    print("dd")
    
        
    return render_template('upload.html')

@app.route('/upload2', methods=['GET', 'POST'])
def upload2():
    uname=""
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    fid = request.args.get('fid')
    
    mycursor = mydb.cursor()
    

    #mycursor.execute("SELECT max(id)+1 FROM sf_files")
    #maxid = mycursor.fetchone()[0]
    #if maxid is None:
    #    maxid=1
                        
    if request.method=='POST':
        
        file = request.files['file']
        print(file.filename)
        #try:
        #    if file.filename == '':
        #        flash('No selected file')
        #        return redirect(request.url)
        #if file:
        fn=file.filename
        fnn="F"+fid+fn
        #fnn = secure_filename(fn1)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn))
        print("upload")
        filename2 = 'static/upload/'+fnn
        
        
        mycursor.execute("update sf_files set filename=%s where id=%s", (fnn,fid))
        mydb.commit()

        ###RPN Face Detection
        
        ##
        # Detect the faces
        image = cv2.imread("static/upload/"+fnn)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw the rectangle around each face
        j = 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rectface="R"+fnn
            cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+rectface)
            
            j += 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #rectface="S"+fnn
            #cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+fnn)
            cropped = image[y:y+h, x:x+w]
            gg="C"+fnn
            cv2.imwrite("static/upload/"+gg, cropped)
            

        msg2="Uploaded Success"
        return redirect(url_for('process_pan',fid=fid))
        #except:
        #    print("dd")
    
        
    return render_template('upload2.html')

@app.route('/upload3', methods=['GET', 'POST'])
def upload3():
    uname=""
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    fid = request.args.get('fid')
    
    mycursor = mydb.cursor()
    

    #mycursor.execute("SELECT max(id)+1 FROM sf_files")
    #maxid = mycursor.fetchone()[0]
    #if maxid is None:
    #    maxid=1
                        
    if request.method=='POST':
        
        file = request.files['file']
        print(file.filename)
        
        fn=file.filename
        fnn="F"+fid+fn
        #fnn = secure_filename(fn1)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn))
        
        #Resize
        
        img = cv2.imread('static/upload/'+fnn)
        rez = cv2.resize(img, (780, 1127))
        cv2.imwrite("static/upload/S"+fnn, rez)

        #Crop
        im = Image.open("static/upload/S"+fnn)
        left = 480
        top = 290
        right = 720
        bottom = 402
        im1 = im.crop((left, top, right, bottom))
        im1.save("static/upload/X"+fnn)

        left = 49
        top = 404
        right = 714
        bottom = 820
        im1 = im.crop((left, top, right, bottom))
        im1.save("static/upload/Y"+fnn)

        left = 49
        top = 993
        right = 265
        bottom = 1083
        im1 = im.crop((left, top, right, bottom))
        im1.save("static/upload/Z"+fnn)
        ##########
        
        mycursor.execute("update sf_files set filename=%s where id=%s", (fnn,fid))
        mydb.commit()

        ###RPN Face Detection
        
        ##
        # Detect the faces
        image = cv2.imread("static/upload/"+fnn)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw the rectangle around each face
        j = 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rectface="R"+fnn
            cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+rectface)
            
            j += 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #rectface="S"+fnn
            #cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/upload/"+fnn)
            cropped = image[y:y+h, x:x+w]
            gg="C"+fnn
            cv2.imwrite("static/upload/"+gg, cropped)
            

        msg2="Uploaded Success"
        return redirect(url_for('process_cert',fid=fid))
        #except:
        #    print("dd")
    
        
    return render_template('upload3.html')


@app.route('/process1', methods=['GET', 'POST'])
def process1():
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    fname="R"+data[2]
    fn=data[2]
    #if request.method=='POST':
        
    #    return redirect(url_for('process2',fid=fid))
        
    return render_template('process1.html',fname=fname,fid=fid)

@app.route('/process21', methods=['GET', 'POST'])
def process21():
    msg=""
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    name=data[1]
    fn=data[2]
    fname=fn
    fn2=data[11]
    if request.method=='POST':
        na1=request.form['nam']
        dob1=request.form['dob1']
        gender1=request.form['gender1']
        aadhar1=request.form['aadhar1']
        address1=request.form['address1']
        mycursor.execute("update sf_files set name=%s,dob=%s,gender=%s,aadhar=%s,address=%s where id=%s", (na1,dob1,gender1,aadhar1,address1,fid))
        mydb.commit()
        msg="yes"

    
    
    ####
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


    #fa=data[5]
    Actual_image = cv2.imread("static/upload/"+fn)
    Sample_img = cv2.resize(Actual_image,(400,350))
    Image_ht,Image_wd,Image_thickness = Sample_img.shape
    Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
    texts = pytesseract.image_to_data(Sample_img) 
    mytext=""
    prevy=0

    na=""
    dob=""
    gender=""
    aadhar=""
    address=""
    n=0
    m=0
    m1=0
    a=""
    for cnt,text in enumerate(texts.splitlines()):
        n+=1
        if cnt==0:
            continue
        text = text.split()
        if len(text)==12:
            x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
            if(len(mytext)==0):
                prey=y
            if(prevy-y>=10 or y-prevy>=10):
                print(mytext)
                name1=name.upper()
                mytext3=mytext
                mytextt=mytext.upper()
                if mytextt.find(name1) != -1:
                    #print("name yes")
                    ff=open("name.txt","w")
                    ff.write(mytext3)
                    ff.close()
                    na=mytext3
                if mytext.find("DOB") != -1:
                    ss=mytext.split(':')
                    dob=ss[1].strip()
                if mytext.find("FEMALE") != -1:
                    gender="FEMALE"
                    m=n
                elif mytext.find("Female") != -1:
                    gender="Female"
                    m=n
                elif mytext.find("MALE") != -1:
                    gender="MALE"
                    m=n
                elif mytext.find("Male") != -1:
                    gender="Male"
                    m=n
                
                
                if n>m:
                    
                    if mytext =="":
                        s=1
                    else:
                        
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[0].find(ii) != -1:
                                a='1'
                                print("len=")
                                mm=mytext.strip()
                                print(len(mm))
                                aadhar=mytext
                        
                
                    
                mytext=""
            mytext = mytext + text[11]+" "
            prevy=y


    print("name="+na)
    print("dob="+dob)
    print("gender="+gender)
    print("aadhar="+aadhar)
    
    ###################################
    Actual_image2 = cv2.imread("static/upload/"+fn2)
    Sample_img2 = cv2.resize(Actual_image2,(400,350))
    Image_ht,Image_wd,Image_thickness = Sample_img2.shape
    Sample_img = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
    texts2 = pytesseract.image_to_data(Sample_img2) 
    mytext2=""
    prevy2=0

    n=0
    for cnt2,text2 in enumerate(texts2.splitlines()):
        n+=1
        if cnt2==0:
            continue
        text2 = text2.split()
        if len(text2)==12:
            x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
            if(len(mytext2)==0):
                prey=y
            #if(prevy-y>=10 or y-prevy>=10):
            #    mytext2=""

            mytext2 = mytext2 + text2[11]+" "
            prevy2=y
    
    addr=mytext2.split("Address:")
    addr2=addr[1].split(aadhar)
    address=addr2[0].strip()
    print("address="+address)
    ss=na+"|"+dob+"|"+gender+"|"+aadhar+"|"+address
    ff=open("name.txt","w")
    ff.write(ss)
    ff.close()
                        
    return render_template('process21.html',msg=msg,fname=fname,fn2=fn2,fid=fid,na=na,dob=dob,gender=gender,aadhar=aadhar,address=address)



@app.route('/process_pan', methods=['GET', 'POST'])
def process_pan():
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    fname="R"+data[2]
    fn=data[2]
    #if request.method=='POST':
        
    #    return redirect(url_for('process2',fid=fid))
        
    return render_template('process_pan.html',fname=fname,fid=fid)

@app.route('/process_pan21', methods=['GET', 'POST'])
def process_pan21():
    msg=""
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    #print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    name=data[1]
    fn=data[2]
    fname=fn

    try:
        ####
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


        #fa=data[5]
        Actual_image = cv2.imread("static/upload/"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        na=""
        dob=""
        gender=""
        aadhar=""
        n=0
        m=0
        m1=0
        a=0
        b=0
        for cnt,text in enumerate(texts.splitlines()):
            n+=1
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)
                    name1=name.upper()
                    if mytext.find(name1) != -1:
                        #print("name yes")
                        ff=open("name.txt","w")
                        ff.write(mytext)
                        ff.close()
                        na=mytext
                    if mytext.find("/") != -1:
                        dob=mytext
                    
                    
                    
                    
                        
                    if mytext =="":
                        s=1
                    else:
                        a=0
                        for i in range(0,10):
                            ii=str(i)
                            if mytext.find(ii) != -1:
                                a+=1
                                print(a)
                                
                        b=0        
                        for i in range(26):
                            alp=chr(65 + i)
                            #print(chr(65 + i), end = " ")
                            
                            if mytext.find(alp) != -1:
                                b+=1
                                print(b)

                        if a>0 and b>0:
                            aadhar=mytext
       
                        
                    
                        
                        '''for i in range(0,10):
                            ii=str(i)
                            if mytext[0].find(ii) != -1:
                                a='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[1].find(ii) != -1:
                                b='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[2].find(ii) != -1:
                                c='1'
                                break
                        if a=='1' and b=='1' and c=='1':
                            aadhar=mytext'''


                        
                    mytext=""
                mytext = mytext + text[11]+" "
                prevy=y


        print("name="+na)
        print("dob="+dob)
        print("aadhar="+aadhar)
        ss=na+"|"+dob+"|"+aadhar
        ff=open("name.txt","w")
        ff.write(ss)
        ff.close()
    except:
        print("try")

    if request.method=='POST':
        try:
            na1=request.form['nam']
            dob1=request.form['dob1']
            aadhar1=request.form['aadhar1']
            mycursor.execute("update sf_files set name=%s,dob=%s,aadhar=%s where id=%s", (na1,dob1,aadhar1,fid))
            mydb.commit()
            msg="yes"
        except:
            print("")
        
        
    return render_template('process_pan21.html',msg=msg,fid=fid,fname=fname,na=na,dob=dob,gender=gender,aadhar=aadhar)

@app.route('/process_cert', methods=['GET', 'POST'])
def process_cert():
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    fname="R"+data[2]
    fn=data[2]
    #if request.method=='POST':
        
    #    return redirect(url_for('process2',fid=fid))
        
    return render_template('process_cert.html',fname=fname,fid=fid)

@app.route('/process_cert21', methods=['GET', 'POST'])
def process_cert21():
    msg=""
    uname=""
    fid = request.args.get('fid')
    if 'username' in session:
        uname = session['username']
    name=""
    #print(uname)
    mycursor = mydb.cursor()
    

    mycursor.execute("SELECT * FROM sf_files where id=%s",(fid, ))
    data = mycursor.fetchone()
    name=data[1]
    fn=data[2]
    fname=fn

    #try:
    ####
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    v1=""
    v2=""
    v3=""
    #fa=data[5]
    Actual_image = cv2.imread("static/upload/X"+fn)
    Sample_img = cv2.resize(Actual_image,(400,350))
    Image_ht,Image_wd,Image_thickness = Sample_img.shape
    Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
    texts = pytesseract.image_to_data(Sample_img) 
    mytext=""
    prevy=0

    
    
    for cnt,text in enumerate(texts.splitlines()):
        
        if cnt==0:
            continue
        text = text.split()
        if len(text)==12:
            x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
            if(len(mytext)==0):
                prey=y
            if(prevy-y>=10 or y-prevy>=10):
                print(mytext)
                #mytext=""
            mytext = mytext + text[11]+" "
            prevy=y

    v1=mytext
    ####
    Actual_image2 = cv2.imread("static/upload/Y"+fn)
    Sample_img2 = cv2.resize(Actual_image2,(400,350))
    Image_ht,Image_wd,Image_thickness = Sample_img2.shape
    Sample_img2 = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
    texts2 = pytesseract.image_to_data(Sample_img2) 
    mytext2=""
    prevy2=0

    
    
    for cnt2,text2 in enumerate(texts2.splitlines()):
        
        if cnt2==0:
            continue
        text2 = text2.split()
        if len(text2)==12:
            x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
            if(len(mytext2)==0):
                prey=y
            if(prevy2-y>=10 or y-prevy2>=10):
                print(mytext2)
                #mytext2=""
                
            mytext2 = mytext2 + text2[11]+" "
            prevy2=y

    v2=mytext2
    ########
    Actual_image3 = cv2.imread("static/upload/Z"+fn)
    Sample_img3 = cv2.resize(Actual_image3,(400,350))
    Image_ht,Image_wd,Image_thickness = Sample_img3.shape
    Sample_img3 = cv2.cvtColor(Sample_img3,cv2.COLOR_BGR2RGB)
    texts3 = pytesseract.image_to_data(Sample_img3) 
    mytext3=""
    prevy3=0

    
    
    for cnt3,text3 in enumerate(texts3.splitlines()):
        
        if cnt3==0:
            continue
        text3 = text3.split()
        if len(text3)==12:
            x,y,w,h = int(text3[6]),int(text3[7]),int(text3[8]),int(text3[9])
            if(len(mytext3)==0):
                prey=y
            if(prevy3-y>=10 or y-prevy3>=10):
                print(mytext3)
                #mytext3=""
                
            mytext3 = mytext3 + text3[11]+" "
            prevy3=y

    v3=mytext3
    ####
    print("v1="+v1)
    print("v2="+v2)
    print("v3="+v3)
    ss=v1+"|"+v2+"|"+v3
    #ff=open("name.txt","w")
    #ff.write(ss)
    #ff.close()
    #except:
    #    print("try")

    if request.method=='POST':
        
        
        mycursor.execute("update sf_files set value1=%s,value2=%s,value3=%s where id=%s", (v1,v2,v3,fid))
        mydb.commit()
        print("updated")
        msg="yes"
        
        
    return render_template('process_cert21.html',msg=msg,fid=fid,fname=fname,v1=v1,v2=v2,v3=v3)


@app.route('/home', methods=['GET', 'POST'])
def home():
    uname=""
    if 'username' in session:
        uname = session['username']
    name=""
    print(uname)
    fid=""
    
    mycursor = mydb.cursor()
      
    if request.method=='POST':
        ctype=request.form['ctype']
        file = request.files['file']
        print(file.filename)
        
        fn=file.filename
        fnn="m1.jpg"
        
        
        file.save(os.path.join("static/test", fnn))
        print("upload")
        filename2 = 'static/upload/'+fnn
        
        
        # Detect the faces
        image = cv2.imread("static/test/"+fnn)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw the rectangle around each face
        j = 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rectface="r1.jpg"
            cv2.imwrite("static/test/"+rectface, mm)
            image = cv2.imread("static/test/"+rectface)
            #cropped = image[y:y+h, x:x+w]
            #gg="C"+fnn
            #cv2.imwrite("static/upload/"+gg, cropped)
            #mm2 = PIL.Image.open("static/upload/"+gg)
            #rz = mm2.resize((100,100), PIL.Image.ANTIALIAS)
            #rz.save("static/upload/"+gg)
            j += 1
        for (x, y, w, h) in faces:
            mm=cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #rectface="S"+fnn
            #cv2.imwrite("static/upload/"+rectface, mm)
            image = cv2.imread("static/test/"+fnn)
            cropped = image[y:y+h, x:x+w]
            gg="f1.jpg"
            cv2.imwrite("static/test/"+gg, cropped)
            
        if ctype=="Aadhar":
            file2 = request.files['file2']
            fn2=file2.filename
            fnn2="s1.jpg"
            file2.save(os.path.join("static/test", fnn2))

        if ctype=="Certificate":
            #Resize
        
            img = cv2.imread('static/test/'+fnn)
            rez = cv2.resize(img, (780, 1127))
            cv2.imwrite("static/test/S"+fnn, rez)

            #Crop
            im = Image.open("static/test/S"+fnn)
            left = 480
            top = 290
            right = 720
            bottom = 402
            im1 = im.crop((left, top, right, bottom))
            im1.save("static/test/X"+fnn)

            left = 49
            top = 404
            right = 714
            bottom = 820
            im1 = im.crop((left, top, right, bottom))
            im1.save("static/test/Y"+fnn)

            left = 49
            top = 993
            right = 265
            bottom = 1083
            im1 = im.crop((left, top, right, bottom))
            im1.save("static/test/Z"+fnn)

            
        msg2="Uploaded Success"
        return redirect(url_for('decode1',ctype=ctype))
        #except:

    
        #    print("dd")
    
        
    return render_template('home.html')


@app.route('/decode1', methods=['GET', 'POST'])
def decode1():
    msg=""
    s1=""
    rid=""
    ctype=request.args.get("ctype")
    uname=""
    if 'username' in session:
        uname = session['username']
    
    mycursor = mydb.cursor()

    
    cutoff=3
    s1="1"

    mycursor.execute("SELECT * FROM sf_files")
    dt = mycursor.fetchall()
    for rr in dt:
        ff="C"+str(rr[2])
        hash0 = imagehash.average_hash(Image.open("static/upload/"+ff)) 
        hash1 = imagehash.average_hash(Image.open("static/test/f1.jpg"))
        cc1=hash0 - hash1
        print("cc="+str(cc1))
        if cc1<=cutoff:
            print("yes")
            st="1"
            rid=str(rr[0])
            break
        else:
            st="2"
            print("no")
    if st=="1":
        ff=open("static/ff.txt","w")
        ff.write("yes")
        ff.close()
        msg="1"
    else:
        ff=open("static/ff.txt","w")
        ff.write("no")
        ff.close()
        msg="2"
            
    

    return render_template('decode1.html',msg=msg,ctype=ctype,s1=s1,rid=rid)


@app.route('/decode2', methods=['GET', 'POST'])
def decode2():
    msg=""
    msg2=""
    s1=""
    ctype=request.args.get("ctype")
    rid=request.args.get("rid")
    uname=""
    if 'username' in session:
        uname = session['username']

    na=""
    dob=""
    gender=""
    aadhar=""
    address=""
    v1=""
    v2=""
    v3=""
    mycursor = mydb.cursor()
    fn="m1.jpg"
    fn2="s1.jpg"

    ff=open("static/ff.txt","r")
    face_st=ff.read()
    ff.close()
            
    name1=""
    if rid=="":
        rr="1"
    else:
        mycursor.execute("SELECT * FROM sf_files where id=%s",(rid,))
        dat = mycursor.fetchone()
        name1=dat[1]

    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    #try:
    if ctype=="Aadhar":
        ####
        


        #fa=data[5]
        Actual_image = cv2.imread("static/test/"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        na=""
        dob=""
        gender=""
        aadhar=""
        n=0
        m=0
        m1=0
        a=0
        b=0
        for cnt,text in enumerate(texts.splitlines()):
            n+=1
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)

                    if rid=="":
                        mycursor.execute("SELECT * FROM sf_files")
                        dat1 = mycursor.fetchall()
                        for nd in dat1:
                            name1=nd[1]
                            name1=name1.upper()
                            mytext3=mytext
                            mytextt=mytext.upper()
                            if mytextt.find(name1) != -1:
                                #print("name yes")
                                ff=open("name.txt","w")
                                ff.write(mytext3)
                                ff.close()
                                na=mytext3
                        
                    else:
                        name1=name1.upper()
                        mytext3=mytext
                        mytextt=mytext.upper()
                        if mytextt.find(name1) != -1:
                            #print("name yes")
                            ff=open("name.txt","w")
                            ff.write(mytext3)
                            ff.close()
                            na=mytext3
                    if mytext.find("DOB") != -1:
                        ss=mytext.split(':')
                        dob=ss[1].strip()
                    if mytext.find("FEMALE") != -1:
                        gender="FEMALE"
                        m=n
                    elif mytext.find("Female") != -1:
                        gender="Female"
                        m=n
                    elif mytext.find("MALE") != -1:
                        gender="MALE"
                        m=n
                    elif mytext.find("Male") != -1:
                        gender="Male"
                        m=n
                    
                    
                    if n>m:
                        
                        if mytext =="":
                            s=1
                        else:
                            s1="1"
                            for i in range(0,10):
                                ii=str(i)
                                if mytext[0].find(ii) != -1:
                                    a='1'
                                    print("len=")
                                    mm=mytext.strip()
                                    print(len(mm))
                                    aadhar=mytext
                            
                    
                        
                    mytext=""
                mytext = mytext + text[11]+" "
                prevy=y

        ###################################
        Actual_image2 = cv2.imread("static/test/"+fn2)
        Sample_img2 = cv2.resize(Actual_image2,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img2.shape
        Sample_img = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
        texts2 = pytesseract.image_to_data(Sample_img2) 
        mytext2=""
        prevy2=0

        n=0
        for cnt2,text2 in enumerate(texts2.splitlines()):
            n+=1
            if cnt2==0:
                continue
            text2 = text2.split()
            if len(text2)==12:
                x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
                if(len(mytext2)==0):
                    prey=y
                #if(prevy-y>=10 or y-prevy>=10):
                #    mytext2=""

                mytext2 = mytext2 + text2[11]+" "
                prevy2=y
        
        addr=mytext2.split("Address:")
        addr2=addr[1].split(aadhar)
        address=addr2[0].strip()
        print("name="+na)
        print("gender="+gender)
        print("dob="+dob)
        print("aadhar="+aadhar)
        print("address="+address)
        ss=na+"|"+dob+"|"+gender+"|"+aadhar+"|"+address
        
        ff=open("name.txt","w")
        ff.write(ss)
        ff.close()
        
        mycursor.execute("SELECT count(*) FROM sf_files where name=%s && gender=%s && dob=%s && aadhar=%s && address=%s",(na,gender,dob,aadhar,address))
        ctt = mycursor.fetchone()[0]

        
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where name=%s && gender=%s && dob=%s && aadhar=%s && address=%s",(na,gender,dob,aadhar,address))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
                ff=open("static/tt.txt","w")
                ff.write("yes/ok")
                ff.close()
        
            else:
                ff=open("static/tt.txt","w")
                ff.write("yes/not")
                ff.close()
        else:
            msg="2"
            ff=open("static/tt.txt","w")
            ff.write("no/not")
            ff.close()
        
    #except:
    #    print("try")
    
    elif ctype=="Pancard":
        print("Pancard")
        Actual_image = cv2.imread("static/test/"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        na=""
        dob=""
        gender=""
        aadhar=""
        n=0
        m=0
        m1=0
        a=0
        b=0
        for cnt,text in enumerate(texts.splitlines()):
            n+=1
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)

                    if rid=="":
                        mycursor.execute("SELECT * FROM sf_files where uname!=''")
                        dat1 = mycursor.fetchall()
                        for nd in dat1:
                            name1=nd[1]
                            name1=name1.upper()
                            mytext3=mytext
                            mytextt=mytext.upper()
                            if mytextt.find(name1) != -1:
                                #print("name yes")
                                ff=open("name.txt","w")
                                ff.write(mytext3)
                                ff.close()
                                na=mytext3
                        
                    else:
                        mytext3=mytext
                        mytext1=mytext.upper()
                        name1=name1.upper()
                        if mytext1.find(name1) != -1:
                            #print("name yes")
                            ff=open("name.txt","w")
                            ff.write(mytext3)
                            ff.close()
                            na=mytext3
                    if mytext.find("/") != -1:
                        dob=mytext
                    
                    
                    
                    
                        
                    if mytext =="":
                        s=1
                    else:
                        s1="1"
                        a=0
                        for i in range(0,10):
                            ii=str(i)
                            if mytext.find(ii) != -1:
                                a+=1
                                print(a)
                                
                        b=0        
                        for i in range(26):
                            alp=chr(65 + i)
                            #print(chr(65 + i), end = " ")
                            
                            if mytext.find(alp) != -1:
                                b+=1
                                print(b)

                        if a>0 and b>0:
                            aadhar=mytext
       
                        
                    
                        
                        '''for i in range(0,10):
                            ii=str(i)
                            if mytext[0].find(ii) != -1:
                                a='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[1].find(ii) != -1:
                                b='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[2].find(ii) != -1:
                                c='1'
                                break
                        if a=='1' and b=='1' and c=='1':
                            aadhar=mytext'''


                        
                    mytext=""
                mytext = mytext + text[11]+" "
                prevy=y


        print("name="+na)
        print("dob="+dob)
        print("aadhar="+aadhar)
        ss=na+"|"+dob+"|"+aadhar
        ff=open("name.txt","w")
        ff.write(ss)
        ff.close()
        mycursor.execute("SELECT count(*) FROM sf_files where name=%s && dob=%s && aadhar=%s",(na,dob,aadhar))
        ctt = mycursor.fetchone()[0]
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where name=%s && dob=%s && aadhar=%s",(na,dob,aadhar))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
                ff=open("static/tt.txt","w")
                ff.write("yes/ok")
                ff.close()

            else:
                ff=open("static/tt.txt","w")
                ff.write("yes/not")
                ff.close()
                
                
        else:
            msg="2"
            ff=open("static/tt.txt","w")
            ff.write("no/not")
            ff.close()

    elif ctype=="Certificate":
        print("Certificate")
        s1="1"
        v1=""
        v2=""
        v3=""
        #fa=data[5]
        Actual_image = cv2.imread("static/test/X"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        
        
        for cnt,text in enumerate(texts.splitlines()):
            
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)
                    #mytext=""
                mytext = mytext + text[11]+" "
                prevy=y

        v1=mytext
        ####
        Actual_image2 = cv2.imread("static/test/Y"+fn)
        Sample_img2 = cv2.resize(Actual_image2,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img2.shape
        Sample_img2 = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
        texts2 = pytesseract.image_to_data(Sample_img2) 
        mytext2=""
        prevy2=0

        
        
        for cnt2,text2 in enumerate(texts2.splitlines()):
            
            if cnt2==0:
                continue
            text2 = text2.split()
            if len(text2)==12:
                x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
                if(len(mytext2)==0):
                    prey=y
                if(prevy2-y>=10 or y-prevy2>=10):
                    print(mytext2)
                    #mytext2=""
                    
                mytext2 = mytext2 + text2[11]+" "
                prevy2=y

        v2=mytext2
        ########
        Actual_image3 = cv2.imread("static/test/Z"+fn)
        Sample_img3 = cv2.resize(Actual_image3,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img3.shape
        Sample_img3 = cv2.cvtColor(Sample_img3,cv2.COLOR_BGR2RGB)
        texts3 = pytesseract.image_to_data(Sample_img3) 
        mytext3=""
        prevy3=0

        
        
        for cnt3,text3 in enumerate(texts3.splitlines()):
            
            if cnt3==0:
                continue
            text3 = text3.split()
            if len(text3)==12:
                x,y,w,h = int(text3[6]),int(text3[7]),int(text3[8]),int(text3[9])
                if(len(mytext3)==0):
                    prey=y
                if(prevy3-y>=10 or y-prevy3>=10):
                    print(mytext3)
                    #mytext3=""
                    
                mytext3 = mytext3 + text3[11]+" "
                prevy3=y

        v3=mytext3
        ####
        print("v1="+v1)
        print("v2="+v2)
        print("v3="+v3)
        ss=v1+"|"+v2+"|"+v3
        mycursor.execute("SELECT count(*) FROM sf_files where value1=%s && value2=%s && value3=%s",(v1,v2,v3))
        ctt = mycursor.fetchone()[0]
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where value1=%s && value2=%s && value3=%s",(v1,v2,v3))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
                ff=open("static/tt.txt","w")
                ff.write("yes/ok")
                ff.close()
            else:
                ff=open("static/tt.txt","w")
                ff.write("yes/not")
                ff.close()
                
        else:
            msg="2"
            ff=open("static/tt.txt","w")
            ff.write("no/not")
            ff.close()

    if rid=="":
        rid=rid2

    
    return render_template('decode2.html',msg=msg,rid=rid,msg2=msg2,ctype=ctype,s1=s1,face_st=face_st,na=na,dob=dob,gender=gender,aadhar=aadhar,address=address,v1=v1,v2=v2,v3=v3)


@app.route('/decode3', methods=['GET', 'POST'])
def decode3():
    msg=""
    msg2=""
    s1=""
    dat=[]
    ctype=request.args.get("ctype")
    rid=request.args.get("rid")
    uname=""
    if 'username' in session:
        uname = session['username']

    na=""
    dob=""
    gender=""
    aadhar=""
    address=""
    v1=""
    v2=""
    v3=""
    mycursor = mydb.cursor()
    fn="m1.jpg"
    fn2="s1.jpg"

    ff=open("static/ff.txt","r")
    face_st=ff.read()
    ff.close()
            
    name1=""
    if rid=="":
        rr="1"
    else:
        mycursor.execute("SELECT * FROM sf_files where id=%s",(rid,))
        dat = mycursor.fetchone()
        name1=dat[1]

    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    #try:
    if ctype=="Aadhar":
        ####
        


        #fa=data[5]
        Actual_image = cv2.imread("static/test/"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        na=""
        dob=""
        gender=""
        aadhar=""
        n=0
        m=0
        m1=0
        a=0
        b=0
        for cnt,text in enumerate(texts.splitlines()):
            n+=1
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)

                    if rid=="":
                        mycursor.execute("SELECT * FROM sf_files")
                        dat1 = mycursor.fetchall()
                        for nd in dat1:
                            name1=nd[1]
                            name1=name1.upper()
                            mytext3=mytext
                            mytextt=mytext.upper()
                            if mytextt.find(name1) != -1:
                                #print("name yes")
                                ff=open("name.txt","w")
                                ff.write(mytext3)
                                ff.close()
                                na=mytext3
                        
                    else:
                        name1=name1.upper()
                        mytext3=mytext
                        mytextt=mytext.upper()
                        if mytextt.find(name1) != -1:
                            #print("name yes")
                            ff=open("name.txt","w")
                            ff.write(mytext3)
                            ff.close()
                            na=mytext3
                    if mytext.find("DOB") != -1:
                        ss=mytext.split(':')
                        dob=ss[1].strip()
                    if mytext.find("FEMALE") != -1:
                        gender="FEMALE"
                        m=n
                    elif mytext.find("Female") != -1:
                        gender="Female"
                        m=n
                    elif mytext.find("MALE") != -1:
                        gender="MALE"
                        m=n
                    elif mytext.find("Male") != -1:
                        gender="Male"
                        m=n
                    
                    
                    if n>m:
                        
                        if mytext =="":
                            s=1
                        else:
                            s1="1"
                            for i in range(0,10):
                                ii=str(i)
                                if mytext[0].find(ii) != -1:
                                    a='1'
                                    print("len=")
                                    mm=mytext.strip()
                                    print(len(mm))
                                    aadhar=mytext
                            
                    
                        
                    mytext=""
                mytext = mytext + text[11]+" "
                prevy=y

        ###################################
        Actual_image2 = cv2.imread("static/test/"+fn2)
        Sample_img2 = cv2.resize(Actual_image2,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img2.shape
        Sample_img = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
        texts2 = pytesseract.image_to_data(Sample_img2) 
        mytext2=""
        prevy2=0

        n=0
        for cnt2,text2 in enumerate(texts2.splitlines()):
            n+=1
            if cnt2==0:
                continue
            text2 = text2.split()
            if len(text2)==12:
                x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
                if(len(mytext2)==0):
                    prey=y
                #if(prevy-y>=10 or y-prevy>=10):
                #    mytext2=""

                mytext2 = mytext2 + text2[11]+" "
                prevy2=y
        
        addr=mytext2.split("Address:")
        addr2=addr[1].split(aadhar)
        address=addr2[0].strip()
        print("name="+na)
        print("gender="+gender)
        print("dob="+dob)
        print("aadhar="+aadhar)
        print("address="+address)
        ss=na+"|"+dob+"|"+gender+"|"+aadhar+"|"+address
        
        ff=open("name.txt","w")
        ff.write(ss)
        ff.close()
        
        mycursor.execute("SELECT count(*) FROM sf_files where name=%s && gender=%s && dob=%s && aadhar=%s && address=%s",(na,gender,dob,aadhar,address))
        ctt = mycursor.fetchone()[0]

        
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where name=%s && gender=%s && dob=%s && aadhar=%s && address=%s",(na,gender,dob,aadhar,address))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
                
        else:
            msg="2"
           
    #except:
    #    print("try")
    
    elif ctype=="Pancard":
        print("Pancard")
        Actual_image = cv2.imread("static/test/"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        na=""
        dob=""
        gender=""
        aadhar=""
        n=0
        m=0
        m1=0
        a=0
        b=0
        for cnt,text in enumerate(texts.splitlines()):
            n+=1
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)

                    if rid=="":
                        mycursor.execute("SELECT * FROM sf_files where uname!=''")
                        dat1 = mycursor.fetchall()
                        for nd in dat1:
                            name1=nd[1]
                            name1=name1.upper()
                            mytext3=mytext
                            mytextt=mytext.upper()
                            if mytextt.find(name1) != -1:
                                #print("name yes")
                                ff=open("name.txt","w")
                                ff.write(mytext3)
                                ff.close()
                                na=mytext3
                        
                    else:
                        mytext3=mytext
                        mytext1=mytext.upper()
                        name1=name1.upper()
                        if mytext1.find(name1) != -1:
                            #print("name yes")
                            ff=open("name.txt","w")
                            ff.write(mytext3)
                            ff.close()
                            na=mytext3
                    if mytext.find("/") != -1:
                        dob=mytext
                    
                    
                    
                    
                        
                    if mytext =="":
                        s=1
                    else:
                        s1="1"
                        a=0
                        for i in range(0,10):
                            ii=str(i)
                            if mytext.find(ii) != -1:
                                a+=1
                                print(a)
                                
                        b=0        
                        for i in range(26):
                            alp=chr(65 + i)
                            #print(chr(65 + i), end = " ")
                            
                            if mytext.find(alp) != -1:
                                b+=1
                                print(b)

                        if a>0 and b>0:
                            aadhar=mytext
       
                        
                    
                        
                        '''for i in range(0,10):
                            ii=str(i)
                            if mytext[0].find(ii) != -1:
                                a='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[1].find(ii) != -1:
                                b='1'
                                break
                        for i in range(0,10):
                            ii=str(i)
                            if mytext[2].find(ii) != -1:
                                c='1'
                                break
                        if a=='1' and b=='1' and c=='1':
                            aadhar=mytext'''


                        
                    mytext=""
                mytext = mytext + text[11]+" "
                prevy=y


        print("name="+na)
        print("dob="+dob)
        print("aadhar="+aadhar)
        ss=na+"|"+dob+"|"+aadhar
        ff=open("name.txt","w")
        ff.write(ss)
        ff.close()
        mycursor.execute("SELECT count(*) FROM sf_files where name=%s && dob=%s && aadhar=%s",(na,dob,aadhar))
        ctt = mycursor.fetchone()[0]
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where name=%s && dob=%s && aadhar=%s",(na,dob,aadhar))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
              
        else:
            msg="2"
           

    elif ctype=="Certificate":
        print("Certificate")
        s1="1"
        v1=""
        v2=""
        v3=""
        #fa=data[5]
        Actual_image = cv2.imread("static/test/X"+fn)
        Sample_img = cv2.resize(Actual_image,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img.shape
        Sample_img = cv2.cvtColor(Sample_img,cv2.COLOR_BGR2RGB)
        texts = pytesseract.image_to_data(Sample_img) 
        mytext=""
        prevy=0

        
        
        for cnt,text in enumerate(texts.splitlines()):
            
            if cnt==0:
                continue
            text = text.split()
            if len(text)==12:
                x,y,w,h = int(text[6]),int(text[7]),int(text[8]),int(text[9])
                if(len(mytext)==0):
                    prey=y
                if(prevy-y>=10 or y-prevy>=10):
                    print(mytext)
                    #mytext=""
                mytext = mytext + text[11]+" "
                prevy=y

        v1=mytext
        ####
        Actual_image2 = cv2.imread("static/test/Y"+fn)
        Sample_img2 = cv2.resize(Actual_image2,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img2.shape
        Sample_img2 = cv2.cvtColor(Sample_img2,cv2.COLOR_BGR2RGB)
        texts2 = pytesseract.image_to_data(Sample_img2) 
        mytext2=""
        prevy2=0

        
        
        for cnt2,text2 in enumerate(texts2.splitlines()):
            
            if cnt2==0:
                continue
            text2 = text2.split()
            if len(text2)==12:
                x,y,w,h = int(text2[6]),int(text2[7]),int(text2[8]),int(text2[9])
                if(len(mytext2)==0):
                    prey=y
                if(prevy2-y>=10 or y-prevy2>=10):
                    print(mytext2)
                    #mytext2=""
                    
                mytext2 = mytext2 + text2[11]+" "
                prevy2=y

        v2=mytext2
        ########
        Actual_image3 = cv2.imread("static/test/Z"+fn)
        Sample_img3 = cv2.resize(Actual_image3,(400,350))
        Image_ht,Image_wd,Image_thickness = Sample_img3.shape
        Sample_img3 = cv2.cvtColor(Sample_img3,cv2.COLOR_BGR2RGB)
        texts3 = pytesseract.image_to_data(Sample_img3) 
        mytext3=""
        prevy3=0

        
        
        for cnt3,text3 in enumerate(texts3.splitlines()):
            
            if cnt3==0:
                continue
            text3 = text3.split()
            if len(text3)==12:
                x,y,w,h = int(text3[6]),int(text3[7]),int(text3[8]),int(text3[9])
                if(len(mytext3)==0):
                    prey=y
                if(prevy3-y>=10 or y-prevy3>=10):
                    print(mytext3)
                    #mytext3=""
                    
                mytext3 = mytext3 + text3[11]+" "
                prevy3=y

        v3=mytext3
        ####
        print("v1="+v1)
        print("v2="+v2)
        print("v3="+v3)
        ss=v1+"|"+v2+"|"+v3
        mycursor.execute("SELECT count(*) FROM sf_files where value1=%s && value2=%s && value3=%s",(v1,v2,v3))
        ctt = mycursor.fetchone()[0]
        if ctt>0:
            msg="1"
            mycursor.execute("SELECT * FROM sf_files where value1=%s && value2=%s && value3=%s",(v1,v2,v3))
            cdata = mycursor.fetchone()
            rid2=str(cdata[0])
            if rid==rid2:
                msg2="1"
               
         
        else:
            msg="2"

    ff=open("static/ff.txt","r")
    fst=ff.read()
    ff.close()
    face_st=""
    if fst=="yes":
        face_st="Face has matched"
    else:
        face_st="Face not match!"

    ff=open("static/tt.txt","r")
    tst=ff.read()
    ff.close()
    ts=tst.split("/")
    test_st=""
    res=""
    tst1=ts[0]
    tst2=ts[1]
   
            

    return render_template('decode3.html',msg=msg,fst=fst,tst1=tst1,tst2=tst2,rid=rid,msg2=msg2,dat=dat,ctype=ctype,s1=s1,face_st=face_st,na=na,dob=dob,gender=gender,aadhar=aadhar,address=address,v1=v1,v2=v2,v3=v3)




@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    #session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
