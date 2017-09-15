#!/usr/bin/python3
#-*- coding: utf-8 -*-

import struct

class DataGenerator:

    def __init__(self, fh, offset=None, size=None, decompressed_size=None, verbose=False):
        self.fh = fh
        self.offset = offset
        self.size = size
        self.decompressed_size = decompressed_size
        self.decompressed = False
        if offset:
            if verbose:
                print("Going to offset %d" % offset)
            self.goto(offset)
        if self.decompressed_size:
            self.decompress()

    def decompress(self, verbose=False):
        # Read header and sanity check
        compsize = self.get_dword()
        if compsize != self.size:
            raise ValueError("Compressed size in header (%d) does not match expected value from Index (%d)" % (compsize, self.size))
        comp_id = self.get_word()
        if comp_id != 0xfb10:
            raise ValueError("Invalid expression ID: expected 0xfb10, got %d" % comp_id)
        decompsize = self.get_uint24()
        if decompsize != self.decompressed_size:
            print("Decompressed size in header (%d) does not match expected value from directory (%d)" % (decompsize, self.decompressed_size))
            #raise ValueError("Decompressed size in header (%d) does not match expected value from directory (%d)" % (decompsize, self.decompressed_size))
        
        # Initialise a byte array and a write pointer
        if verbose:
            print("Creating buffer for decompressed data, size %d" % decompsize)
        self.decomp_buffer = bytearray(decompsize)
        wptr = 0
        
        # Now iterate through the compressed data until the buffer is full
        while wptr < decompsize:
            byte0 = self.get_byte()
            if byte0 < 0x80:
                byte1 = self.get_byte()
                num_plain_text = (byte0 & 0x03)
                num_to_copy = ((byte0 & 0x1c) >> 2) + 3
                copy_offset = ((byte0 & 0x60) << 3) + byte1 + 1
            elif byte0 < 0xc0:
                byte1 = self.get_byte()
                byte2 = self.get_byte()
                num_plain_text = ((byte1 & 0xc0) >> 6)
                num_to_copy = (byte0 & 0x3f) + 4
                copy_offset = ((byte1 & 0x3f) << 8) + byte2 + 1
            elif byte0 < 0xe0:
                byte1 = self.get_byte()
                byte2 = self.get_byte()
                byte3 = self.get_byte()
                num_plain_text = (byte0 & 0x03)
                num_to_copy = ((byte0 & 0x0C) << 6) + byte3 + 5
                copy_offset = ((byte0 & 0x10) << 12) + (byte1 << 8) + byte2 + 1
            elif byte0 < 0xfd:
                num_plain_text = ((byte0 & 0x1F) << 2) + 4
                num_to_copy = 0
                copy_offset = None
            else:
                num_plain_text = (byte0 & 0x03)
                num_to_copy = 0
                copy_offset = None
        
            if verbose:
                print("Num plain text = %d" % num_plain_text, end='')
                if num_to_copy > 0:
                    print(", num to copy = %d, copy offset = %d" % (num_to_copy, copy_offset))
                else:
                    print()
    
            # Copy plain text from input stream
            self.decomp_buffer[wptr:(wptr + num_plain_text - 1)] = self.get_bytes(num_plain_text)
            wptr += num_plain_text
            # Copy from earlier in buffer. Need to do this with a loop because the input and output could overlap
            if num_to_copy > 0:
                rptr = wptr - copy_offset
                for _ in range(0, num_to_copy):
                    if verbose:
                        print("wptr = %d, rptr = %d" % (wptr, rptr))
                    self.decomp_buffer[wptr] = self.decomp_buffer[rptr]
                    wptr += 1
                    rptr += 1
            if verbose:
                print(repr(self.decomp_buffer))
            
        # Sanity check!
        if wptr != decompsize:
            raise ValueError("Decompressed larger than expected!")
        
        # Finally set a flag to say we've decompressed and a pointer to the start of the byte array
        self.decompressed = True
        self.decomp_ptr = 0

    def read(self, n):
        if self.decompressed:
            res = self.decomp_buffer[self.decomp_ptr:(self.decomp_ptr + n)]
            self.decomp_ptr += n
        else:
            res = self.fh.read(n)
        return res
        
    def get_byte(self, verbose=False):
        res = struct.unpack('B', self.read(1))[0]
        if verbose:
            print(format(res, '#04x'))
        return res
    
    def get_bytes(self, num):
        return struct.unpack('%dB' % num, self.read(num))
    
    def get_string(self, num):
        return struct.unpack('%ds' % num, self.read(num))[0].decode('ascii')

    def get_word(self):
        return struct.unpack('H', self.read(2))[0]

    def get_words(self, num):
        return struct.unpack('%dH' % num, self.read(2*num))
    
    def get_uint24(self):
        data = struct.unpack('3B', self.read(3))
        return data[0]*256*256 + data[1]*256 + data[2]
    
    def get_dword(self):
        return struct.unpack('I', self.read(4))[0]
        
    def get_dwords(self, num):
        return struct.unpack('%dI' % num, self.read(4*num))

    def get_float(self):
        return struct.unpack('f', self.read(4))[0]
        
    def get_floats(self, num):
        return struct.unpack('%df' % num, self.read(4*num))

    def goto(self, offset):
        if self.decompressed:
            self.decomp_ptr = offset
        else:
            self.fh.seek(offset)

    def tell(self):
        if self.decompressed:
            res = self.decomp_ptr
        else:
            res = self.fh.tell()
        return res

    def remaining(self):
        if self.decompressed:
            res = self.decompressed_size - self.decomp_ptr
        else:
            res = self.fh.tell() - self.offset
        return res