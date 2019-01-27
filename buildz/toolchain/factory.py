from buildz.toolchain.avrgcc import AvrGccToolchain
from buildz.toolchain.gcc import GccToolchain

def factory_toolchain(tch):
    if tch.type == 'GccToolchain':
        return GccToolchain(tch)
    if tch.type == 'AvrGccToolchain':
        return AvrGccToolchain(tch)
    
    raise ValueError('Unknown toolchain type {}.'.format(tch.type))
    