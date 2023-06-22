import os
from dotenv import load_dotenv
load_dotenv()

# Constants
DB_NAME       = 'teste.db'
CODVERSIONS   = ['CoD4', 'WaW', 'BO1']
COLOR         = 0x48
NORMAL        = 0x54
SPEC          = 0x60
ENVPARAM      = 0x68
COLORTINT     = 0x7C
TECHSET       = 0x34
TECHSET_FLAGS = {
    'COLOR'    : "c0",
    'NORMAL'   : "n0",
    'SPEC'     : "s0",
    'REPLACE'  : "r0",
    'ALPHATEST': "t0",
    'BLEND'    : "b0"}

# Change it here if you want :)
# i.e. _spc and _cos
with open(R'mtlprop.csv','rt') as f:
    lines = f.readlines()
SURFACETYPES = sorted([(y[0], int(y[2], base=16)) for y in [x.strip(
    '\n').split(',') for x in lines[:27]]], key=lambda x: x[1], reverse=True)
# print(SURFACETYPES)
SURFACEPROPS = sorted([(y[0], int(y[2], base=16)) for y in [x.strip(
    '\n').split(',') for x in lines[27:]]], key=lambda x: x[1], reverse=True)
# print(SURFACEPROPS)
SPEC_SUFFIX  = os.environ.get('SpecSuffix', '_s')
GLOSS_SUFFIX = os.environ.get('GlossSuffix', '_g')