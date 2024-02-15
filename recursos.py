
#!/usr/bin/python3

import os
import subprocess
import time
from datetime import datetime, timedelta

INTERVAL_DEFAULT = 3
LIMPIA_FICHEROS = True
OUTPUT_FOLDER = './output'

class Recurso:
    def __init__(
        self,
        name: str,
        file: str,
        command: str,
        interval: int = INTERVAL_DEFAULT,
        add_timestamp: bool = False,
        add_separation_line: bool = False,
    ):
        self.name = name
        self.file = os.path.join(OUTPUT_FOLDER, file)
        self.command = command
        self.interval = interval
        self.last_updated = datetime.now() - timedelta(minutes=10)
        self.add_timestamp = add_timestamp
        self.add_separation_line = add_separation_line

    def update(self):
        self.last_updated = datetime.now()
    
    def log(self, text):
        with open(self.file, 'a') as file:
            if self.add_timestamp:
                file.write(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            file.write(text)
            if self.add_separation_line:
                file.write(f"\n")
        self.update()



def limpia(recursos):
    for recurso in recursos:
        if os.path.exists(recurso.file):
            os.remove(recurso.file)



def run(recursos):
    try:
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        if LIMPIA_FICHEROS:
            limpia(recursos)
            
        while True:
            for recurso in recursos:
                if (datetime.now() - recurso.last_updated).seconds > recurso.interval:
                    result = subprocess.run(recurso.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)
                    recurso.log(result.stdout)
                    
            time.sleep(1)

    except KeyboardInterrupt:
        print("exiting...")


def main():
    # cpu
    top = Recurso(name="TOP", file="top.txt", command="top -b -n 1 | head -15", add_separation_line=True, interval=10)
    mpstat = Recurso("MPSTAT", "mpstat.txt", "mpstat")

    # mem
    free = Recurso("MEMORY", "free.txt", "free -m", add_separation_line=True, add_timestamp=True)
    vmstat = Recurso("VMSTAT", "vmstat.txt", "vmstat", add_separation_line=True, add_timestamp=True)

    # red
    interfaces = Recurso("INTERFACES", "interfaces.txt", "netstat -i", interval=5, add_timestamp=True, add_separation_line=True)

    # disco
    iostat = Recurso("IOSTAT", "iostat.txt", "iostat", interval=5, add_timestamp=True)
    df = Recurso("DF", "df.txt", "df -h", interval=60, add_timestamp=True, add_separation_line=True)

    # otros
    docker = Recurso("DOCKER", "docker.txt", "docker ps", interval=30, add_separation_line=True, add_timestamp=True)

    recursos = [top, mpstat, free, vmstat, interfaces, iostat, df, docker]  

    run(recursos)


if __name__ == "__main__":
    main()