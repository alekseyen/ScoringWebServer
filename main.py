import json
import os
from typing import List

import pandas as pd
from flask import Flask
from flask import abort
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation

from modeling import run

# TODO

# - early_stopping в catboost, чтобы не было по 1k итераций, он явно быстрее сходиться

# - nginx. reversed proxy server.
# См вот тут: https://github.com/sachua/mlflow-docker-compose (крутой проект)

# - подружить optuna с mlflow

# - прочитать про аналогичные REST проекты
# NGINX + FLASK: https://towardsdatascience.com/how-to-deploy-ml-models-using-flask-gunicorn-nginx-docker-9b32055b3d0
# https://towardsdatascience.com/machine-learning-prediction-in-real-time-using-docker-and-python-rest-apis-with-flask-4235aa2395eb
# https://towardsdatascience.com/build-and-run-a-docker-container-for-your-machine-learning-model-60209c2d7a7f

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
