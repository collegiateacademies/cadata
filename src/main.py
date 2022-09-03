from util import *
sys.path.append("..")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)