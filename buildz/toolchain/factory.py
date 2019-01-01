from buildz.toolchain.avrgcc import AvrGccToolchain
from buildz.toolchain.gcc import GccToolchain

def factory_named_toolchain(tch_name, tch_dict):
    tch = tch_dict.get(tch_name)

    if tch is None:
        raise KeyError('Missing toolchain {} in toolchains.'.format(tch_name))

    temp_tch = factory_toolchain_type(tch['type'], tch['conf'], tch['env'])

    return temp_tch

def factory_toolchain_type(type_name, conf, env):
    if type_name == 'GccToolchain':
        return GccToolchain(conf, env)
    if type_name == 'AvrGccToolchain':
        return AvrGccToolchain(conf, env)
    
    raise ValueError('Unknown toolchain type {}.'.format(type_name))