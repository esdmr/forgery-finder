from os.path import dirname, join
from sys import path

path.append(join(dirname(__file__), "src"))

from forgery_finder import app  # type: ignore
