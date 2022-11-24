#-*- coding: utf-8 -*-
from flask import Flask, render_template, Response, jsonify,request
from Pose_Analyze import main
import time
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


#设置允许的文件格式
ALLOWED_EXTENSIONS = {'mp4'}

@app.route('/')
def index():
    return render_template("login.html")


@app.route('/cam',methods=['GET','POST'])
def cam():
    str = "hello"

    return render_template("index.html",str=str)


@app.route('/video_feed',methods=['GET','POST'])
def video_feed():
    return Response(main(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        print(request.form)
        txtname = request.args.get('username')
        txtpswd = request.args.get('userpswd')

        if (txtname == "longdb" and txtpswd == "123"):
            return "success"  # get可以到这里
        else:
            return "enterfailed"




if __name__ == '__main__':
    app.run(host='172.17.152.170',debug=True,port=6001)