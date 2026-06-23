import zlib

f = open('C:\\Users\\adbhu\\AppData\\Local\\Temp\\opencode\\test_id_card.pdf', 'rb')
c = f.read()
f.close()

# Find stream content
t = c.decode('latin-1')
start = t.find('stream\n') + len('stream\n')
end = t.find('\nendstream')
raw = c[start:end]

# Try to decompress
try:
    decompressed = zlib.decompress(raw)
    print(decompressed.decode('latin-1'))
except:
    print('Could not decompress, showing raw:')
    print(raw[:200])
