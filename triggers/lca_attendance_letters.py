import sys
sys.path.append("..")
from src.main import *

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)

generate_attendance_letters('LCA', '2022-08-01', repeated_letters=False)