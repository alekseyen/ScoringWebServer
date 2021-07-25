from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired


class ExampleSelectField(FlaskForm):
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