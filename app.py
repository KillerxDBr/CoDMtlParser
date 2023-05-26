import os
import json
import struct

# TKinter
from tkinter import StringVar, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# SQLAlchemy
from sqlalchemy import asc, desc
from Models.base import Model
from Models.materials import Material, Normal, SpecGloss
from newmain import session, BASE_DIR, DB_NAME, engine

# Misc
from kxdconstants import * # Check this file to edit surface type and spec gloss suffix

if not os.path.exists(f'{BASE_DIR}\\{DB_NAME}'):
    Model.metadata.create_all(engine)

    identity      = Normal()
    identity.Name = '$identitynormalmap'
    identity.Path = 'Default Image'

    session.add(identity)
    session.commit()

class MaterialMaker:
    @staticmethod
    def getMtlString(mtl, offset):
        # print(offset)
        string = ''
        while (mtl[offset] != 0x00):
            # print(chr(mtl_file[offset]))
            string += chr(mtl[offset])
            offset += 1
        return string

    @staticmethod
    def getTechsetArgs(techset: str):
        tsarg = {}
        for flag, value in TECHSET_FLAGS.items():
            tsarg.update({flag: (value in techset)})
        return tsarg
    
    @staticmethod
    def toGDT(mtl:Material):
        ver  = 'CoD4'
        path = f'texture_assets\\\\{ver}\\\\{mtl.Name}\\\\'
        pathNormal = f'texture_assets\\\\{ver}\\\\{mtl.NormalMap.Path}\\\\'
        pathSpec = f'texture_assets\\\\{ver}\\\\{mtl.SpecGlossMap.Path}\\\\'
        envpars = json.loads(mtl.EnvMapParms)
        cTint = json.loads(mtl.ColorTint)
        techsetArgs = json.loads(mtl.TechsetArgs)
        string = (
            f'\t"{mtl.Name}" ( "material.gdf" )\n'
            f'\t{{\n'
            f'\t\t"template" "material.template"\n'
		    f'\t\t"materialType" "model phong"\n'
            f'\t\t"surfaceType" "{SURFACETYPE}"\n'
            f'\t\t"envMapMin" "{envpars[0]}"\n'
		    f'\t\t"envMapMax" "{envpars[1]}"\n'
		    f'\t\t"envMapExponent" "{envpars[2]}"\n'
            f'\t\t"colorMap" "{path}{mtl.ColorMap}.tga"\n'
            f'\t\t"colorTint" "{cTint[0]:.6f} {cTint[1]:.6f} {cTint[2]:.6f} {cTint[3]:.6f}"\n'
        )
        if techsetArgs['NORMAL']:
            string += f'\t\t"normalMap" "{pathNormal}{mtl.NormalMap.Name}.tga"\n'
        else:
            string += f'\t\t"normalMap" "$identityNormalMap"\n'
        if techsetArgs['SPEC']:
            string +=(
                    f'\t\t"specColorMap" "{pathSpec}{mtl.SpecGlossMap.SpecMap}.tga"\n'
		            f'\t\t"cosinePowerMap" "{pathSpec}{mtl.SpecGlossMap.GlossMap}.tga"\n')
        if techsetArgs['REPLACE']:
            string += (f'\t\t"blendFunc" "Replace*"\n'
                       f'\t\t"depthWrite" "<auto>*"\n')
        elif techsetArgs['BLEND']:
            string += (f'\t\t"blendFunc" "Blend"\n'
                       f'\t\t"depthWrite" "On"\n')
        if techsetArgs['ALPHATEST']:
            string += f'\t\t"alphaTest" "GE128"\n'
        else:
            string += f'\t\t"alphaTest" "Always*"\n'
        string += f'\t}}\n'
        return string

    @classmethod
    def MaterialMaker(cls, materialFile):
        # Offsets
        mtlName_offset = struct.unpack('i', materialFile[0:4])[0]
        techset_offset = struct.unpack('i', materialFile[TECHSET:TECHSET+4])[0]
        color_offset   = struct.unpack('i', materialFile[COLOR:COLOR+4])[0]
        normal_offset  = struct.unpack('i', materialFile[NORMAL:NORMAL+4])[0]
        spec_offset    = struct.unpack('i', materialFile[SPEC:SPEC+4])[0]

        newMtl = Material()
        # Texture Names
        newMtl.Name        = cls.getMtlString(materialFile, mtlName_offset)
        if Material.query.filter(Material.Name == newMtl.Name).first(): 
            return False
        newMtl.Techset     = cls.getMtlString(materialFile, techset_offset)
        newMtl.TechsetArgs = json.dumps(cls.getTechsetArgs(newMtl.Techset))
        newMtl.ColorMap    = cls.getMtlString(materialFile, color_offset)
        normal             = cls.getMtlString(materialFile, normal_offset)
        raw_spec           = cls.getMtlString(materialFile, spec_offset)

        sg = SpecGloss.query.filter(SpecGloss.RawSpecMap == raw_spec).first()

        if sg:
            sg.Materials.append(newMtl)
            # newMtl.RawSpecMap = sg
        else:
            # Names for conversion
            spec = '_'.join(raw_spec.split('&')[0].strip(
                '~').split('_')[:-1]) + SPEC_SUFFIX
            gloss = spec[:-len(SPEC_SUFFIX)] + GLOSS_SUFFIX

            newMtl.SpecGlossMap = SpecGloss(
                RawSpecMap = raw_spec,
                SpecMap    = spec,
                GlossMap   = gloss,
                Path       = newMtl.Name
            )

        nml = Normal.query.filter(Normal.Name == normal).first()
        if nml: 
            nml.Materials.append(newMtl)
            # newMtl.Normal_Id = nml.Id
        else: 
            newMtl.NormalMap = Normal(
                Name = normal,
                Path = newMtl.Name
            )

        envMapMin, envMapMax, envMapExponent = struct.unpack('3f',
            bytes([int(x) for x in materialFile[ENVPARAM:ENVPARAM+12]]))
        
        if envMapMin > envMapMax:
            raise Exception(f'envMapMin maior que envMapMax: {envMapMin} > {envMapMax}')

        envMapMin, envMapMax = envMapMin/4, envMapMax/4
        newMtl.EnvMapParms = json.dumps(
            (round(envMapMin/4, 2), round(envMapMax/4, 2), round(envMapExponent, 2)))

        newMtl.ColorTint = json.dumps(struct.unpack('4f', bytes(
            [int(x) for x in materialFile[COLORTINT:COLORTINT+16]])))

        return newMtl


class ListScroll(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(ListScroll, self).__init__(master, **kw)

        self.entry_search = ttk.Entry(master=self)
        self.entry_search.grid(column=0, row=0, padx=10,
                               pady=10, sticky='news', columnspan=2)
        self.entry_search.bind('<KeyRelease>', self.searchApply)

        self.scrFrame = ScrolledFrame(master=self, autohide=False)
        self.scrFrame.grid(sticky='news', column=0, padx=10, pady=10, row=1, columnspan=2)

        self.exportButton = ttk.Button(
            master=self, text='Export Materials', command=self.exportMtls)
        self.exportButton.grid(column=0, row=2, padx=10, pady=10)

        self.deleteButton = ttk.Button(master=self, text='Delete Materials')
        self.deleteButton.grid(column=1, row=2, padx=10, pady=10)

    def exportMtls(self):
        gdtResult = '{\n'
        for w in self.scrFrame.winfo_children():
            if 'selected' in w.state():
                # print(f'{w["text"] = }')
                gdtResult += MaterialMaker.toGDT(Material.query.filter(Material.Name == w["text"]).first())
        gdtResult += '}'
        print(gdtResult)
                

    def searchApply(self, evt=None):
        filter = self.entry_search.get()
        for w in self.scrFrame.winfo_children():
            w.destroy()
        if filter == '':
            self.canvasPopulation(Material.query.order_by(Material.Name).all())
        else:
            self.canvasPopulation(Material.query.filter(
                Material.Name.ilike(f'%{filter}%')).order_by(asc(Material.Name)).all())

    def canvasPopulation(self, mtl_list):
        for i, mtl in enumerate(mtl_list):
            # sv = StringVar(value=mtl.Name)
            chbox = ttk.Checkbutton(master=self.scrFrame, text=mtl.Name)
            chbox.state(['!alternate'])
            chbox.grid(column=0, row=i, padx=5, pady=5, sticky='news')
            # chbox.pack(fill='both',padx=5,pady=3)


class App(ttk.Window):
    def __init__(self, title="ttkbootstrap", themename="litera", iconphoto='', size=None, position=None,
                 minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None,
                 overrideredirect=False, alpha=1):
        super().__init__(title, themename, iconphoto, size, position, minsize,
                         maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)
        self.frame = ttk.Frame(self, height=100, width=100)
        self.frame.pack()

        self.entry = ttk.Entry(master=self.frame)
        self.entry.grid(column=0, row=0, padx=(10, 0))

        self.selectFile = ttk.Button(
            master    = self.frame,
            text      = '...',
            bootstyle = SECONDARY,
            command   = self.selectFileDialog
        )
        self.selectFile.grid(column=1, row=0, padx=(0, 10))

        self.listScr = ListScroll(master=self.frame)
        self.listScr.grid(column=2, row=0, rowspan=5, padx=20, pady=20)

        self.listScr.canvasPopulation(Material.query.order_by(Material.Name).all())

        # for w in self.listScr.scrFrame.winfo_children():
        #     print(w.state())

    def selectFileDialog(self):
        try:
            with filedialog.askopenfile(mode='rb', initialdir=BASE_DIR) as f:
                file, fname = f.read(), os.path.basename(f.name)
        except Exception as e:
            messagebox.showerror(title='Erro', message=f'ocorreu um erro nao tratado!!!\n{e}')
            return
        mtl = MaterialMaker.MaterialMaker(file)
        if mtl: 
            session.add(mtl)
            session.commit()
            self.listScr.searchApply()
        else: 
            messagebox.showerror(
                title='Erro', message=f"Material {fname} ja cadastrado")


if __name__ == "__main__":

    testObj = App(title='TestApp', themename="vapor", resizable=(False, False))
    testObj.mainloop()
