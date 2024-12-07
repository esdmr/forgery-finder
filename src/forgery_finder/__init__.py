from os import environ, path
from secrets import token_bytes
from re import compile
from hmac import compare_digest

from flask import Flask, request, Request
from flask.helpers import make_response, redirect
from flask.templating import render_template
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException, NotFound, BadRequest, Unauthorized
from os.path import dirname, join
from . import pil_image as img
from .verify import verify
from .encode import to_data_url

app = Flask(
    __name__,
    static_url_path="",
    static_folder=join(dirname(__file__), "static"),
    template_folder=join(dirname(__file__), "template"),
)

app.config["SECRET_KEY"] = token_bytes()
app.config["SESSION_COOKIE_SECURE"] = environ.get("FORGERY_FINDER_USING_HTTPS") == "1"

USERNAME_PATTERN = compile(r"^\w+$")


def is_html(req: Request = request) -> bool:
    return "text/html" in (req.headers.get("Accept") or "")


class InvalidUsername(BadRequest):
    description = (
        "The format of the username is invalid."
        " Please check your spelling and try again."
    )

    @property
    def name(self) -> str:
        return "Invalid Username"


class InvalidPassword(Unauthorized):
    description = (
        "The given password is invalid." " Please check your spelling and try again."
    )

    @property
    def name(self) -> str:
        return "Invalid Password"


class UsernameNotFound(NotFound):
    description = (
        "The requested user was not found on the server."
        " Please check your spelling and try again."
    )

    @property
    def name(self) -> str:
        return "Username Not Found"


@app.errorhandler(HTTPException)
def on_bad_request_error(e: HTTPException) -> ResponseReturnValue:
    json = {"error": e.name, "code": e.code, "description": e.description}

    if is_html():
        return make_response(render_template("error.html", **json), e.code)
    else:
        return make_response(json, e.code)


@app.route("/", methods=["GET"])
def on_root_get() -> ResponseReturnValue:
    return redirect("/index.html")


@app.route("/api/verify", methods=["POST"])
def on_verify_post() -> ResponseReturnValue:
    username = request.form["username"]
    original_path = join(dirname(__file__), "images", username + ".png")

    if not USERNAME_PATTERN.match(username):
        raise InvalidUsername()

    if not path.isfile(original_path):
        raise UsernameNotFound()

    uploaded_image_pil = img.open(request.files["file_upload"].stream)
    original_image_pil = img.open(original_path)

    result = verify(uploaded_image_pil, original_image_pil)

    json = {
        "score": round(result.score * 100, 2),
        "uploaded": to_data_url(result.uploaded),
        "original": to_data_url(result.original),
        "diff": to_data_url(result.diff),
        "threshold": to_data_url(result.threshold),
    }

    if is_html():
        return render_template("verify.html", **json)
    else:
        return json


@app.route("/api/upload", methods=["POST"])
def on_upload_post() -> ResponseReturnValue:
    username = request.form["username"]
    original_path = join(dirname(__file__), "images", username + ".png")
    password = request.form["password"].strip()

    if not USERNAME_PATTERN.match(username):
        raise InvalidUsername()

    try:
        with open(
            join(dirname(__file__), "..", "..", "secrets", "upload.txt"), "r"
        ) as f:
            upload_password = f.read().strip()
    except:
        # Disables uploading
        upload_password = None

    if not isinstance(upload_password, str) or not compare_digest(
        password.encode(), upload_password.encode()
    ):
        raise InvalidPassword()

    uploaded_image_pil = img.open(request.files["file_upload"].stream)
    img.save(uploaded_image_pil, original_path)
    json = {"ok": True}

    if is_html():
        return render_template("upload.html", **json)
    else:
        return json
