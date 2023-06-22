import json
import struct
from pathlib import Path

# TKinter
from tkinter import IntVar, StringVar, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# SQLAlchemy
from sqlalchemy import asc, desc, event
from Models.base import Model
from Models.materials import Material, Normal, SpecGloss
from main import session, BASE_DIR, engine

# Misc
# Check this file to edit surface type and spec gloss suffix
from kxdconstants import *

@event.listens_for(Normal.__table__, 'after_create')
def addDefaultNormalMap(target, connection, **kw):
    identity      = Normal()
    identity.Name = '$identitynormalmap'
    identity.Path = 'Default Image'

    session.add(identity)
    session.commit()

Model.metadata.create_all(engine)

class MaterialMaker:   
    @staticmethod
    def getMtlString(mtl:bytes, offset:int) -> str:
        # print(offset)
        string = ''
        while (mtl[offset] != 0x00):
            # print(chr(mtl_file[offset]))
            string += chr(mtl[offset])
            offset += 1
        return string

    @staticmethod
    def getTechsetArgs(techset: str):
        tsArgs = {}
        for flag, value in TECHSET_FLAGS.items():
            tsArgs.update({flag: (value in techset)})
        return tsArgs

    @staticmethod
    def toGDT(mtl: Material) -> str:
        CoDVer      = 'CoD4'
        path        = f'texture_assets\\\\{CoDVer}\\\\{mtl.Name}' + r'\\'
        pathNormal  = f'texture_assets\\\\{CoDVer}\\\\{mtl.NormalMap.Path}' + r'\\'
        pathSpec    = f'texture_assets\\\\{CoDVer}\\\\{mtl.SpecGlossMap.Path}' + r'\\'
        envPars     = json.loads(mtl.EnvMapParms)
        colorTint   = ' '.join(str(x) for x in json.loads(mtl.ColorTint))
        techsetArgs = json.loads(mtl.TechsetArgs)
        surfProps   = json.loads(mtl.Properties) if mtl.Properties else None
        mtlType     = 'model' if mtl.Name[:4] == 'mtl_' else 'world'
        gdtEntry = (
            f'\t"{mtl.Name}" ( "material.gdf" )\n'
             '\t{\n'
             '\t\t"template" "material.template"\n'
            f'\t\t"materialType" "{mtlType} phong"\n'
            f'\t\t"surfaceType" "{mtl.SurfaceType}"\n'
            f'\t\t"envMapMin" "{envPars[0]}"\n'
            f'\t\t"envMapMax" "{envPars[1]}"\n'
            f'\t\t"envMapExponent" "{envPars[2]}"\n'
            f'\t\t"colorMap" "{path}{mtl.ColorMap}.tga"\n'
            f'\t\t"colorTint" "{colorTint}"\n')
        if surfProps:
            for prop in surfProps:
                gdtEntry += f'\t\t"{prop}" "1"\n'
        if techsetArgs['NORMAL']:
            gdtEntry += f'\t\t"normalMap" "{pathNormal}{mtl.NormalMap.Name}.tga"\n'
        else:
            gdtEntry += '\t\t"normalMap" "$identityNormalMap"\n'
        if techsetArgs['SPEC']:
            gdtEntry += (
                f'\t\t"specColorMap" "{pathSpec}{mtl.SpecGlossMap.SpecMap}.tga"\n'
                f'\t\t"cosinePowerMap" "{pathSpec}{mtl.SpecGlossMap.GlossMap}.tga"\n')
        if techsetArgs['REPLACE']:
            gdtEntry += ('\t\t"blendFunc" "Replace*"\n'
                       '\t\t"depthWrite" "<auto>*"\n')
        elif techsetArgs['BLEND']:
            gdtEntry += ('\t\t"blendFunc" "Blend"\n'
                       '\t\t"depthWrite" "On"\n')
        if techsetArgs['ALPHATEST']:
            gdtEntry += '\t\t"alphaTest" "GE128"\n'
        else:
            gdtEntry += '\t\t"alphaTest" "Always*"\n'
        gdtEntry += '\t}\n'
        return gdtEntry

    @classmethod
    def MaterialMaker(cls, materialFile:bytes) -> tuple[Material|bool, bool]:
        commit = False
        # Offsets
        mtlName_offset = struct.unpack('<I', materialFile[0:4])[0]
        techset_offset = struct.unpack('<I', materialFile[TECHSET:TECHSET+4])[0]
        color_offset   = struct.unpack('<I', materialFile[COLOR:COLOR+4])[0]
        normal_offset  = struct.unpack('<I', materialFile[NORMAL:NORMAL+4])[0]
        spec_offset    = struct.unpack('<I', materialFile[SPEC:SPEC+4])[0]

        newMtl = Material()
        # Texture Names
        newMtl.Name        = cls.getMtlString(materialFile, mtlName_offset)
        if Material.query.filter(Material.Name == newMtl.Name).first() or newMtl.Name[0:3] == 'gfx_': 
            return False, False
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
            commit = True
            # Names for conversion
            spec = '_'.join(raw_spec.split('&')[0].strip(
                '~').split('_')[:-1]) + SPEC_SUFFIX
            gloss = spec[:-len(SPEC_SUFFIX)] + GLOSS_SUFFIX

            newMtl.SpecGlossMap = SpecGloss(
                RawSpecMap = raw_spec,
                SpecMap    = spec,
                GlossMap   = gloss,
                Path       = newMtl.Name)

        nml = Normal.query.filter(Normal.Name == normal).first()
        if nml:
            nml.Materials.append(newMtl)
            # newMtl.Normal_Id = nml.Id
        else:
            commit = True
            newMtl.NormalMap = Normal(
                Name = normal,
                Path = newMtl.Name)

        envMapMin, envMapMax, envMapExponent = struct.unpack(
                    '<3f', materialFile[ENVPARAM:ENVPARAM+12])

        # USELESS, asset manager already does that...
        # if envMapMin > envMapMax:
        #     raise BaseException(
        #         f'Material Invalido!!!\n\
        #         envMapMin maior que envMapMax: {envMapMin:.2f} > {envMapMax:.2f}')

        # envMapMin, envMapMax = envMapMin/4, envMapMax/4
        newMtl.EnvMapParms = json.dumps(
            (round(envMapMin/4, 2), round(envMapMax/4, 2), round(envMapExponent, 2)))

        newMtl.ColorTint = json.dumps(
                struct.unpack('<4f', materialFile[COLORTINT:COLORTINT+16]))
        
        surfaceTypeProps: int = struct.unpack('<I', materialFile[0x20:0x24])[0]


        for surfType in SURFACETYPES:
            if surfaceTypeProps - surfType[1] >= 0:
                newMtl.SurfaceType = surfType[0]
                surfaceTypeProps -= surfType[1]
            if surfaceTypeProps <= 0:
                break

        props = []
        for surfProp in SURFACEPROPS:
            if surfProp[1] > 0 and surfaceTypeProps - surfProp[1] >= 0:
                props.append(surfProp[0])
                surfaceTypeProps -= surfProp[1]
            if surfaceTypeProps <= 0:
                break
        if props:
            newMtl.Properties = json.dumps(props)

        return newMtl, commit


class ListScroll(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super(ListScroll, self).__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.entry_search = ttk.Entry(master=self)
        self.entry_search.grid(
            column = 0,
            row    = 0,
            sticky = 'ew',
            pady   = 10)
        self.entry_search.bind('<KeyRelease>', self.searchApply)

        self.orderByBool = True
        self.orderButtonText = StringVar(value=chr(9650))
        self.orderButton = ttk.Button(
            master       = self,
            textvariable = self.orderButtonText,
            command      = self.invertBoolButton)
        self.orderButton.grid(column=1, row=0, padx=0, pady=10,sticky = 'e')

        self.scrFrame = ScrolledFrame(master=self, autohide=False)
        self.scrFrame.grid(sticky='news', column=0, pady=10, row=1, columnspan=2)

        self.expDelFrame = ttk.Frame(master=self)
        self.expDelFrame.grid(column=0, row=2, sticky='news', columnspan=2)

        self.exportButton = ttk.Button(
            master    = self.expDelFrame,
            text      = 'Export Materials',
            command   = self.exportMtls,
            bootstyle = (SUCCESS, OUTLINE))
        self.exportButton.grid(column=0, row=0, padx=(20,10),
                               pady=(10,0), sticky='ew')

        self.editButton = ttk.Button(
            master    = self.expDelFrame,
            text      = 'Edit Materials',
            bootstyle = (WARNING, OUTLINE))
        self.editButton.grid(column=1, row=0, padx=10,
                               pady=(10, 0), sticky='ew')

        self.deleteButton = ttk.Button(
            master    = self.expDelFrame,
            text      = 'Delete Materials',
            bootstyle = (DANGER, OUTLINE))
        self.deleteButton.grid(column=2, row=0, padx=(10, 20),
                               pady=(10, 0), sticky='ew')

    def invertBoolButton(self):
        self.orderByBool = not self.orderByBool
        self.orderButtonText.set(
            f'{chr(9650) if self.orderByBool else chr(9660)}')
        self.focus()
        self.searchApply()

    def exportMtls(self):
        gdtResult = '{\n'
        for w in self.scrFrame.winfo_children():
            if 'selected' in w.state():
                # print(f'{w["text"] = }')
                gdtResult += MaterialMaker.toGDT(
                    Material.query.filter(Material.Name == w["text"]).first())
        gdtResult += '}'
        with open('result.gdt', 'wt') as f:
            f.write(gdtResult)

    def searchApply(self, evt=None):
        searchFilter = self.entry_search.get()
        orderFunc = asc if self.orderByBool else desc
        for w in self.scrFrame.winfo_children():
            w.destroy()
        if searchFilter == '':
            self.canvasPopulation(Material.query.order_by(orderFunc(Material.Name)).all())
        else:
            self.canvasPopulation(Material.query.filter(
                Material.Name.ilike(f'%{searchFilter}%')).order_by(orderFunc(Material.Name)).all())

    def canvasPopulation(self, mtl_list):
        for i, mtl in enumerate(mtl_list):
            # sv = StringVar(value=mtl.Name)
            chbox = ttk.Checkbutton(master=self.scrFrame, text=mtl.Name)
            chbox.state(['!alternate'])
            chbox.grid(column=0, row=i, padx=5, pady=5, sticky='news')
            # chbox.pack(fill='both',padx=5,pady=3)


class App(ttk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame = ttk.Frame(self)
        self.frame.pack()

        self.rbVar = IntVar(value=0)
        self.rdBtnSingle = ttk.Radiobutton(
            master   = self.frame,
            variable = self.rbVar,
            value    = 0,
            text     = 'Single File')
        self.rdBtnSingle.grid(column=0, row=0, padx=10, pady=10, sticky='news')

        self.rdBtnMulti = ttk.Radiobutton(
            master   = self.frame,
            variable = self.rbVar,
            value    = 1,
            text     = 'Folder')
        self.rdBtnMulti.grid(column=1, row=0, padx=10, pady=10, sticky='news')

        self.selectFile = ttk.Button(
            master    = self.frame,
            text      = '...',
            bootstyle = (SECONDARY, OUTLINE),
            command   = self.selectFileDialog)
        self.selectFile.grid(column=3, row=0, padx=10, pady=10, sticky='ew')

        self.CoDVersionVar = ttk.StringVar()
        self.CoDVersion = ttk.Combobox(
            master       = self.frame,
            state        = 'readonly',
            values       = CODVERSIONS,
            textvariable = self.CoDVersionVar,
            bootstyle    = LIGHT)
        self.CoDVersion.set('CoD Version')
        self.CoDVersion.grid(column=2, row=0, padx=10, pady=10, sticky='ew')

        self.listScr = ListScroll(master=self.frame)
        self.listScr.grid(column=4, row=0, rowspan=10,
                          padx=(10, 20), pady=10, sticky='ew')

        self.listScr.searchApply()

    def selectFileDialog(self):
        try:
            if self.rbVar.get():
                errorList = []
                fDir: Path = Path(filedialog.askdirectory(initialdir=BASE_DIR))
                if not fDir.is_dir() or not fDir.exists():
                    return
                for fName in fDir.iterdir():
                    if not fName.is_file():
                        continue
                    with fName.open(mode='rb') as f:
                        fRead = f.read()
                        try:
                            if fName.name != MaterialMaker.getMtlString(
                                    fRead, struct.unpack('<I', fRead[0:4])[0]):
                                errorList.append(fName.name)
                                continue
                        except:
                            errorList.append(fName.name)
                            continue
                        try:
                            material, commit = MaterialMaker.MaterialMaker(
                                fRead)
                        except:
                            material = False
                        if material:
                            session.add(material)
                            if commit:
                                session.commit()
                        else:
                            errorList.append(fName.name)
                session.commit()
                if errorList:
                    errorString = '\n'.join(errorList)
                    messagebox.showwarning(
                        title   = 'Warning',
                        message = (f'Some material files were not added to the database:\n{errorString}'))
                self.listScr.searchApply()
            else:
                selectedFile: Path = Path(
                    filedialog.askopenfilename(initialdir=BASE_DIR))
                if not selectedFile.is_file() or not selectedFile.exists():
                    messagebox.showerror(
                        title   = 'Erro',
                        message = f"{selectedFile.name} is NOT a file!")
                    return
                with selectedFile.open(mode='rb') as f:
                    file = f.read()
                try:
                    if selectedFile.name != MaterialMaker.getMtlString(file,
                                                            struct.unpack('<I', file[0:4])[0]):
                        material = False
                    else:
                        material, = MaterialMaker.MaterialMaker(file)
                except:
                    material = False
                if material:
                    session.add(material)
                    session.commit()
                    self.listScr.searchApply()
                else:
                    messagebox.showerror(
                        title   = 'Erro',
                        message = f"Material {selectedFile.name} invalido ou ja cadastrado")
        except TypeError:
            return
        except BaseException as e:
            messagebox.showerror(
                title   = 'Erro',
                message = f'ocorreu um erro nao tratado!!!\n{e}')
            return


if __name__ == "__main__":
    app = App(
        title     = 'CoD Material Parser',
        themename = "vapor",
        resizable = (False, False))
    app.mainloop()
