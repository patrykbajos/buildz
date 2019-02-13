from buildz.config.bzconfig import BZConfig
from buildz.config.module import Module
from buildz.toolchain.factory import factory_toolchain

class BuildzSelfFrontend():
    def __init__(self):
        return

    def build(self):
        bz = BZConfig.from_file()

        for trg in bz.targets.values():
            print('Processing target {}.'.format(trg.name))

            # trg.modules can be mod names list or string 'all'
            if trg.modules == 'all':
                modules = bz.modules
            else:
                modules = trg.modules

            tch = bz.toolchains[trg.toolchain]
            tch_handler = factory_toolchain(tch)

            for mod_name in modules:
                print('Processing module {} of target {}.'.format(mod_name, trg.name))
                mod = Module.from_file(mod_name)
                tch_handler.build_mod(bz, mod, trg)

    _route = build