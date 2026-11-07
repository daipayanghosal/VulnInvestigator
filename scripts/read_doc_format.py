import os

path = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\2)Format_Mid & Final.doc"
with open(path, 'rb') as f:
    content = f.read()

# Extract readable ASCII / UTF-16 text
import re
text_chunks = re.findall(b'[\x20-\x7E]{4,}', content)
readable = [c.decode('latin1') for c in text_chunks]
print("Found chunks:", len(readable))
for c in readable[:40]:
    if any(k in c.lower() for k in ['mid', 'final', 'format', 'report', 'chapter', 'section', 'contents', 'bits']):
        print(" ", c)
