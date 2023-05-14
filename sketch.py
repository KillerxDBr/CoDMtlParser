import struct

# ch_asphalt01 CoD4
mtl_file = [0x9A, 0x00, 0x00, 0x00, 0xA7, 0x00, 0x00, 0x00, 0x12, 0x04, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x14, 0x10, 0x08, 0x80, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x01, 0x01, 0x00, 0x00, 0x00, 0x12, 0x88, 0x12, 0x08, 0x0D, 0x00, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00, 0x8C, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0xB8, 0x00, 0x00, 0x00, 0x0B, 0x02, 0x00, 0x00, 0xA7, 0x00, 0x00, 0x00, 0xC1, 0x00, 0x00, 0x00, 0x0B, 0x05, 0x00, 0x00, 0xCB, 0x00, 0x00, 0x00, 0xDC, 0x00, 0x00, 0x00, 0x0B, 0x08, 0x00, 0x00, 0xE8, 0x00, 0x00, 0x00, 0x0F, 0x01, 0x00, 0x00, 0xCD, 0xCC, 0x4C, 0x3F, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0xA0, 0x40, 0x00, 0x00, 0x20, 0x3F, 0x1B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x6C, 0x5F, 0x73, 0x6D, 0x5F, 0x72, 0x30, 0x63, 0x30, 0x6E, 0x30, 0x73, 0x30, 0x00, 0x63, 0x68, 0x5F, 0x61, 0x73, 0x70, 0x68, 0x61, 0x6C, 0x74, 0x30, 0x31, 0x00, 0x63, 0x68, 0x5F, 0x61, 0x73, 0x70, 0x68, 0x61, 0x6C, 0x74, 0x30, 0x31, 0x5F, 0x63, 0x6F, 0x6C, 0x00, 0x63, 0x6F, 0x6C, 0x6F, 0x72, 0x4D, 0x61, 0x70, 0x00, 0x6E, 0x6F, 0x72, 0x6D, 0x61, 0x6C, 0x4D, 0x61, 0x70, 0x00, 0x63, 0x68, 0x5F, 0x61, 0x73, 0x70, 0x68, 0x61, 0x6C, 0x74, 0x30, 0x31, 0x5F, 0x6E, 0x6D, 0x6C, 0x00, 0x73, 0x70, 0x65, 0x63, 0x75, 0x6C, 0x61, 0x72, 0x4D, 0x61, 0x70, 0x00, 0x7E, 0x63, 0x68, 0x5F, 0x61, 0x73, 0x70, 0x68, 0x61, 0x6C, 0x74, 0x30, 0x31, 0x5F, 0x73, 0x70, 0x63, 0x2D, 0x72, 0x67, 0x62, 0x26, 0x63, 0x68, 0x5F, 0x61, 0x73, 0x70, 0x68, 0x7E, 0x35, 0x62, 0x32, 0x35, 0x64, 0x65, 0x62, 0x36, 0x00, 0x65, 0x6E, 0x76, 0x4D, 0x61, 0x70, 0x50, 0x61, 0x72, 0x6D, 0x73, 0x00, 0x63, 0x6F, 0x6C, 0x6F, 0x72, 0x54, 0x69, 0x6E, 0x74, 0x00]
mtl_deagle = [
0x98, 0x00, 0x00, 0x00, 0xB7, 0x00, 0x00, 0x00, 0x12, 0x04, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x10, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0xD0, 0x00, 0x01, 0x00, 0x00, 0x00, 0x12, 0x88, 0x12, 0x08, 0x0D, 0x00, 0x00, 0x00, 
0x03, 0x00, 0x02, 0x00, 0x8C, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 
0xD6, 0x00, 0x00, 0x00, 0x0B, 0x02, 0x00, 0x00, 0xB7, 0x00, 0x00, 0x00, 0xDF, 0x00, 0x00, 0x00, 
0x01, 0x05, 0x00, 0x00, 0xE9, 0x00, 0x00, 0x00, 0xFC, 0x00, 0x00, 0x00, 0x0B, 0x08, 0x00, 0x00, 
0x08, 0x01, 0x00, 0x00, 0x2F, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x40, 0x00, 0x00, 0x80, 0x40, 
0x00, 0x00, 0xC0, 0x40, 0x00, 0x00, 0x20, 0x3F, 0x3B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3F, 
0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x6C, 0x5F, 0x73, 0x6D, 
0x5F, 0x72, 0x30, 0x63, 0x30, 0x73, 0x30, 0x00, 0x6D, 0x74, 0x6C, 0x5F, 0x77, 0x65, 0x61, 0x70, 
0x6F, 0x6E, 0x5F, 0x64, 0x65, 0x73, 0x65, 0x72, 0x74, 0x5F, 0x65, 0x61, 0x67, 0x6C, 0x65, 0x5F, 
0x73, 0x69, 0x6C, 0x76, 0x65, 0x72, 0x00, 0x77, 0x65, 0x61, 0x70, 0x6F, 0x6E, 0x5F, 0x64, 0x65, 
0x73, 0x65, 0x72, 0x74, 0x5F, 0x65, 0x61, 0x67, 0x6C, 0x65, 0x5F, 0x73, 0x69, 0x6C, 0x76, 0x65, 
0x72, 0x5F, 0x63, 0x6F, 0x6C, 0x00, 0x63, 0x6F, 0x6C, 0x6F, 0x72, 0x4D, 0x61, 0x70, 0x00, 0x6E, 
0x6F, 0x72, 0x6D, 0x61, 0x6C, 0x4D, 0x61, 0x70, 0x00, 0x24, 0x69, 0x64, 0x65, 0x6E, 0x74, 0x69, 
0x74, 0x79, 0x6E, 0x6F, 0x72, 0x6D, 0x61, 0x6C, 0x6D, 0x61, 0x70, 0x00, 0x73, 0x70, 0x65, 0x63, 
0x75, 0x6C, 0x61, 0x72, 0x4D, 0x61, 0x70, 0x00, 0x7E, 0x77, 0x65, 0x61, 0x70, 0x6F, 0x6E, 0x5F, 
0x64, 0x65, 0x73, 0x65, 0x72, 0x74, 0x5F, 0x65, 0x61, 0x67, 0x6C, 0x65, 0x5F, 0x73, 0x69, 0x6C, 
0x76, 0x65, 0x72, 0x5F, 0x73, 0x7E, 0x30, 0x65, 0x39, 0x35, 0x62, 0x30, 0x65, 0x62, 0x00, 0x65, 
0x6E, 0x76, 0x4D, 0x61, 0x70, 0x50, 0x61, 0x72, 0x6D, 0x73, 0x00, 0x63, 0x6F, 0x6C, 0x6F, 0x72, 
0x54, 0x69, 0x6E, 0x74, 0x00]

# offsets precisam de mais testes
COLOR = 0x48
color_start = int.from_bytes(mtl_file[COLOR:COLOR+4],'little')
NORMAL = 0x54
normal_start=int.from_bytes(mtl_file[NORMAL:NORMAL+4],'little')

SPEC = 0x60
spec_start = int.from_bytes(mtl_file[SPEC:SPEC+4],'little')

deagle_offsets= int.from_bytes(mtl_deagle[COLOR:COLOR+4],'little'),int.from_bytes(mtl_deagle[NORMAL:NORMAL+4],'little'),int.from_bytes(mtl_deagle[SPEC:SPEC+4],'little')

def getMtlStrings(mtl,offset):
    string = ''
    while(mtl[offset] != 0x00):
        #print(chr(mtl_file[offset]))
        string += chr(mtl[offset])
        offset+=1
    return string

colorstr = getMtlStrings(mtl_file,COLORSTART)
nmlstr = getMtlStrings(mtl_file,NORMALSTART)
specstr = getMtlStrings(mtl_file,SPECSTART)

deaglestr = getMtlStrings(mtl_deagle,deagle_offsets[0]),getMtlStrings(mtl_deagle,deagle_offsets[1]),getMtlStrings(mtl_deagle,deagle_offsets[2])
print(deaglestr, "<----")

print(f'{colorstr}, {nmlstr}, {specstr}')

teste_bytes=mtl_deagle[0x6C:0x7c] #EnvMap min max exp offsets
print(teste_bytes)

result = bytes([int(x) for x in teste_bytes])
print(result)

envMapMin, envMapMax, envMapExponent, sunint = struct.unpack('4f',result)
print(f'{envMapMin/4}, {envMapMax/4}, {envMapExponent}')
