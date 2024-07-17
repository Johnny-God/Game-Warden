import psutil
import os
import signal
import time
from datetime import datetime, time as dtime
from win10toast import ToastNotifier
import setproctitle

toaster = ToastNotifier()
setproctitle.setproctitle("Game Warden")

def terminate_process_tree(pid):
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        try:
            os.kill(child.pid, signal.SIGTERM)
        except psutil.NoSuchProcess:
            continue
    try:
        os.kill(pid, signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass

def check_and_terminate_steam():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'].lower() == 'steam.exe':
            terminate_process_tree(process.info['pid'])
            toaster.show_toast(
                "Gaming Lockout Active",
                f"Terminated Steam process tree with PID {process.info['pid']}",
                duration=3  # Duration in seconds
            )
            print(f"Terminated Steam process tree with PID {process.info['pid']}")
            return
    print("Steam is not running")

def should_terminate():
    now = datetime.now()
    day_of_week = now.weekday()  # Monday is 0 and Sunday is 6
    current_time = now.time()

    # Time ranges for checking
    evening_start = dtime(hour=18, minute=0, second=0)
    evening_end = dtime(hour=20, minute=0, second=0)
    afternoon_start = dtime(hour=14, minute=0, second=0)

    if day_of_week == 3:  # Thursday (index 3)
        return False
    if (day_of_week >= 4 or day_of_week == 0) and (evening_start <= current_time <= evening_end):
        return False
    if day_of_week == 2 and current_time > afternoon_start:
        return False
    return True

if __name__ == "__main__":
    while True:
        if should_terminate():
            check_and_terminate_steam()
        time.sleep(1)
