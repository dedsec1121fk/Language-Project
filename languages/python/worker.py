#!/usr/bin/env python3
import sys
KEY=0x59
for line in sys.stdin:
    line=line.rstrip("\r\n")
    if line=="PING": print("PONG",flush=True); continue
    if line=="QUIT": break
    if len(line)>=2 and line[0] in "ED" and line[1]==" ":
        try: print(bytes(b^KEY for b in bytes.fromhex(line[2:])).hex(),flush=True)
        except ValueError: print("ERR",flush=True)
    else: print("ERR",flush=True)
