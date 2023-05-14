import os
import struct
import argparse
import json

# Constants
COLOR    = 0x48
NORMAL   = 0x54
SPEC     = 0x60
ENVPARAM = 0x6C

TECHSET_FLAGS = {
    'COLOR'     : "c0",
    'NORMAL'    : "n0",
    'SPEC'      : "s0",
    'REPLACE'   : "r0",
    'ALPHATEST' : "t0",
    'BLEND'     : "b0"}

# Change it here if you want :)
# i.e. _spc and _cos
SPEC_SUFFIX  = '_s'
GLOSS_SUFFIX = '_g'

class MTL:   
    def __init__(self,mtl_file):

        # Based on CoD 4 Assets

        # Offsets
        mtl_name_offset = struct.unpack('i', mtl_file[0:4])[0]
        techset_offset  = struct.unpack('i', mtl_file[0x34:0x34+4])[0]
        color_offset    = struct.unpack('i', mtl_file[COLOR:COLOR+4])[0]
        normal_offset   = struct.unpack('i', mtl_file[NORMAL:NORMAL+4])[0]
        spec_offser     = struct.unpack('i', mtl_file[SPEC:SPEC+4])[0]

        # Texture Names
        self.mtl_name    = self.getMtlString(mtl_file, mtl_name_offset)
        self.techset     = self.getMtlString(mtl_file, techset_offset)
        self.techsetArgs = self.getTechsetArgs(self.techset)
        self.color       = self.getMtlString(mtl_file, color_offset)
        self.normal      = self.getMtlString(mtl_file, normal_offset)
        self.raw_spec    = self.getMtlString(mtl_file, spec_offser)

        # Names for conversion
        self.spec       = '_'.join(self.raw_spec.split('&')[0].strip('~').split('_')[:-1]) + SPEC_SUFFIX
        self.gloss      = self.spec[:-2] + GLOSS_SUFFIX

        # sunint: UNUSED, value calculated in asset manager compile
        # from file: Cod4Root/deffiles/materials/mtl_phong.template
        # #define SUN_INTENSITY 2.5
		# "envMapParms" = float4( @envMapMin@ * 4, @envMapMax@ * 4, @envMapExponent@, SUN_INTENSITY * 0.25 );

        envMapMin, envMapMax, self.envMapExponent, sunint = struct.unpack('4f',
                                                bytes([int(x) for x in mtl_file[ENVPARAM:ENVPARAM+16]]))
        
        self.envMapMin, self.envMapMax = envMapMin/4, envMapMax/4

        # todo
        # Check if WaW envMapParms is different

    def __str__(self):
        return (f'\n------------------\n'
                f'Material: {self.mtl_name}\n'
                f'Techset: {self.techset}\n'
                f'Color Map: {self.color}\n'
                f'Normal Map: {self.normal}\n'
                f'Raw Specular Map: {self.raw_spec}\n'
                f'Specular Map: {self.spec}\n'
                f'Glossiness Map: {self.gloss}\n'
                f'EnvMapArgs: Min: {self.envMapMin} Max: {self.envMapMax} Exp: {self.envMapExponent}')
    
    def getMtlString(self,mtl,offset):
        # print(offset)
        string = ''
        while(mtl[offset] != 0x00):
            #print(chr(mtl_file[offset]))
            string += chr(mtl[offset])
            offset+=1
        return string
    
    def getTechsetArgs(self,ts):
        pass
    

# parser = argparse.ArgumentParser()
# parser.add_argument('-i','--input',type=str,help='input material file')
# args = parser.parse_args()
# mtl_file = args.input


# getting material files from 'materials' directory
paths = os.listdir( 'materials' )

mtl_classe = []
for mtlpath in paths:
    mtl = ''
    with open(f'materials/{mtlpath}','rb') as f:
        mtl = f.read()
        mtl_classe.append(MTL(mtl))

for mtl in mtl_classe:
    print(mtl.__str__())

print()