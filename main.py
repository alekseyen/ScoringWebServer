import os

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
from wtforms import SelectField
from wtforms.validators import DataRequired

from modeling import run

# TODO
# добавить авто проверки типа тех, что были в ETNA
# настроить CI на гитхабе
# добавить в mlflow параметр тип обучения: single, grid, random
# запустить и почекать какие там параметры получаются
# исправить endpoint (все в формате templatet'ов)
# добавить на главную страничку с selected-форму для выбора типа обучения
# прикрутить optuna для подбора параметров (https://www.kaggle.com/satorushibata/optimize-catboost-hyperparameter-with-optuna-gpu)
# подружить их с mlflow
# делать return предсказаных значений в POST запросе

# прочитать про REST проекты
# https://towardsdatascience.com/machine-learning-prediction-in-real-time-using-docker-and-python-rest-apis-with-flask-4235aa2395eb
# https://towardsdatascience.com/build-and-run-a-docker-container-for-your-machine-learning-model-60209c2d7a7f
#

app = Flask(__name__)

app.config.update(
    dict(SECRET_KEY="powerful secretkey", WTF_CSRF_SECRET_KEY="a csrf secret key")
)


@app.route("/badrequest400")
def bad_request():
    return abort(400)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "csv"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# if not os.path.exists(UPLOAD_FOLDER):
#     os.mkdir(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file")
            print("didn't sent any files")
            return redirect(request.url)

        if file and allowed_file(file.filename):
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

            # todo: поставить в очередь, отпустить сайт
            run(df)

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


# todo: Test
class TEST(FlaskForm):
    """Sign up for a user account."""

    title = SelectField(
        "Title",
        [DataRequired()],
        choices=[
            ("Farmer", "farmer"),
            ("Corrupt Politician", "politician"),
            ("No-nonsense City Cop", "cop"),
            ("Professional Rocket League Player", "rocket"),
            ("Lonely Guy At A Diner", "lonely"),
            ("Pokemon Trainer", "pokemon"),
        ],
    )


@app.route("/test", methods=["GET", "POST"])
def test():
    """User sign-up form for account creation."""
    form = TEST()
    if form.validate_on_submit():
        return redirect(url_for("success"))

    return render_template("template_test.html", form=form)
