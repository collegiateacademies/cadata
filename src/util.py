import base64, requests, datetime, pprint, json, csv, logging, sys
from pathlib import Path

pp = pprint.PrettyPrinter(indent=2)

# ANSI Escape Codes

# Colors
black = "\u001b[30m"
red = "\u001b[31m"
green = "\u001b[32m"
yellow = "\u001b[33m"
blue = "\u001b[34m"
magenta = "\u001b[35m"
cyan = "\u001b[36m"
white = "\u001b[37m"
reset = "\u001b[0m"

# Text Decorations
bold = "\u001b[1m"
underline = "\u001b[4m"

sys.path.append("..")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)