import json
import os
from typing import List

import pandas as pd
from flask import Flask
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation

from modeling import run

app = Flask(__name__)

app.config.update(
    dict(SECRET_KEY="powerful secretkey", WTF_CSRF_SECRET_KEY="a csrf secret key")
)


@app.route("/badrequest400")
def bad_request():
    return abort(400)


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

try:
    os.mkdir(UPLOAD_FOLDER)
except:
    print("uploads already exist")
    pass


def check_file_type(valid_types: List[str] = ["csv"]):
    def validate_file_type(form, field):
        file_extension = form.file.data.filename.split(".")[1]

        if file_extension not in valid_types:
            field.errors[:] = []
            raise StopValidation(field.gettext("CSV is required."))

    return validate_file_type


class SubmitForm(FlaskForm):
    """Sign up for a user account."""

    learning_field = SelectField(
        label="Choose learning way",
        choices=[
            ("single", "single"),
            ("optuna", "optuna"),
            ("grid", "grid"),
            ("randomized", "randomized"),
        ],
    )

    file = FileField(validators=[DataRequired(), check_file_type()])


@app.route("/", methods=["GET", "POST"])
def main():
    """User sign-up form for account creation."""
    form = SubmitForm(learning_field="single")

    if form.validate_on_submit():
        df = pd.read_csv(form.file.data)

        run(df, search_type=form.learning_field.data)

        return """
            <!doctype html>
            <h1>success</h1>
            """

    return render_template("template_field.html", form=form)


@app.route("/send_csv", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)


        file = request.files["file"]

        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        filename = secure_filename(file.filename)

        ### validate datetype

        if filename[-3:] != "csv":
            redirect(
                url_for(
                    "upload_file",
                )
            )

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        df = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        #### validate csv

        run(df, search_type = json.load(request.files["param"])['search_type'])

        return "file uploaded"

    return """
    <!doctype html>
    <title> Upload </title>

    <h1> Upload csv</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    """
