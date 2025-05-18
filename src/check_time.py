import datetime

def check_time():
    now = datetime.datetime.now()
    print("Current time:", now.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    check_time()
