from buildz.utils import get_buildz_conf
from buildz.toolchain.factory import factory_named_toolchain

class BuildzSelfFrontend():
    def __init__(self):
        return

    def build(self):
        bz_conf = get_buildz_conf()

        tchs = bz_conf['toolchains']
        trgs = bz_conf['targets']

        build_type = bz_conf['build']['type']

        for trg_name, trg in trgs.items():
            print('Processing target {}.'.format(trg_name))

            # tg.modules can be mod names list or string 'all'
            trg_mod_names = trg['modules']
            if trg_mod_names == 'all':
                trg_mod_names = bz_conf['modules']

            trg_env = trg['env']

            tch_name = trg['toolchain']
            tch = tchs[tch_name]
            tch_handler = factory_named_toolchain(tch_name, tchs)

            for mod_name in trg_mod_names:
                print('Processing module {} of target {}.'.format(mod_name, trg_name))
            
                tch_handler.build_mod(build_type, mod_name, tch_name, tch, trg_name, trg_env)

    _route = build