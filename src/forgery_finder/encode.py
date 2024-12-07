from base64 import b64encode
import cv2 as cv
import cv2.typing as cvt


def to_png(i: cvt.MatLike) -> bytes:
    return bytes(cv.imencode(".png", i)[1])


def to_data_url(i: cvt.MatLike) -> str:
    return "data:image/png;base64," + b64encode(to_png(i)).decode()
