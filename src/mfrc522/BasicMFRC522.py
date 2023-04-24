from . import MFRC522


class BasicMFRC522:
    def __init__(self, KEY=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]):
        self.MFRC522 = MFRC522()
        self.KEY = KEY

    def read_sector(self, trailer_block=11):
        id, text = self.read_no_block(
            trailer_block, (trailer_block-3, trailer_block-2, trailer_block-1))
        while not id:
            id, text = self.read_no_block(
                trailer_block, (trailer_block-3, trailer_block-2, trailer_block-1))
        return id, text

    def read_sectors(self, trailer_blocks=[11]):
        text_all = ''
        for trailer_block in trailer_blocks:
            id, text = self.read_sector(trailer_block)
            text_all += text
        return id, text_all

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

    def read_no_block(self, trailer_block, block_addr):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)
        data = []
        text_read = ''
        try:
            if status == self.MFRC522.MI_OK:
                for block_num in block_addr:
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

    def write_sector(self, text, trailer_block=11):
        block_addr = [trailer_block-3, trailer_block-2, trailer_block-1]
        id, text_in = self.write_no_block(text, trailer_block, block_addr)
        while not id:
            id, text_in = self.write_no_block(text, trailer_block, block_addr)
        return id, text_in

    def write_sectors(self, text, trailer_blocks=[11]):
        text_formated_list = self.split_string(text)
        text_all = ''
        for i in range(0, len(trailer_blocks)):
            try:
                id, text = self.write_sector(
                    text_formated_list[i], trailer_blocks[i])
                text_all += text
            except IndexError:
                pass
        return id, text_all

    def write_no_block(self, text, trailer_block, block_addr):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)
        self.MFRC522.ReadTag(trailer_block)
        try:
            if status == self.MFRC522.MI_OK:
                data = bytearray()
                data.extend(bytearray(text.ljust(
                    len(block_addr) * 16).encode('ascii')))
                i = 0
                for block_num in block_addr:
                    self.MFRC522.WriteTag(block_num, data[(i*16):(i+1)*16])
                    i += 1
            self.MFRC522.StopCrypto1()
            return id, text[0:(len(block_addr) * 16)]
        except:
            self.MFRC522.StopCrypto1()
            return None, None

    def clear_no_sector(self, trailer_block):
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None
        id = self.uid_to_num(uid)
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)
        self.MFRC522.ReadTag(trailer_block)
        block_addr = [trailer_block-3, trailer_block-2, trailer_block-1]
        try:
            if status == self.MFRC522.MI_OK:
                data = [0x00]*16
                for block_num in block_addr:
                    self.MFRC522.WriteTag(block_num, data)
            self.MFRC522.StopCrypto1()
            return id
        except:
            self.MFRC522.StopCrypto1()
            return None

    def clear_sector(self, trailer_block):
        id = self.clear_no_sector(trailer_block)
        while not id:
            id = self.clear_no_sector(trailer_block)
        return id

    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

    def split_string(self, s):
        l = list()
        for i in range(0, len(s), 48):
            l.append(s[i:i+48])
        if len(l[-1]) < 48:
            l[-1] += '\0'*(48-len(l[-1]))
        return l
