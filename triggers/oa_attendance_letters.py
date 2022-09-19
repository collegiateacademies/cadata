import sys
sys.path.append("..")
from src.main import *

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)

generate_attendance_letters('OA', '2022-08-08', repeated_letters=True)