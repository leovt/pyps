from zlib import crc32, compress
import struct
from itertools import zip_longest

PNGSIGNATURE = bytes([137,80,78,71,13,10,26,10])

def chunk(f, type, data):
    f.write(struct.pack('>L', len(data)))
    f.write(type)
    f.write(data)
    f.write(struct.pack('>L', crc32(type+data)))

def grouper(iterable, n, fillvalue=None):
    '''grouper('ABCDEFG', 3, 'x')  # --> 'ABC' 'DEF' 'Gxx' '''
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def widen_bytes(data):
    bits = []
    mask = [2**7,2**6,2**5,2**4,8,4,2,1]
    return (bool(b & m) for b in data for m in mask)

def pack_bits(bits):
    data = []
    for group in grouper(bits, 8, 0):
        byte = 0
        for bit in group:
            byte *= 2
            if bit:
                byte += 1
        data.append(byte)
    return bytes(data)

def png_mask(f, width, height, img):

    bits = widen_bytes(img)
    scanlines = [b'\0'+pack_bits(sl) for sl in grouper(bits, width, 0)][:height]

    f.write(PNGSIGNATURE)
    # png header for 1 bit palette
    chunk(f, b'IHDR', struct.pack('>LLBBBBB', width, height, 1, 3, 0, 0, 0))

    # palette with 2 entries, second is black
    chunk(f, b'PLTE', bytes([255,0,255,0,0,0]))

    # first palette entry fully transparent
    chunk(f, b'tRNS', b'\0')

    # zlib compressed imagedata
    # each scanline is prepended by 0
    img = compress(b''.join(scanlines))
    chunk(f, b'IDAT', img)
    chunk(f, b'IEND', b'')
