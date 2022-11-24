# -*- coding: utf-8 -*-
import os
from flask import Flask, request, url_for, send_from_directory, render_template,Response
from werkzeug.utils import secure_filename
from Pose_Analyze import main


ALLOWED_EXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "D:\Mr Huang\DeepLearning\pose_evaluate"
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

file_up = ""

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
    <input type="submit" value="Upload">
</form>
    '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            global file_up, str
            file_up = filename
            print(file_up)

    a = []

    print(a)

    return render_template("index.html",a=a)

@app.route('/cam',methods=['GET','POST'])
def cam():
    str = "hello"
    return render_template("index.html",str=str)


@app.route('/video_feed',methods=['GET','POST'])
def video_feed():
    return Response(main(file_up), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run()