import subprocess
import platform
from copy import deepcopy
from pathlib import Path

from pyavrutils import AvrGcc
from schema import Optional, Schema, Or

from buildz.toolchain.gcc import GccToolchain
from buildz.utils import get_buildz_mod, merge_envs


class AvrGccToolchain(GccToolchain):
    _env_sch_val = deepcopy(GccToolchain._env_sch_val)
    _env_sch_val.update({
        "mcu": str,
        "fcpu": [int],
        Optional('optimization'): Or(0, 1, 2, 3, 's')
    })

    def __init__(self,  conf, env):
        super().__init__(conf, env)

    def make_env(self, compile_flags, mcu, fcpu):
        mcu_flag = '-mmcu={}'.format(mcu)

        return {
            'compile_flags': compile_flags + mcu_flag,
            'defines': 'F_CPU={}'.format(fcpu)
        }

    def get_defines(self, flags, mcu, fcpu):
        return GccToolchain.get_defines(self, self.make_env(flags, mcu, fcpu))

    def build_mod(self, build_type, mod_name, tch_name, tch, trg_name, trg_env):
        try:
            mod = get_buildz_mod(mod_name)
        except FileNotFoundError:
            print('GccToolchain.build_mod(): Not found module.')
            return
        except:
            print("GccToolchain.build_mod(): Unexpeced error getting build module.")
            return

        mod_envs = mod.get('env', {})
        mod_env = mod_envs.get(tch_name, {})
        env = merge_envs(self.env, mod_env, trg_env, self._env_sch_val)  

        env_defs = env.get('defines', [])
        env_incls = env.get('includes', [])
        env_mcu =  env.get('mcu')
        env_fcpu = env.get('fcpu')
        env_cflags = env.get('compile_flags', [])
        env_opt = env.get('optimization')

        gcc_pathstr = self.conf['gcc_path']

        cc = AvrGcc()
        cc.cc = gcc_pathstr
        cc.includes = env_incls
        if env_opt:
            cc.optimization = env_opt
        cc.options_extra.extend(env_cflags)
        cc.mcu = env_mcu
        
        tch_out_dir = Path(tch['output_dir'])
        tch_out_pattern = tch['output_pattern']

        out_name_params = {
            'build_type': build_type,
            'module_name': mod_name,
            'target_name': trg_name,
            'target_toolchain': tch_name,
            'env': deepcopy(env)
        }
        cc.defines = [d.format(**out_name_params) for d in env_defs]

        for f_cpu in env_fcpu:
                out_name_params['env']['fcpu'] = f_cpu
                out_name = tch_out_pattern.format(**out_name_params)

                cc.output = str(tch_out_dir / out_name)
                cc.f_cpu = f_cpu
                cc.build(mod['files'])
