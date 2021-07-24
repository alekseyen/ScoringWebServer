import subprocess

import pandas as pd
from flask import Flask, abort, redirect, url_for, request, jsonify, render_template, send_file, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from run_model import run

app = Flask(__name__)

app.config.update(dict(SECRET_KEY="powerful secretkey",
                       WTF_CSRF_SECRET_KEY="a csrf secret key"
                       ))


@app.route('/badrequest400')
def bad_request():
    return abort(400)


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            print("didn't sent any files")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            ### validate datetype

            if filename[-3:] != 'csv':
                redirect(url_for('upload_file', ))

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #### validate csv

            # if 'target' in df.columns:
            #     redirect(url_for('upload_file', ))

            # поставить в очередь, отпустить сайт
            run(df)

            return 'file uploaded'

    return '''
    <!doctype html>
    <title> Upload </title>
    <h1> Upload csv</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''
