file = open('music_db.xml', 'r', encoding='shift_jisx0213')
data = file.read()
et = ET.fromstring(data): element

# get names
for child in et:
    print(child.find('info').find('title_name'))