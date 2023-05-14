import struct
import argparse

# Constants
COLOR = 0x48
NORMAL = 0x54
SPEC = 0x60
ENVPARAM = 0x6C

def getMtlStrings(mtl,offset):
    string = ''
    while(mtl[offset] != 0x00):
        #print(chr(mtl_file[offset]))
        string += chr(mtl[offset])
        offset+=1
    return string

class MTL:
    def __init__(self,mtl_file):
        self.mtl_name = getMtlStrings
        self.color = getMtlStrings(mtl_file,COLOR)
        self.normal = getMtlStrings(mtl_file,NORMAL)
        self.spec = getMtlStrings(mtl_file,SPEC)

        envMapMin, envMapMax, self.envMapExponent, sunint = struct.unpack('4f',bytes([int(x) for x in mtl_file[ENVPARAM:ENVPARAM+16]]))
        
        self.envMapMin, self.envMapMax = envMapMin/4, envMapMax/4

    def __str__(self):
        return f'Material: {self.mtl_name}\nColor Map: {self.color}\nNormal Map: {self.normal}\nRaw Specular Map: {self.spec}'

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',type=str,help='input material file')
arg = parser.parse_args()
mtl_file = parser.input

with open(mtl_file,'rb') as f:
    mtl = f.read()
mtl_classe = MTL(mtl)
