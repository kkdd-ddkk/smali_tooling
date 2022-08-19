
def myexit():
    print("\x1b[101;93m   THIS IS  THE END   \x1b[0m")
    print("\x1b[101;93m   BEAUTIFUL FRIEND   \x1b[0m")

    exit()



import random 
import string
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_uppercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str