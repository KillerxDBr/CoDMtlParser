import os
import struct
import argparse
import sqlite3

# Constants
COLOR     = 0x48
NORMAL    = 0x54
SPEC      = 0x60
ENVPARAM  = 0x6C
COLORTINT = 0x7C
TECHSET   = 0x34
TECHSET_FLAGS = {
    'COLOR'     : "c0",
    'NORMAL'    : "n0",
    'SPEC'      : "s0",
    'REPLACE'   : "r0",
    'ALPHATEST' : "t0",
    'BLEND'     : "b0"}

# Change it here if you want :)
# i.e. _spc and _cos
SURFACETYPE  = '<error>'
SPEC_SUFFIX  = '_s'
GLOSS_SUFFIX = '_g'

DATABASE = 'mtl.db'

createTable = not os.path.exists(DATABASE)

db = sqlite3.connect(DATABASE)
cur = db.cursor()
res = cur.execute("SELECT name FROM sqlite_master")
if res.fetchone() is None:
    createTable = True
if createTable:
    cur.execute('create table specgloss(raw_spec,spec,gloss,sg_material)')
    cur.execute('create table normals(normal,nml_material)')

class MTL:
    def __init__(self,mtl_file):
        self.duplicate, self.duplicateNormal = False, False
        # Based on CoD 4 Assets
        # CoD4 Mtls are compatible with WaW
        # But WaW store envMapParms differently

        # Offsets
        mtlName_offset  = struct.unpack('i', mtl_file[0:4])[0]
        techset_offset  = struct.unpack('i', mtl_file[TECHSET:TECHSET+4])[0]
        color_offset    = struct.unpack('i', mtl_file[COLOR:COLOR+4])[0]
        normal_offset   = struct.unpack('i', mtl_file[NORMAL:NORMAL+4])[0]
        spec_offset     = struct.unpack('i', mtl_file[SPEC:SPEC+4])[0]

        # Texture Names
        self.mtlName     = self.getMtlString(mtl_file, mtlName_offset)
        self.techset     = self.getMtlString(mtl_file, techset_offset)
        self.techsetArgs = self.getTechsetArgs()
        self.color       = self.getMtlString(mtl_file, color_offset)
        self.normal      = self.getMtlString(mtl_file, normal_offset)
        self.raw_spec    = self.getMtlString(mtl_file, spec_offset)

        # Names for conversion
        spec       = '_'.join(self.raw_spec.split('&')[0].strip('~').split('_')[:-1]) + SPEC_SUFFIX
        gloss      = spec[:-2] + GLOSS_SUFFIX

        if self.normal.lower() != "$identityNormalMap".lower():
            rst = cur.execute('select normal from normals')
            for n in rst.fetchall():
                self.duplicateNormal = self.normal in n
                if self.duplicateNormal:
                    break
            if self.duplicateNormal:
                rst = cur.execute('select nml_material from normals where normal=?', [self.normal])
                self.normalDuplicate = rst.fetchone()
            else:                                    # create table normals(normal, nml_material)
                rst = cur.execute('insert into normals values(?, ?)', [self.normal, self.mtlName])


        
        rst = cur.execute('select raw_spec from specgloss')
        for t in rst.fetchall():
            self.duplicate = self.raw_spec in t
            if self.duplicate:
                break;

        if self.duplicate:
            rst = cur.execute('select sg_material, spec, gloss from specgloss where raw_spec=?', [self.raw_spec])
            self.duplicatePath, self.spec, self.gloss = rst.fetchone()
        else:
            self.spec  = spec
            self.gloss = gloss
                                                 # create table specgloss(raw_spec,      spec,      gloss,  sg_material)
            cur.execute('insert into specgloss values(?, ?, ?, ?)', (self.raw_spec, self.spec, self.gloss, self.mtlName)) 
            db.commit()

        # sunint: UNUSED, value calculated in asset manager compile
        # from file: Cod4Root/deffiles/materials/mtl_phong.template
        # #define SUN_INTENSITY 2.5
		# "envMapParms" = float4( @envMapMin@ * 4, @envMapMax@ * 4, @envMapExponent@, SUN_INTENSITY * 0.25 );

        envMapMin, envMapMax, self.envMapExponent, sunint = struct.unpack('4f',
                                                bytes([int(x) for x in mtl_file[ENVPARAM:ENVPARAM+16]]))
        
        self.envMapMin, self.envMapMax = envMapMin/4, envMapMax/4
        self.colorTint = struct.unpack('4f', bytes([int(x) for x in mtl_file[COLORTINT:COLORTINT+16]]))

        # todo
        # Check if WaW envMapParms is different
    
    def __str__(self):
        return (f'\n------------------\n'
                f'Material: {self.mtlName}\n'
                f'Techset: {self.techset}\n'
                f'Techset Args: {[flag for flag, value in self.techsetArgs.items() if value]}\n'
                f'Color Map: {self.color}\n'
                f'Color Tint(RGB Float): R: {self.colorTint[0]:.1f} G: {self.colorTint[1]:.1f} B: {self.colorTint[2]:.1f} A: {self.colorTint[3]:.1f}\n'
                f'Color Tint(RGB Int): R: {self.colorTint[0]*255:.0f} G: {self.colorTint[1]*255:.0f} B: {self.colorTint[2]*255:.0f} A: {self.colorTint[3]*255:.0f}\n'
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
    
    def getTechsetArgs(self):
        tsarg = {}
        for flag, value in TECHSET_FLAGS.items():
            tsarg.update({flag:(value in self.techset)})
        return tsarg
    
    def toGDT(self):
        path = f'texture_assets\\\\CoD4\\\\{self.mtlName}\\\\'
        string = (
            f'\t"{self.mtlName}" ( "material.gdf" )\n'
            f'\t{{\n'
            f'\t\t"template" "material.template"\n'
		    f'\t\t"materialType" "model phong"\n'
            f'\t\t"surfaceType" "{SURFACETYPE}"\n'
            f'\t\t"envMapMin" "{self.envMapMin}"\n'
		    f'\t\t"envMapMax" "{self.envMapMax}"\n'
		    f'\t\t"envMapExponent" "{self.envMapExponent}"\n'
            f'\t\t"colorMap" "{path}{self.color}.tga"\n'
            f'\t\t"colorTint" "{self.colorTint[0]:.6f} {self.colorTint[1]:.6f} {self.colorTint[2]:.6f} {self.colorTint[3]:.6f}"\n'
        )
        if self.techsetArgs['NORMAL']:
            if self.normal.lower() == "$identityNormalMap".lower():
                string += f'\t\t"normalMap" "$identityNormalMap"\n'
            else:
                if self.normalDuplicate:
                    string += f'\t\t"normalMap" "texture_assets\\\\CoD4\\\\{self.normalDuplicate}\\\\{self.normal}.tga"\n'
                else:
                    string += f'\t\t"normalMap" "{path}{self.normal}.tga"\n'
        if self.techsetArgs['SPEC']:
            if self.duplicate:
                string +=(
                    f'\t\t"specColorMap" "texture_assets\\\\CoD4\\\\{self.duplicatePath}\\\\{self.spec}.tga"\n'
		            f'\t\t"cosinePowerMap" "texture_assets\\\\CoD4\\\\{self.duplicatePath}\\\\{self.gloss}.tga"\n')
            else:
                string +=(
                    f'\t\t"specColorMap" "{path}{self.spec}.tga"\n'
		            f'\t\t"cosinePowerMap" "{path}{self.gloss}.tga"\n')
        if self.techsetArgs['REPLACE']:
            string += (f'\t\t"blendFunc" "Replace*"\n'
                       f'\t\t"depthWrite" "<auto>*"\n')
        elif self.techsetArgs['BLEND']:
            string += (f'\t\t"blendFunc" "Blend"\n'
                       f'\t\t"depthWrite" "On"\n')
        if self.techsetArgs['ALPHATEST']:
            string += f'\t\t"alphaTest" "GE128"\n'
        else:
            string += f'\t\t"alphaTest" "Always*"\n'
        string += f'\t}}\n'
        return string

def main():

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i','--input',type=str,help='input material file')
    # args = parser.parse_args()
    # mtl_file = args.input

    # getting material files from 'materials' directory

    def bConvert(mtl, btype='i', step = 4):
        # print(f'\n--------------------\n')
        rst = []
        techset_offset  = struct.unpack('i', mtl[TECHSET:TECHSET+4])[0]
        for i in range(0,techset_offset,step):
            rst.append(struct.unpack(btype, mtl[i:i+4])[0])
        return rst
        # print(f'\n--------------------\n')

    paths = os.listdir( 'materials' )
    mtl_classe = []
    for mtlpath in paths:
        mtl = ''
        with open(f'materials/{mtlpath}','rb') as f:
            mtl = f.read()
            f.close()
        mtl_classe.append(MTL(mtl))
        # print(f'\n{mtl_classe[-1].mtlName}\n'
        #       f'Float\n{bConvert(mtl,"f")}\n'
        #       f'{"-"*50}'
        #       f'\nInt\n{bConvert(mtl,"i")}')

    # for mtl in mtl_classe:
    #     print(mtl.toGDT())

    # print(mtl_classe[0].__str__())

    db.close()

if __name__ == '__main__':
    main()