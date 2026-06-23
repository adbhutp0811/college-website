f = open('C:\\Users\\adbhu\\AppData\\Local\\Temp\\opencode\\test_id_card.pdf', 'rb')
c = f.read()
f.close()
t = c.decode('latin-1')
strings_to_find = ['MIRACLE INSTITUTE', 'STUDENT IDENTITY', 'Roll No', 'B.Tech', 
                   'Date of Birth', 'Gender', 'Blood Group', 'Father']
for s in strings_to_find:
    if s in t:
        print('FOUND: ' + s)
    else:
        print('NOT FOUND: ' + s)

# Print PDF structure summary
print()
print('PDF length:', len(c))
print('First 500 chars:', repr(t[:500]))
print()
print('Last 500 chars:', repr(t[-500:]))
