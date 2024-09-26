from functions import *

try:
    driver = bot_setup()
except:
    print("Failed to setup bot.")
    exit()