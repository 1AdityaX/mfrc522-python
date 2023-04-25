from . import MFRC522


class SimpleMFRC522:
    """
    A class for reading and writing data using the MFRC522 RFID module.

    Attributes:
        MFRC522 (module): The MFRC522 module used for communication with the RFID reader.
        KEY (list): The default authentication key used for reading and writing data.
        BLOCK_ADDRS (list): The list of block addresses used for reading and writing data.
    """

    def __init__(self):
        """
        Initializes a SimpleMFRC522 instance.
        """
        
        self.MFRC522 = MFRC522()
        self.KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.BLOCK_ADDRS = [8, 9, 10]
    
    def read(self):
        """
        Reads data from the RFID tag.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data read (as a string).
        """
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
        return id, text

    def read_id(self):
        """
        Reads the tag ID from the RFID tag.

        Returns:
            id (int): The tag ID as an integer.
        """
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        """
        Attempt to read the tag ID from the RFID tag.

        Returns:
            id (int): The tag ID as an integer, or None if the operation fails.
        """

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None

        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None

        # Convert UID to integer and returns id
        return self._uid_to_num(uid)

    def read_no_block(self):
        """
        Attempt to read the data from the RFID tag.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data read (as a string), or (None, None) if the operation fails.
        """

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None
        
        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None
        
        # Convert UID to integer and returns id
        id = self._uid_to_num(uid)
        
        # Select tag and authenticate using the stored key
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(self.MFRC522.PICC_AUTHENT1A, 11, self.KEY, uid)
        
        try:
            data = []
            text_read = ''
            # Read each block in the specified address range
            if status == self.MFRC522.MI_OK:
                for block_num in self.BLOCK_ADDRS:
                    block = self.MFRC522.ReadTag(block_num)
                    if block:
                        data += block
                # If data was read, convert it to a string
                if data:
                    text_read = ''.join(chr(i) for i in data)
            # Stop the crypto1 communication after reading
            self.MFRC522.StopCrypto1()
            # Return ID and data read from the tag
            return id, text_read
        except:
            self.MFRC522.StopCrypto1()
            # Return None if an exception occurred during reading
            return None, None

    def write(self, text):
        """
        Writes the given text to an RFID tag.

        Args:
            text (str): A string to be written to the RFID tag.

        Returns:
            tuple: A tuple containing the ID of the tag and the text that was written to the tag.
        """

        id, text_in = self.write_no_block(text)
        while not id:
            id, text_in = self.write_no_block(text)
        return id, text_in

    def write_no_block(self, text):
        """
        Attempt to write the given text to a RFID tag.

        Args:
            text (str): The text to write to the RFID tag.

        Returns:
            tuple: A tuple containing the ID of the RFID tag (as an integer) and
                the portion of the text that was successfully written to the tag.
                If the write operation failed, returns (None, None).
        """

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None

        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None

        # Convert UID to integer and returns id
        id = self._uid_to_num(uid)

        # Select tag and authenticate using the stored key
        self.MFRC522.SelectTag(uid)
        status = self.MFRC522.Authenticate(
            self.MFRC522.PICC_AUTHENT1A, 11, self.KEY, uid)

        try:
            # Write the text to each block on the tag
            self.MFRC522.ReadTag(11)
            if status == self.MFRC522.MI_OK:
                data = bytearray()
                data.extend(bytearray(text.ljust(
                    len(self.BLOCK_ADDRS) * 16).encode('ascii')))
                i = 0
                for block_num in self.BLOCK_ADDRS:
                    self.MFRC522.WriteTag(block_num, data[(i*16):(i+1)*16])
                    i += 1

            # Stop the crypto1 communication after writing
            self.MFRC522.StopCrypto1()
            return id, text[0:(len(self.BLOCK_ADDRS) * 16)]

        except:
            # Stop the crypto1 communication on exception
            self.MFRC522.StopCrypto1()
            return None, None

    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
