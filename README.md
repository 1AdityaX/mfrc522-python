# MFRC522-python
The mfrc522 library is used to interact with RFID readers that use the MFRC522 chip.


# Example Code

 **read.py**
 
 To read a particular sector and convert the bytes to plain string/text.
```py
from mfrc522 import MFRC522

reader = MFRC522()
def read(trailer_block, key, block_addrs):
    (status, TagType) = reader.Request(reader.PICC_REQIDL)
    if status != reader.MI_OK:
        return None, None
    (status, uid) = reader.Anticoll()
    if status != reader.MI_OK:
        return None, None
    id = self.uid_to_num(uid)
    reader.SelectTag(uid)
    status = reader.Auth(
        reader.PICC_AUTHENT1A, trailer_block , key, uid)
    data = []
    text_read = ''
    if status == reader.MI_OK:
        for block_num in block_addrs:
            block = reader.ReadTag(block_num)
            if block:
                data += block
        if data:
            text_read = ''.join(chr(i) for i in data)
    reader.StopAuth()
    return id, text_read

trailer_block = 11
key = KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
block_addrs = [8, 9, 10]
id, text = read(trailer_block, key, block_addrs)
while not id:
    id, text = read(trailer_block, key, block_addrs)

print(id)
print(text)
```

**write.py**

To write a particular sector.
```py
from mfrc522.MFRC522 import MFRC522

reader = MFRC522()

def write(trailer_block, key, block_addrs, text):
    (status, TagType) = reader.Request(reader.PICC_REQIDL)
        if status != reader.MI_OK:
            return None, None
        (status, uid) = reader.Anticoll()
        if status != reader.MI_OK:
            return None, None
        id = uid
        reader.SelectTag(uid)
        status = reader.Auth(
            reader.PICC_AUTHENT1A, trailer_block, key, uid)
        reader.ReadTag(trailer_block)
        if status == reader.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(
                len(block_addrs) * 16).encode('ascii')))
            i = 0
            for block_num in block_addrs:
                reader.WriteTag(block_num, data[(i*16):(i+1)*16])
                i += 1
        reader.StopAuth()
        return id, text[0:(len(block_addrs) * 16)]

trailer_block = 11
block_addrs = [8, 9, 10]
key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
text = "some random text"
id, text = write(trailer_block, key, block_addrs, text)
while not id:
    id, text = write(trailer_block, key, block_addrs, text)
print(id, text)

```


