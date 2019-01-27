import os
import subprocess
import platform
from copy import deepcopy
from pathlib import Path

from pyavrutils import AvrGcc, AvrGccCompileError
from schema import Optional, Schema, Or

from buildz.toolchain.gcc import GccToolchain
from buildz.utils import get_buildz_mod, merge_envs, get_abs_mod_path, resolve_rel_paths_list


class AvrGccToolchain(GccToolchain):
    _env_sch_val = deepcopy(GccToolchain._env_sch_val)
    _env_sch_val.update({
        Optional('mcu'): str,
        Optional('fcpu'): [int],
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
            print('AvrGccToolchain.build_mod(): Not found module {}.'.format(mod_name))
            return
        except:
            print("AvrGccToolchain.build_mod(): Unexpeced error getting build module {}.".format(mod_name))
            return

        mod_absdir = get_abs_mod_path(mod_name).parent
        mod_envs = mod.get('env', {})
        mod_env = mod_envs.get(tch_name, {})

        tch_incls_temp = self.env.get('includes', [])
        trg_incls_temp = trg_env.get('includes', [])
        mod_incls_temp = mod_env.get('includes', [])

        self.env['includes'] = resolve_rel_paths_list(tch_incls_temp, os.getcwd())
        trg_env['includes'] = resolve_rel_paths_list(trg_incls_temp, os.getcwd())
        mod_env['includes'] = resolve_rel_paths_list(mod_incls_temp, mod_absdir)

        env = merge_envs(self.env, mod_env, trg_env, self._env_sch_val)  

        env_defs = env.get('defines', [])
        env_incls = env.get('includes', [])
        env_mcu =  env.get('mcu')
        env_fcpu = env.get('fcpu')
        env_cflags = env.get('compile_flags', [])
        env_opt = env.get('optimization')


        cc.cc = gcc_pathstr
        cc.includes = env_incls
        if env_opt:
            cc.optimization = env_opt
        cc.options_extra.extend(env_cflags)
        cc.mcu = env_mcu

        out_name_params = {
            'build_type': build_type,
            'module_name': mod_name,
            'target_name': trg_name,
            'target_toolchain': tch_name,
            'env': deepcopy(env)
        }

        out_absdir = Path(tch['output_dir'].format(**out_name_params)).resolve()
        out_name_pattern = tch['output_pattern']
        os.makedirs(str(out_absdir), exist_ok=True)
        cc.defines = [d.format(**out_name_params) for d in env_defs]
        gcc_pathstr = self.conf['gcc_path']


        for f_cpu in env_fcpu:
                out_name_params['env']['fcpu'] = f_cpu
                out_name = out_name_pattern.format(**out_name_params)

                src_abspath_strs = []
                for f_pathstr in mod['files']:
                    f_path = Path(f_pathstr)
                    if f_path.is_absolute():
                        continue

                    src_abspath_strs.append(str(mod_absdir / f_pathstr))

                cc.output = str(out_absdir / out_name)
                cc.f_cpu = f_cpu

                try:
                    cc.build(src_abspath_strs)
                except AvrGccCompileError as err:
                    print(err) 

    # VSCode support
    def gen_task_params(self, trg_name, trg):
        fcpus = trg['env'].get('fcpu', [])

        return [(trg_name, str(fcpu)) for fcpu in fcpus]
    
    def gen_config(self, trg_name, fcpu):
        return {}