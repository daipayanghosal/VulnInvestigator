import os
import re

path = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\1)Guidelines for dissertation.doc"
with open(path, 'rb') as f:
    content = f.read()

text_chunks = re.findall(b'[\x20-\x7E]{4,}', content)
readable = [c.decode('latin1') for c in text_chunks]
print("Found chunks:", len(readable))
for c in readable:
    if any(k in c.lower() for k in ['mid-sem', 'mid sem', 'midterm', 'mid semester', 'evaluation']):
        print(" ", c)
