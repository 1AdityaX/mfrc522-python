from . import MFRC522


class SimpleMFRC522:
    def __init__(self):
        self.MFRC522 = MFRC522()
        self.KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.BLOCK_ADDRS = [8, 9, 10]
    
    def read(self):
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
        return id, text

    def read_id(self):
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None
        return self.uid_to_num(uid)

    def read_no_block(self):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, 11, self.KEY, uid)
        try:
            data = []
            text_read = ''
            if status == self.MFRC522.MI_OK:
                for block_num in self.BLOCK_ADDRS:
                    block = self.MFRC522.ReadTag(block_num)
                    if block:
                        data += block
                if data:
                    text_read = ''.join(chr(i) for i in data)
            self.MFRC522.StopCrypto1()
            return id, text_read
        except:
            self.MFRC522.StopCrypto1()
            return None, None

    def write(self, text):
        id, text_in = self.write_no_block(text)
        while not id:
            id, text_in = self.write_no_block(text)
        return id, text_in

    def write_no_block(self, text):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, 11, self.KEY, uid)
        try:
            self.MFRC522.ReadTag(11)
            if status == self.MFRC522.MI_OK:
                data = bytearray()
                data.extend(bytearray(text.ljust(
                    len(self.BLOCK_ADDRS) * 16).encode('ascii')))
                i = 0
                for block_num in self.BLOCK_ADDRS:
                    self.MFRC522.WriteTag(block_num, data[(i*16):(i+1)*16])
                    i += 1
            self.MFRC522.StopCrypto1()
            return id, text[0:(len(self.BLOCK_ADDRS) * 16)]
        except:
            self.MFRC522.StopCrypto1()
            return None, None

    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
