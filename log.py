from datetime import datetime


state = None
valg = None

first_log = False
running = False
close = False

def log(state ,valg, valg_log):
    time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if close:
        log = open("log.txt", "a")
        log.write(f"{time}  log closing\n=============================\n\n\n\n")
        log.close
        return

    if first_log == False:
        log = open("log.txt", "a")
        log.write(f"{time}: {state}    {valg}  {valg_log}\n")
        log.close
    else:
        log = open("log.txt", "a")
        log.write(f"log starts at {time}.\n\n")
        log.close
