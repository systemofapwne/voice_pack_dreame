#!/usr/bin/env python3


import pandas as pd

en = list(pd.read_csv("sound_list.csv", header = None)[1])
de = list(pd.read_csv("sound_list_de.csv", header = None)[1])

start = 132
for i in range(len(en)):
    if i < start: continue
    print(f"EN[{i}]: {en[i]}")
    print(f"DE[{i}]: {de[i]}")
    input("Press Enter to continue...")