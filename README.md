# MFRC522-python
### The mfrc522-python library is used to interact with RFID readers that use the MFRC522 chip interfaced with a Raspberry Pi.
<br>

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Connections](#connections)
- [Usage](#usage)
	- [Using `mfrc522.MFRC522`](#using-mfrc522-class)
	- [Using `mfrc522.SimpleMFRC522`](#using-simplemfrc522-class)
	- [Using `mfrc522.BasicMFRC522`](#using-basicmfrc522-class)
- [Example Code](#example-code)
	- [Using `mfrc522.MFRC522`](#using-mfrc522-class-1)
	- [Using `mfrc522.SimpleMFRC522`](#using-simplemfrc522-class-1)
	- [Using `mfrc522.BasicMFRC522`](#using-basicmfrc522-class-1)
- [Contributions](#contributions)
- [License](#license)

## Introduction
### **MFRC522**
The MFRC522 is a popular RFID module that supports contactless communication using the 13.56 MHz frequency. It can read and write data to RFID cards or tags, making it ideal for projects that require identification or access control. This repository provides a library and example code to interact with the MFRC522 module using various microcontroller platforms.

### **Sectors and Blocks**
Sectors and Blocks refer to the organization and structure of memory on an RFID tag or card.
<br>
The memory of card is divided into **16 sectors** (for classic MIFARE 1k). Each sector contains **4 blocks** and each block can hold upto **16 bytes of data**.
<br>
So a classic MIFARE 1k has **16 sectors, 64 blocks (16  sectors x 4 blocks)  and can hold upto 1024 bytes (64 blocks x 16 bytes)**  in total.
<br>
Not Every blocks are writeable, the first block of the first sector and the last block of every sectors are not writeable.
The first block of **first sector typically holds the manufaturer's details** *(like **manufacturer's identification number (MID) and the application identifier (AID)**. The MID is a unique number that identifies the manufacturer of the card. The AID is a unique number that identifies the application that is stored on the card.)*. **The last block of every sector is called a trailer block**, the trailer block contains information about the sector, such as the **sector number, the number of blocks in the sector, and the checksum**. The checksum is used to verify the integrity of the data in the sector. **If you ever write to a trailer block then the entire sector will be unwritable.**

| Sectors | Block Number   |
|---------|----------------|
| 0       | 0, 1, 2, 3     |
| 1       | 4, 5, 6, 7     |
| 2       | 8, 9, 10, 11   |
| 3       | 12, 13, 14, 15 |
| 4       | 16, 17, 18, 19 |
| 5       | 20, 21, 22, 23 |
| 6       | 24, 25, 26, 27 |
| 7       | 28, 29, 30, 31 |
| 8       | 32, 33, 34, 35 |
| 9       | 36, 37, 38, 39 |
| 10      | 40, 41, 42, 43 |
| 11      | 44, 45, 46, 47 |
| 12      | 48, 49, 50, 51 |
| 13      | 52, 53, 54, 55 |
| 14      | 56, 57, 58, 59 |
| 15      | 60, 61, 62, 63 |

Manfacturer's details is stored in block number 0  and 
Trailer blocks are 3, 7, 11, etc,.
<br>
**( Tips: It's better to not store any data in the first sector. Start from the first sector )**
<br>
**Note: Different cards have diiferent number of sectors and blocks. For example, Classic MIFARE 4k has 40 Sectors. It's better to check the datasheet for the RFID tag/card you use before writing data to it.**

## Installation
### 1. From PyPI (Stable)
```
pip install mfrc522-python 
```
### 2. From Github ( Beta/dev version)
```
pip install git+https://github.com/1AdityaX/mfrc522-python
```
## Connections
| RF522 Module | Raspberry Pi          |
|--------------|---------------------- |
| SDA          | Pin 24 / GPIO8 (CE0)  |
| SCK          | Pin 23 / GPIO11 (SCKL)|
| MOSI         | Pin 19 / GPIO10 (MOSI)|
| MISO         | Pin 21 / GPIO9 (MISO) |
| IRQ          | –                     |
| GND          | GND                   |
| RST          | Pin 22 / GPIO25       |
| 3.3V         | 3.3V                  |

## Usage
### Using `MFRC522` class
1. Import and create an instance of class `MFRC522` from `mfrc522` module.
```py
from mfrc522 import MFRC522

reader = MFRC522() 
```
2. Request communication with a PICC *(Proximity Integrated Circuit Card A.K.A rfid card)* and check if the communication is established.
```py
status =  None
while status != reader.MI_OK:
	(status, TagType) = reader.Request(reader.PICC_REQIDL)
	if status == reader.MI_OK:
		print("Connection Success!")
```
3.  Perform an Anti-collision Algorithm *(Picks one rfid card if multiple cards are placed )* and return the UID.
```py
(status, uid) = reader.Anticoll()
if status == reader.MI_OK:
	print(uid)
```
4.  Select the tag to Authenticate and perform funtions like reading or writing data to the card.
```py
reader.SelectTag(uid)
``` 
5. Authenticate a particular sector with a key to read or write data to it.
```py
trailer_block = 11
#This is the default key for MIFARE Cards
key = [0xFF, 0xFF, 0xFF , 0xFF, 0xFF, 0xFF]
status = reader.Authenticate(
        reader.PICC_AUTHENT1A, trailer_block , key, uid)
```
6. Now read or write to the block numbers in the sector that you have authenticated.

**To read**
```py
block_nums = [8, 9, 10]
data = []
for block_num in block_nums:
	block_data = reader.ReadTag(block_num)
	if block_data:
		data += block_data
if data:
	print(''.join(chr(i) for i in data))
```
**To write**
```py
block_nums = [8, 9, 10]
text = "Hello, World"
data = bytearray()
data.extend(bytearray(text.ljust(  len(block_addrs)  *  16).encode('ascii')))
i = 0
for block_num in block_addrs:
	reader.WriteTag(block_num, data[(i*16):(i+1)*16]) 
	i +=  1
```
7. Once you business with the RFID card or Tag is over. Always Stop the Authenciation/communiction with the card.
**Note: If you miss out this step, you won't be able to use a different card.**
```py
reader.StopAuth()
```

### Using `SimpleMFRC522` class
1. Import and create an instance of class `SimpleMFRC522` from `mfrc522` module
```py
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
```
2. Use `read()`  to read and `write()` to write
**To read** 
```py
id, text = reader.read()
print(f"ID: {id}")
print(f"Text: {text}")
```
**To write**
```py
text = "hello_world"
id, text_written = reader.write(text)
print(f"ID: {id}")
print(f"Text Written: {text_written}")
```
### `mfrc522.SimpleMFRC522()` Methods
#### `__init__()`

Initializes a `SimpleMFRC522` instance. It sets up the MFRC522 module, defines the default authentication key, sets the trailer block number to 11, and initializes the BasicMFRC522 module.

#### `read()`

Reads data from the RFID tag.

-   Returns: A tuple containing the tag ID (as an integer) and the data read (as a string).

#### `read_id()`

Reads the tag ID from the RFID tag.

-   Returns: The tag ID as an integer.

#### `write(text)`

Writes the given text to an RFID tag.

-   Args:
    -   `text` (str): A string to be written to the RFID tag.
-   Returns: A tuple containing the ID of the tag and the text that was written to the tag.
    
### Using `BasicMFRC522` class
1. Import and create an instance of the class `BasicMFRC522` from `mfrc522` module
```py
from mfrc522 import BasicMFRC522

reader = BasicMFRC522()
```
2. Use any methods.

### `mfrc522.BasicMFRC522` Methods


####  `__init__(KEY=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])`
Initializes a `BasicMFRC522` instance.
-   Args:
    -   `KEY` (list): The authentication key used for reading and writing data. The default key is `[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]`.



#### `read_sector(trailer_block=11)`
Reads data from a sector of the RFID tag.
-   Args:
    -   `trailer_block` (int): The block number of the sector trailer.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the data read (as a string).

#### `read_sectors(trailer_blocks=[11])`
Reds data from multiple sectors of the RFID tag.
-   Args:
    -   `trailer_blocks` (list): The list of block numbers of the sector trailers.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the concatenated data read from all sectors (as a string).

#### `read_id()`
 Reads the tag ID from the RFID tag.
-   Returns:
    -   `int`: The tag ID as an integer.

#### `read_id_no_block()`
Attempts to read the tag ID from the RFID tag without blocking.
-   Returns:
    -   `int`: The tag ID as an integer, or `None` if the operation fails.

#### `read_no_block(trailer_block)`
Attempts to read data from the RFID tag without blocking.
-   Args:
    -   `trailer_block` (int): The block number of the sector trailer.
    -   `block_addr` (tuple): The block numbers of the data blocks to read.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the data read (as a string), or `(None, None)` if the operation fails.

#### `write_sector(text, trailer_block=11)`
Writes data to a sector of the RFID tag.
-   Args:
    -   `text` (str): The data to write.
    -   `trailer_block` (int): The block number of the sector trailer.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the data written (as a string).

#### `write_sectors(text, trailer_blocks=[11])`
 Writes data to multiple sectors of the RFID tag.
-   Args:
    -   `text` (str): The data to write.
    -   `trailer_blocks` (list): The list of block numbers of the sector trailers.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the concatenated data written to all sectors (as a string).

#### `write_no_block(text, trailer_block)`
Attempts to write data to the RFID tag without blocking.
-   Args:
    -   `text` (str): The data to write.
    -   `trailer_block` (int): The block number of the sector trailer.
    -   `block_addr` (tuple): The block numbers.
    
#### `clear_sector(trailer_block=11)`
Clears a sector of the RFID tag by writing empty data to all blocks.
-   Args:
    -   `trailer_block` (int): The block number of the sector trailer.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the cleared data (as an empty string).

#### `clear_sectors(trailer_blocks=[11])`
Clears multiple sectors of the RFID tag by writing empty data to all blocks.
-   Args:
    -   `trailer_blocks` (list): The list of block numbers of the sector trailers.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the concatenated cleared data (as an empty string).

#### `clear_no_block(trailer_block)`
Attempts to clear a sector of the RFID tag without blocking.
-   Args:
    -   `trailer_block` (int): The block number of the sector trailer.
    -   `block_addr` (tuple): The block numbers of the data blocks to clear.
-   Returns:
    -   `tuple`: A tuple containing the tag ID (as an integer) and the cleared data (as an empty string), or `(None, None)` if the operation fails.

**Note: Clearing a sector will permanently erase the data stored in the blocks of that sector. Use with caution as this operation cannot be undone.**

## Example Code
### Using `MFRC522` class 
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
    id = uid
    reader.SelectTag(uid)
    status = reader.Authenticate(
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
key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
block_addrs = [8,9,10]
id, text = read(trailer_block, key, block_addrs)
while not id:
    id, text = read(trailer_block, key, block_addrs)

print(id)
print(text)
```

**write.py**

To write a particular sector.
```py
from mfrc522 import MFRC522

reader = MFRC522()

def write(trailer_block, key, block_addrs, text):
    (status, TagType) = reader.Request(reader.PICC_REQIDL)
    if status != reader.MI_OK:
        return None, None
    (status, uid) = reader.Anticoll()
    if status != reader.MI_OK:
        return None, None
    reader.SelectTag(uid)
    status = reader.Authenticate(
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
    return uid, text[0:(len(block_addrs) * 16)]

trailer_block = 11
block_addrs = [8, 9, 10]
key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
text = "some random text"
uid, text_in = write(trailer_block, key, block_addrs, text)
while not uid:
    uid, text_in = write(trailer_block, key, block_addrs, text)
print(uid)
print(text_in)
```
### Using `SimpleMFRC522` class
**read.py**
```py
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

id, text = reader.read()
print(f"ID: {id}")
print(f"Text: {text}")
```
**write.py**
```py
from mfrc522 import SimpleMFRC522

writer = SimpleMFRC522()
text = "Hello, world"

id, text_written = writer.write(text)
print(f"ID: {id}")  
print(f"Text Written: {text_written}")
```
### Using `BasicMFRC522` class
**read_sector.py**
To read a particular sector
```py
from mfrc522 import BasicMFRC522

reader = BasicMFRC522()
sector = 15
id, text = reader.read_sector(sector)
print(f"ID: {id}")
print(f"Text: {text}")
```
**read_sectors.py**
To read multiple sectors
```py
from mfrc522 import BasicMFRC522

reader = BasicMFRC522()
sectors = [11, 15]
id, text = reader.read_sectors(sectors)
print(f"ID: {id}")
print(f"Text: {text}")
```
**write_sector.py**
To write a particular sector
```py
from mfrc522 import BasicMFRC522

writer = BasicMFRC522()

sector =  15
text =  "Example to use write_sector method"
id, text_written = writer.write_sector(text, sector)
print(f"ID: {id}")
print(f"Text Written: {text_written}")
```
**write_sectors.py**
To write multiple sectors
```py
from mfrc522 import BasicMFRC522

writer = BasicMFRC522()

sector = [11, 15]
text =  "Example to use write_sector method"

id, text_written = writer.write_sectors(text, sector)
print(f"ID: {id}")
print(f"Text Written: {text_written}")
```
**clear_sector.py**
To clear data written in a sector
```py
from mfrc522 import BasicMFRC522

writer = BasicMFRC522()
sector = 11

id = writer.clear_sector(sector)
print("Cleared")
```

**clear_sectors.py**
To clear data written in multiple sectors
```py
from mfrc522 import BasicMFRC522

writer = BasicMFRC522()
sectors  = [11, 15]

id = writer.clear_sectors(sectors)
print("Cleared")
```
## Contributions
Contributions to the `mfrc522-python` library are welcome. To contribute, follow these steps:

1.  Fork the repository on GitHub.
2.  Create a new branch for your changes.
3.  Make your changes and commit them.
4.  Push your changes to your forked repository.
5.  Submit a pull request to the main repository.

That's it! By submitting a pull request, you can contribute your changes to the `mfrc522-python` library.
 Provide a clear description of your changes in the pull request.
If you have any questions or need further assistance, feel free to open an issue.

## License
This project is licensed under the GNU General Public License (GPL) version 3.0. You can find the full text of the license in the [LICENSE](LICENSE) file.