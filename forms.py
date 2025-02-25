from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from config import ANON_NAME_MAX_LENGTH, BODY_MAX_LENGTH, THREAD_NAME_MAX_LENGTH


class ResForm(FlaskForm):
    anon_name = StringField(
        "名前(省略可)",
        validators=[Length(max=ANON_NAME_MAX_LENGTH)],
    )
    anon_email = StringField(
        "メールアドレス(省略可)",
        validators=[Optional(), Email()],
    )
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
    )


class ThreadForm(FlaskForm):
    thread_name = StringField(
        "スレッド名",
        validators=[Length(max=THREAD_NAME_MAX_LENGTH)],
    )
    anon_name = StringField(
        "名前(省略可)",
        validators=[Length(max=ANON_NAME_MAX_LENGTH)],
    )
    anon_email = StringField(
        "メールアドレス(省略可)",
        validators=[Optional(), Email()],
    )
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
    )