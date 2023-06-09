import os
import json
import struct

# TKinter
from tkinter import IntVar, StringVar, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# SQLAlchemy
from sqlalchemy import asc, desc
from Models.base import Model
from Models.materials import Material, Normal, SpecGloss
from main import session, BASE_DIR, engine

# Misc
# Check this file to edit surface type and spec gloss suffix
from kxdconstants import *

Model.metadata.create_all(engine)

if not Normal.query.filter(Normal.Name == '$identitynormalmap').first():
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
        tsArgs = {}
        for flag, value in TECHSET_FLAGS.items():
            tsArgs.update({flag: (value in techset)})
        return tsArgs

    @staticmethod
    def toGDT(mtl: Material):
        ver         = 'CoD4'
        path        = f'texture_assets\\\\{ver}\\\\{mtl.Name}' + r'\\'
        pathNormal  = f'texture_assets\\\\{ver}\\\\{mtl.NormalMap.Path}' + r'\\'
        pathSpec    = f'texture_assets\\\\{ver}\\\\{mtl.SpecGlossMap.Path}' + r'\\'
        envpars     = json.loads(mtl.EnvMapParms)
        colorTint   = json.loads(mtl.ColorTint)
        techsetArgs = json.loads(mtl.TechsetArgs)
        mtlType = 'model' if mtl.Name[:4] == 'mtl_' else 'world'
        string = (
            f'\t"{mtl.Name}" ( "material.gdf" )\n'
             '\t{\n'
             '\t\t"template" "material.template"\n'
            f'\t\t"materialType" "{mtlType} phong"\n'
            f'\t\t"surfaceType" "{SURFACETYPE}"\n'
            f'\t\t"envMapMin" "{envpars[0]}"\n'
            f'\t\t"envMapMax" "{envpars[1]}"\n'
            f'\t\t"envMapExponent" "{envpars[2]}"\n'
            f'\t\t"colorMap" "{path}{mtl.ColorMap}.tga"\n'
            f'\t\t"colorTint" "{colorTint[0]} {colorTint[1]} {colorTint[2]} {colorTint[3]}"\n')
        if techsetArgs['NORMAL']:
            string += f'\t\t"normalMap" "{pathNormal}{mtl.NormalMap.Name}.tga"\n'
        else:
            string += '\t\t"normalMap" "$identityNormalMap"\n'
        if techsetArgs['SPEC']:
            string += (
                f'\t\t"specColorMap" "{pathSpec}{mtl.SpecGlossMap.SpecMap}.tga"\n'
                f'\t\t"cosinePowerMap" "{pathSpec}{mtl.SpecGlossMap.GlossMap}.tga"\n')
        if techsetArgs['REPLACE']:
            string += ('\t\t"blendFunc" "Replace*"\n'
                       '\t\t"depthWrite" "<auto>*"\n')
        elif techsetArgs['BLEND']:
            string += ('\t\t"blendFunc" "Blend"\n'
                       '\t\t"depthWrite" "On"\n')
        if techsetArgs['ALPHATEST']:
            string += '\t\t"alphaTest" "GE128"\n'
        else:
            string += '\t\t"alphaTest" "Always*"\n'
        string += '\t}\n'
        return string

    @classmethod
    def MaterialMaker(cls, materialFile):
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
        if Material.query.filter(Material.Name == newMtl.Name).first(): 
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
        self.selectFile.grid(column=2, row=0, padx=10, pady=10, sticky='ew')

        self.CoDVersionVar = ttk.StringVar()
        self.CoDVersion = ttk.Combobox(
            master       = self.frame,
            state        = 'readonly',
            values       = ['CoD Version', 'CoD4', 'CoD5', 'BO1'],
            textvariable = self.CoDVersionVar,
            bootstyle    = LIGHT)
        self.CoDVersion.current(0)
        self.CoDVersion.grid(column=3, row=0)

        self.listScr = ListScroll(master=self.frame)
        self.listScr.grid(column=4, row=0, rowspan=10, padx=(10, 20), pady=10)

        self.listScr.searchApply()

    def selectFileDialog(self):
        try:
            if self.rbVar.get():
                fdir = filedialog.askdirectory(initialdir=BASE_DIR)
                for fname in os.listdir(fdir):
                    with open(f'{fdir}/{fname}', 'rb') as f:
                        fread = f.read()
                        if fname != MaterialMaker.getMtlString(
                            fread, struct.unpack('<I', fread[0:4])[0]):
                            continue
                        material, commit = MaterialMaker.MaterialMaker(fread)
                        if material:
                            session.add(material)
                            if commit:
                                session.commit()
                session.commit()
                self.listScr.searchApply()
            else:
                with filedialog.askopenfile(mode='rb', initialdir=BASE_DIR) as f:
                    file, fname = f.read(), os.path.basename(f.name)
                if fname != MaterialMaker.getMtlString(file, struct.unpack('<I', file[0:4])[0]):
                    raise BaseException(
                        'File name and Material name dont match\n\
                            Material file invalid!!!')
                mtl = MaterialMaker.MaterialMaker(file)[0]
                if mtl:
                    session.add(mtl)
                    session.commit()
                    self.listScr.searchApply()
                else:
                    messagebox.showerror(
                        title   = 'Erro',
                        message = f"Material {fname} ja cadastrado")
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
