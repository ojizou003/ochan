from datetime import datetime
import pytz

from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_wtf.csrf import CSRFProtect

from config import Config
from filters import authorformat, datetimeformat, whoformat, uuidshort
from forms import ResForm, ThreadForm
from models import Board, BoardCategory, Res, Thread, db
from utils import get_b64encoded_digest_string_from_words, normalize_uuid_string

app = Flask(__name__)
app.config.from_object(Config)
app.debug = Config.DEBUG
csrf = CSRFProtect(app)
db.init_app(app)

app.add_template_filter(datetimeformat)
app.add_template_filter(authorformat)
app.add_template_filter(whoformat)
app.add_template_filter(uuidshort)

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def index():
    board_categories = BoardCategory.query.all()
    flash('welcome')
    return render_template("index.html", board_categories=board_categories)

@app.route("/guideline")
def guideline():
    return render_template("guideline.html")

@app.route("/boards/<board_id>", methods=["GET", "POST"])
def board(board_id):
    try:
        board_uuid = normalize_uuid_string(board_id)
        board = Board.query.get(board_uuid)

        form = ThreadForm()
        if form.validate_on_submit():
            thread = Thread(name=form.thread_name.data, board_id=board_uuid)
            ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
            japan_tz = pytz.timezone('Asia/Tokyo')
            today_utc = datetime.now(japan_tz).strftime("%Y%m%d")
            res = Res(
                number=thread.next_res_number,
                anon_name=form.anon_name.data or None,
                anon_email=form.anon_email.data or None,
                who=get_b64encoded_digest_string_from_words(ip, today_utc),
                body=form.body.data,
            )
            thread.reses.append(res)
            try:
                db.session.add(thread)
                db.session.commit()
                return redirect(request.url)
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error creating thread: {str(e)}")
                flash('スレッドの作成中にエラーが発生しました。', 'error')
                return redirect(request.url)
        return render_template("board.html", board=board, form=form)
    except Exception as e:
        logger.error(f"Unexpected error in board route: {str(e)}")
        flash('予期せぬエラーが発生しました。', 'error')
        return redirect(url_for('index'))

@app.route("/threads/<thread_id>", methods=["GET", "POST"])
def thread(thread_id):
    thread_uuid = normalize_uuid_string(thread_id)
    thread = Thread.query.get(thread_uuid)

    form = ResForm()
    if form.validate_on_submit():
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        japan_tz = pytz.timezone('Asia/Tokyo')
        today_utc = datetime.now(japan_tz).strftime("%Y%m%d")
        res = Res(
            number=thread.next_res_number,
            anon_name=form.anon_name.data or None,
            anon_email=form.anon_email.data or None,
            who=get_b64encoded_digest_string_from_words(ip, today_utc),
            body=form.body.data,
        )
        thread.reses.append(res)
        db.session.commit()
        return redirect(url_for("thread", thread_id=thread_id, _anchor="res-form"))

    anchor = "res-form" if form.is_submitted() else None
    return render_template("thread.html", thread=thread, form=form, anchor=anchor)

# 404エラーハンドラー
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 500エラーハンドラー
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 一般的なHTTPエラーハンドラー
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

# データベースエラーハンドラー
@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    logger.error(f"Database error occurred: {str(e)}")
    return render_template('db_error.html'), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)