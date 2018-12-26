from buildz.frontend.vscode import VSCodeFrontend
from buildz.frontend.buildzself import BuildzSelfFrontend
from buildz.utils import get_buildz_conf, get_buildz_mod, factory_toolchain

import sys

def build(mod_args):
    bz_conf = get_buildz_conf()
    tch_dict = bz_conf.toolchains

    for tg_name, tg in bz_conf.targets.values():
        print('Processing target {}.'.format(tg_name))

        # tg.modules can be mod names list or string 'all'
        tg_mod_names = tg.modules
        if tg_mod_names == 'all':
            tg_mod_names = bz_conf.modules

        tch = factory_toolchain(tg.toolchain, tch_dict)

        for mod_name in tg_mod_names:
            print('Processing module {} of target {}.'.format(mod_name, tg_name))
            mod_conf = get_buildz_mod(mod_name)
            tch.build_mod(mod_name, mod_conf



    return

def main():
    mod = None
    mod_args = []

    if len(sys.argv) == 1:
        print("Please specify module")
        return -1
    elif len(sys.argv) == 2:
        mod = sys.argv[1]
    else:
        mod = sys.argv[1]
        mod_args = sys.argv[2:]

    if mod == "build":
        build(mod_args)
    elif mod == "vscode":
        vsc = VSCodeFrontend()
        vsc.run(mod_args)
    else:
        print("Unknown module \"{}\"".format(mod))
    return 0

if __name__ == "__main__":
    result = main()
    sys.exit(result)
