
from typing import List
from sqlalchemy.orm import Relationship, Mapped
from sqlalchemy import Column, ForeignKey, Integer, Null, String
from Models.base import Model


class Material(Model):
    __tablename__ = 'materials'
    Id            = Column(Integer, primary_key=True)
    CodVersion    = Column(Integer, nullable=False, default=0)
    Name          = Column(String, unique=True, nullable=False)
    Techset       = Column(String, nullable=False)
    TechsetArgs   = Column(String, nullable=False)
    ColorMap      = Column(String, nullable=False)
    EnvMapParms   = Column(String, nullable=False)  # Convert array to json
    ColorTint     = Column(String, nullable=False)  # Convert array to json
    SurfaceType   = Column(String, nullable=False, default='<none>')
    Properties    = Column(String)

    Normal_Id = Column(Integer, ForeignKey('normals.Id'),
                       nullable=False, unique=False, index=True)
    NormalMap: Mapped['Normal'] = Relationship(back_populates='Materials')

    SpecGloss_Id = Column(Integer, ForeignKey('specglosses.Id'),
                        nullable=False, unique=False, index=True)
    SpecGlossMap: Mapped['SpecGloss'] = Relationship(back_populates='Materials')

    def __repr__(self):
        return (
            f'\nMaterial Name: {self.Name}\n'
            f'Normal Map: {self.NormalMap.Name}\n'
            f'Spec/Gloss: {self.SpecGlossMap.SpecMap} {self.SpecGlossMap.GlossMap}\n'
            f'Texture Paths: texture_assets\\{self.Name}\\\ntexture_assets\\{self.NormalMap.Path}\\\ntexture_assets\\{self.SpecGlossMap.Path}\\\n'
        )


class Normal(Model):
    __tablename__ = 'normals'
    Id            = Column(Integer, primary_key=True)
    Name          = Column(String, unique=True, nullable=False)
    Path          = Column(String, unique=True, nullable=False)
    Materials: Mapped[List['Material']] = Relationship(back_populates='NormalMap', uselist=True)

    def __repr__(self):
        return (
            f'\nNormal Map: {self.Name}\n'
            f'Texture Path Path: {self.Path}\n'
        )


class SpecGloss(Model):
    __tablename__ = 'specglosses'
    Id            = Column(Integer, primary_key=True)
    RawSpecMap    = Column(String, unique=True, nullable=False)
    Path          = Column(String, unique=True, nullable=False)
    SpecMap       = Column(String, nullable=False)
    GlossMap      = Column(String, nullable=False)
    Materials: Mapped[List['Material']] = Relationship(back_populates='SpecGlossMap', uselist=True)

    def __repr__(self):
        return (
            f'\nSpecular Map: {self.SpecMap}\n'
            f'Glossiness Map: {self.GlossMap}\n'
            f'Raw Specular map: {self.RawSpecMap}\n'
            f'Texture Path: {self.Path}'
        )
