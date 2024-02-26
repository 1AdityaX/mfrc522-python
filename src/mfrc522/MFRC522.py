import RPi.GPIO as GPIO
import spidev
import logging
import time


class MFRC522:
    MAX_LEN = 16

    # Proximity Coupling Device
    PCD_IDLE = 0x00
    PCD_AUTHENT = 0x0E
    PCD_RECEIVE = 0x08
    PCD_TRANSMIT = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC = 0x03

    # Proximity Integrated Circuit Card
    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SElECTTAG = 0x93
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ = 0x30
    PICC_WRITE = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE = 0xC2
    PICC_TRANSFER = 0xB0
    PICC_HALT = 0x50

    # Status
    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    # MFRC522 Registers Addresses
    Reserved00 = 0x00
    CommandReg = 0x01
    CommIEnReg = 0x02
    DivlEnReg = 0x03
    CommIrqReg = 0x04
    DivIrqReg = 0x05
    ErrorReg = 0x06
    Status1Reg = 0x07
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    WaterLevelReg = 0x0B
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    CollReg = 0x0E
    Reserved01 = 0x0F

    Reserved10 = 0x10
    ModeReg = 0x11
    TxModeReg = 0x12
    RxModeReg = 0x13
    TxControlReg = 0x14
    TxAutoReg = 0x15
    TxSelReg = 0x16
    RxSelReg = 0x17
    RxThresholdReg = 0x18
    DemodReg = 0x19
    Reserved11 = 0x1A
    Reserved12 = 0x1B
    MifareReg = 0x1C
    Reserved13 = 0x1D
    Reserved14 = 0x1E
    SerialSpeedReg = 0x1F

    Reserved20 = 0x20
    CRCResultRegM = 0x21
    CRCResultRegL = 0x22
    Reserved21 = 0x23
    ModWidthReg = 0x24
    Reserved22 = 0x25
    RFCfgReg = 0x26
    GsNReg = 0x27
    CWGsPReg = 0x28
    ModGsPReg = 0x29
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    Reserved30 = 0x30
    TestSel1Reg = 0x31
    TestSel2Reg = 0x32
    TestPinEnReg = 0x33
    TestPinValueReg = 0x34
    TestBusReg = 0x35
    AutoTestReg = 0x36
    VersionReg = 0x37
    AnalogTestReg = 0x38
    TestDAC1Reg = 0x39
    TestDAC2Reg = 0x3A
    TestADCReg = 0x3B
    Reserved31 = 0x3C
    Reserved32 = 0x3D
    Reserved33 = 0x3E
    Reserved34 = 0x3F

    serNum = []

    def __init__(self, bus=0, device=0, spd=1000000, pin_mode=10, pin_rst=-1, debugLevel='WARNING'):
        """
        Initializes the MFRC522 RFID reader.

        Args:
        - bus (int): the SPI bus number (default 0).
        - device (int): the SPI device number (default 0).
        - spd (int): the SPI bus speed (default 1000000).
        - pin_mode (int): the GPIO pin numbering mode (default 10).
        - pin_rst (int): the GPIO pin number for reset (default -1, which sets the pin based on pin_mode).
        - debugLevel (str): the logging debug level (default 'WARNING').
        """
        # Initialize SPI communication
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = spd

        # Initialize logger for debugging
        self.logger = logging.getLogger('mfrc522Logger')
        self.logger.addHandler(logging.StreamHandler())
        level = logging.getLevelName(debugLevel)
        self.logger.setLevel(level)

        # Set GPIO pin numbering mode if not already set
        gpioMode = GPIO.getmode()

        if gpioMode is None:
            GPIO.setmode(pin_mode)
        else:
            pin_mode = gpioMode

        # Set reset pin based on pin_mode if not specified
        if pin_rst == -1:
            if pin_mode == 11:
                pin_rst = 25
            else:
                pin_rst = 22

        self.StopAuth = self.StopCrypto1
        # Set up reset pin and initialize MFRC522 RFID reader
        GPIO.setup(pin_rst, GPIO.OUT)
        GPIO.output(pin_rst, 1)
        self.Init()

    def Reset(self):
        """
        Reset the MFRC522 chip by writing the PCD_RESETPHASE command to the CommandReg register.

        This function sends the PCD_RESETPHASE command to the MFRC522 chip, which resets its internal state
        and clears all registers. After the reset, the chip is ready to accept new commands.
        """

        self.WriteReg(self.CommandReg, self.PCD_RESETPHASE)

    def WriteReg(self, addr, val):
        """
        Write a value to a register of the MFRC522 chip using SPI communication.

        This method sends a write command to the MFRC522 chip using the SPI interface, specifying the
        register address and the value to be written.

        Args:
            :param: (int): the address of the register to write to, in the range 0x00-0xFF.
            val (int): the value to write to the register, in the range 0x00-0xFF.
        """
        val = self.spi.xfer2([(addr << 1) & 0x7E, val])

    def ReadReg(self, addr):
        """
        Read the value of a register of the MFRC522 chip using SPI communication.

        This method sends a read command to the MFRC522 chip using the SPI interface, specifying the
        register address.

        Args:
            addr (int): the address of the register to read from, in the range 0x00-0xFF.

        Returns:
            The value read from the register.
        """
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]

    def Close(self):
        """
        Close the MFRC522 chip by releasing the SPI interface and cleaning up the GPIO.

        This method closes the SPI interface used to communicate with the MFRC522 chip, releasing any
        system resources associated with it. It also calls the `GPIO.cleanup()` function to release
        any GPIO pins that were used to control the chip.
        """
        self.spi.close()
        GPIO.cleanup()

    def SetBitMask(self, reg, mask):
        """
        Sets specific bits in a register of an MFRC522 RFID module
        by performing a bitwise OR operation with the provided mask.

        Args:
            reg (int): the register to modify
            mask (int): the bit mask to apply
        """
        # Read the current value of the register
        tmp = self.ReadReg(reg)

        # Set the desired bits using a bitwise OR operation
        self.WriteReg(reg, tmp | mask)

    def ClearBitMask(self, reg, mask):
        """
        Clears specific bits in a register of an MFRC522 RFID module
        by performing a bitwise AND operation with the complement of the provided mask.

        Args:
            reg (int): the register to modify
            mask (int): the bit mask to clear
        """
        # Read the current value of the register
        tmp = self.ReadReg(reg)

        # Clear the desired bits using a bitwise AND operation
        self.WriteReg(reg, tmp & (~mask))

    def AntennaOn(self):
        """
        Turns on the antenna of an MFRC522 RFID module by setting the TxControlReg register.

        If the antenna is already on, this method does nothing.

        """
        # Read the current value of the TxControlReg register
        temp = self.ReadReg(self.TxControlReg)

        # Check if the least significant two bits are already set
        if (temp & 0x03) != 0x03:
            # If not, turn on the antenna by setting the bits using a bit mask
            self.SetBitMask(self.TxControlReg, 0x03)

    def AntennaOff(self):
        """
        Turns off the antenna of an MFRC522 RFID module by clearing the TxControlReg register.

        """
        # Clear the least significant two bits of the TxControlReg register to turn off the antenna
        self.ClearBitMask(self.TxControlReg, 0x03)

    def MFRC522_ToCard(self, command, sendData):
        """
        Executes a command on the MFRC522 and communicates with the tag or card.

        Args:
            command (int): The command to execute.
            sendData (list): A list of bytes to send to the tag or card.

        Returns:
            tuple: A tuple containing:
                - status (int): The status of the command execution.
                - backData (list): A list of bytes received from the tag or card.
                - backLen (int): The length of the backData list.
        """
        backData = []  # List to store response data
        backLen = 0  # Length of response data
        status = self.MI_ERR  # Default status
        irqEn = 0x00  # Interrupt request enable flag
        waitIRq = 0x00  # Wait for interrupt request flag
        lastBits = None  # Number of valid bits in last byte
        n = 0  # Number of bytes received

        # Set interrupt request and wait flags based on command
        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIRq = 0x10
        if command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIRq = 0x30

        # Enable interrupts and reset FIFO buffer
        self.WriteReg(self.CommIEnReg, irqEn | 0x80)
        self.ClearBitMask(self.CommIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        # Put MFRC522 into idle state
        self.WriteReg(self.CommandReg, self.PCD_IDLE)

        # Write data to FIFO buffer
        for i in range(len(sendData)):
            self.WriteReg(self.FIFODataReg, sendData[i])

        # Start command execution
        self.WriteReg(self.CommandReg, command)

        # Set bit framing if command is transceive
        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, 0x80)

        # Wait for command execution (timeout)
        i = 2000
        while True:
            time.sleep(0.35)
            n = self.ReadReg(self.CommIrqReg)
            i -= 1
            # Break if interrupt request received or timeout
            if i == 0 or (n & 0x01) or (n & waitIRq):
                break

        # Clear bit framing if command is transceive
        self.ClearBitMask(self.BitFramingReg, 0x80)

        # Check for errors and update status accordingly
        if i != 0:
            if (self.ReadReg(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK

                if n & irqEn & 0x01:
                    status = self.MI_NOTAGERR

                # Read response data if command is transceive
                if command == self.PCD_TRANSCEIVE:
                    n = self.ReadReg(self.FIFOLevelReg)
                    lastBits = self.ReadReg(self.ControlReg) & 0x07
                    if lastBits != 0:
                        backLen = (n - 1) * 8 + lastBits
                    else:
                        backLen = n * 8

                    if n == 0:
                        n = 1
                    if n > self.MAX_LEN:
                        n = self.MAX_LEN

                    for i in range(n):
                        backData.append(self.ReadReg(self.FIFODataReg))
            else:
                status = self.MI_ERR

        # Return response data, length, and status
        return (status, backData, backLen)

    def Request(self, reqMode):
        """
        Sends a request command to a tag or card to initiate communication.

        Args:
            reqMode (int): The request mode to send.

        Returns:
            tuple: A tuple containing:
                - status (int): The status of the command execution.
                - backBits (int): The number of bits received from the tag or card.
        """
        status = None
        backBits = None
        TagType = []

        # Set the bit framing register to 0x07
        self.WriteReg(self.BitFramingReg, 0x07)

        # Append the request mode to the TagType list
        TagType.append(reqMode)

        # Send the request to the card using the MFRC522_ToCard method
        (status, backData, backBits) = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, TagType)

        # If the status is not MI_OK or the back bits are not 0x10, set status to MI_ERR
        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR

        # Return a tuple containing the status, back bits and tag type
        return (status, backBits)

    def Anticoll(self):
        """
        Sends an anticollision command/Performs an anticollision algorithm to a tag or card to prevent multiple tags from responding.

        Returns:
            tuple: A tuple containing:
                - uid (list): The unique identifier of the tag or card.
                - size (int): The size of the UID in bits.
        """
        backData = []
        serNumCheck = 0

        serNum = []

        # Set the BitFramingReg to 0x00
        self.WriteReg(self.BitFramingReg, 0x00)

        # Append the PICC_ANTICOLL command and 0x20 to the serNum list
        serNum.append(self.PICC_ANTICOLL)
        serNum.append(0x20)

        # Call the MFRC522_ToCard method with PCD_TRANSCEIVE command and serNum data
        (status, backData, backBits) = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, serNum)

        # Check if the operation was successful
        if (status == self.MI_OK):
            i = 0
            # Check if the backData has the expected length of 5 bytes
            if len(backData) == 5:
                # Calculate the XOR checksum of the first 4 bytes of the backData
                for i in range(4):
                    serNumCheck = serNumCheck ^ backData[i]
                # Check if the calculated checksum matches the 5th byte of backData
                if serNumCheck != backData[4]:
                    # If not, set the status to MI_ERR
                    status = self.MI_ERR
            else:
                # If backData doesn't have 5 bytes, set the status to MI_ERR
                status = self.MI_ERR

        # Return the status and backData
        return (status, backData)

    def CalulateCRC(self, pIndata):
        """
        Calculates the CRC value for the given input data using the MFRC522 chip.

        Args:
            pIndata (list): A list of integers representing the input data for which to calculate the CRC.

        Returns:
            A list of two integers representing the calculated CRC value.
        """

        # Clear the CRC IRQ flag and set the FIFO level to maximum.
        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        # Write the input data to the FIFO.
        for i in range(len(pIndata)):
            self.WriteReg(self.FIFODataReg, pIndata[i])

        # Start the CRC calculation command.
        self.WriteReg(self.CommandReg, self.PCD_CALCCRC)

        # Wait for the CRC calculation to complete.
        i = 0xFF
        while True:
            n = self.ReadReg(self.DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        # Read the calculated CRC value from the chip.
        pOutData = []
        pOutData.append(self.ReadReg(self.CRCResultRegL))
        pOutData.append(self.ReadReg(self.CRCResultRegM))
        return pOutData

    def SelectTag(self, serNum):
        """
        Selects a tag or card for communication.

        Args:
            uid (list): The unique identifier of the tag or card.

        Returns:
            int: The status of the command execution (1 or 0).
        """
        # Initialize empty lists for the response data and the data buffer
        backData = []
        buf = []

        # Add the command byte and tag type to the buffer
        buf.append(self.PICC_SElECTTAG)
        buf.append(0x70)

        # Add the serial number of the tag to the buffer
        for i in range(5):
            buf.append(serNum[i])

        # Calculate the CRC values for the buffer and add them to the buffer
        pOut = self.CalulateCRC(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])

        # Send the buffer to the tag and receive the response
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)

        # Check if the response is successful and has the expected length
        if (status == self.MI_OK) and (backLen == 0x18):
            # Log the size of the response and return the first byte of the response
            self.logger.debug("Size: " + str(backData[0]))
            return backData[0]
        else:
            # Return 0 if the response is not successful or has an unexpected length
            return 0

    def Authenticate(self, authMode, BlockAddr, Sectorkey, serNum):
        """
        Authenticates a tag or card for a specific block.

        Args:
            authMode (int): The authentication mode to use.
            blockAddr (int): The address of the block to authenticate.
            sectorKey (list): The key of the sector to authenticate.
            uid (list): The unique identifier of the tag or card.

        Returns:
            The status of the authentication.
        """
        buff = []

        # First byte should be the authMode (A or B)
        buff.append(authMode)

        # Second byte is the trailerBlock (usually 7)
        buff.append(BlockAddr)

        # Now we need to append the authKey which usually is 6 bytes of 0xFF
        for i in range(len(Sectorkey)):
            buff.append(Sectorkey[i])

        # Next we append the first 4 bytes of the UID
        for i in range(4):
            buff.append(serNum[i])

        # Now we start the authentication itself
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT, buff)
        
        # Check if an error occurred
        if not (status == self.MI_OK):
            self.logger.error("AUTH ERROR!!")
        if not (self.ReadReg(self.Status2Reg) & 0x08) != 0:
            self.logger.error("AUTH ERROR(status2reg & 0x08) != 0")

        # Return the status
        return status

    def StopCrypto1(self):
        """
        Stops the authentication process.
        """
        self.ClearBitMask(self.Status2Reg, 0x08)

    def ReadTag(self, blockAddr):
        """
        Reads data from a specific block of a RFID card.

        Args:
            blockAddr (int): The block address of the RFID card to read from.

        Returns:
            If the read is successful and the received data is of the correct length, the function returns the received data as a list of 16 bytes. If the read is unsuccessful or the received data is of incorrect length, the function returns None.
        """

        # create an array containing the READ command and the block address to be read
        recvData = []
        recvData.append(self.PICC_READ)
        recvData.append(blockAddr)
        # calculate the CRC checksum for the command and block address
        pOut = self.CalulateCRC(recvData)
        # append the calculated checksum to the command and block address array
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        # send the command and block address array to the RFID card and receive response
        (status, backData, backLen) = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, recvData)
        # if response status is not OK, print error message
        if not (status == self.MI_OK):
            self.logger.error("Error while reading!")

        # if response data has length 16, print debug message and return data
        if len(backData) == 16:
            self.logger.debug("Sector " + str(blockAddr) + " " + str(backData))
            return backData
        # if response data length is not 16, return None
        else:
            return None

    def WriteTag(self, blockAddr, writeData):
        """
        Writes data to a specified block address in the RFID tag.'

        Args:
            blockAddr (int): The block address where data needs to be written
            writeData (list): A list of 16 bytes of data to be written to the block

        Returns:
            None
        """

        # The buffer to be sent to the tag for writing data
        buff = []
        buff.append(self.PICC_WRITE)
        buff.append(blockAddr)

        # Calculate the CRC checksum for the buffer
        crc = self.CalulateCRC(buff)
        buff.append(crc[0])
        buff.append(crc[1])

        # Send the buffer to the tag and receive the response
        (status, backData, backLen) = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, buff)

        # Check if the write operation was successful or not
        if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR

        self.logger.debug("%s backdata &0x0F == 0x0A %s" %
                          (backLen, backData[0] & 0x0F))

        # If the initial write operation was successful, write the actual data to the tag
        if status == self.MI_OK:
            buf = []
            for i in range(16):
                buf.append(writeData[i])
            # Calculate the CRC checksum for the data to be written
            crc = self.CalulateCRC(buf)
            buf.append(crc[0])
            buf.append(crc[1])
            # Send the data buffer to the tag and receive the response
            (status, backData, backLen) = self.MFRC522_ToCard(
                self.PCD_TRANSCEIVE, buf)
            # Check if the write operation was successful or not
            if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
                self.logger.error("Error while writing")
            # If the write operation was successful, log it
            if status == self.MI_OK:
                self.logger.debug("Data written")

    def Init(self):
        """
        Initializes the MFRC522 RFID reader by resetting it and configuring its registers.
        """

        # Reset the MFRC522
        self.Reset()

        # Set the timer mode and prescaler
        self.WriteReg(self.TModeReg, 0x8D)
        self.WriteReg(self.TPrescalerReg, 0x3E)
        self.WriteReg(self.TReloadRegL, 30)
        self.WriteReg(self.TReloadRegH, 0)

        # Enable the auto-timer for transmission and set the mode
        self.WriteReg(self.TxAutoReg, 0x40)
        self.WriteReg(self.ModeReg, 0x3D)

        # Turn on the antenna
        self.AntennaOn()
