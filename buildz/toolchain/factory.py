from buildz.toolchain.avrgcc import AvrGccToolchain
from buildz.toolchain.gcc import GccToolchain

__factoryroute = {
    'GccToolchain': GccToolchain,
    'AvrGccToolchain': AvrGccToolchain
}

def factory_toolchain(tch):
    try:
        return __factoryroute[tch.type](tch)
    except:
        raise ValueError('Unknown toolchain type {}.'.format(tch.type))
    