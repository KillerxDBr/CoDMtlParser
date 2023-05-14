import os
import random
import struct
import argparse

# Constants
COLOR = 0x48
NORMAL = 0x54
SPEC = 0x60
ENVPARAM = 0x6C

def getMtlString(mtl,offset):
    # print(offset)
    string = ''
    while(mtl[offset] != 0x00):
        #print(chr(mtl_file[offset]))
        string += chr(mtl[offset])
        offset+=1
    return string

class MTL:
    def __init__(self,mtl_file):
        #Offsets
        mtl_name_offset = struct.unpack('i',mtl_file[0:4])[0]
        shader_offset = struct.unpack('i',mtl_file[0x34:0x34+4])[0]
        color_offset = struct.unpack('i',mtl_file[COLOR:COLOR+4])[0]
        normal_offset = struct.unpack('i',mtl_file[NORMAL:NORMAL+4])[0]
        spec_offser = struct.unpack('i',mtl_file[SPEC:SPEC+4])[0]

        # print(f'\n\nOffsets\nmtl_name: {mtl_name_offset}\nshader: {shader_offset}\nColor: {color_offset}\nSpec: {spec_offser}')

        self.mtl_name = getMtlString(mtl_file,mtl_name_offset)
        self.shader = getMtlString(mtl_file,shader_offset)
        self.color = getMtlString(mtl_file,color_offset)
        self.normal = getMtlString(mtl_file,normal_offset)
        self.spec = getMtlString(mtl_file,spec_offser)

        envMapMin, envMapMax, self.envMapExponent, sunint = struct.unpack('4f',bytes([int(x) for x in mtl_file[ENVPARAM:ENVPARAM+16]]))
        
        self.envMapMin, self.envMapMax = envMapMin/4, envMapMax/4

    def __str__(self):
        return (f'\n------------------\n'
                f'Material: {self.mtl_name}\n'
                f'Shader type: {self.shader}\n'
                f'Color Map: {self.color}\n'
                f'Normal Map: {self.normal}\n'
                f'Raw Specular Map: {self.spec}\n'
                f'EnvMapArgs: Min: {self.envMapMin} Max: {self.envMapMax} Exp: {self.envMapExponent}')

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',type=str,help='input material file')
args = parser.parse_args()
mtl_file = args.input


# print(mtl_file)

# if mtl_file is None:
paths = os.listdir( 'materials' )
    # mtlname = random.choice( os.listdir( 'materials/' ))
    # mtl_file = f'materials/{mtlname}'
    # print(mtl_file)
    # print(f'os.listdir {paths} <-------------')

with open(f'materials/{paths[0]}','rb') as f:
    mtl1 = f.read()
with open(f'materials/{paths[1]}','rb') as f:
    mtl2 = f.read()
with open(f'materials/{paths[2]}','rb') as f:
    mtl3 = f.read()
    # print(mtl)
mtl_classe = []
mtl_classe.append(MTL(mtl1))
mtl_classe.append(MTL(mtl2))
mtl_classe.append(MTL(mtl3))

print(mtl3[264:274])

for classe in mtl_classe:
    print(classe.__str__())
# print(hex(mtl[COLOR]))

