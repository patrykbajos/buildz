import os
import subprocess
import platform
from copy import deepcopy
from pathlib import Path

from pyavrutils import AvrGcc, AvrGccCompileError
from schema import Optional, Schema, Or

from buildz.toolchain.gcc import GccToolchain
from buildz.utils import merge, merge_envs, resolve_rel_paths_list


class AvrGccToolchain(GccToolchain):
    _envsch = Schema(merge(GccToolchain._envsch._schema, {
        Optional('mcu'): str,
        Optional('fcpu'): [int],
    }))

    def __init__(self, toolchain_setup):
        super().__init__(toolchain_setup)

    def _unifiedflags_env(self, env):
        mcu = env.get('mcu')

        return merge(super()._unifiedflags_env(env), {
            'compile_flags': ['-mmcu=' + mcu, '-DF_CPU={fcpu}']
        })

    def build_mod(self, config, module, target):
        mod_env = module.envs.get(target.toolchain, {})

        build_params = {
            'build_type': config.build.type,
            'module_name': module.name,
            'target_name': target.name,
            'target_toolchain': target.toolchain
        }

        norm_tchenv = self._normalize_env(self.env, os.getcwd(), build_params)
        norm_modenv = self._normalize_env(mod_env, module.absdir, build_params)
        norm_trgenv = self._normalize_env(target.env, os.getcwd(), build_params)

        env = merge_envs(norm_tchenv, norm_modenv, norm_trgenv, self._envsch)
        uf_env = self._unifiedflags_env(env)
        env = merge(env, uf_env)

        mcu = env['mcu']

        for fcpu in env['fcpu']:
            print('[AVRGCC] Building module for {} with {} Hz clock.'.format(mcu, fcpu))

            tenv = deepcopy(env)

            outname_params = {
                'mcu': mcu,
                'fcpu': fcpu
            }
            outname_params.update(build_params)

            out_absdir = Path(self.setup.output_dir.format(**outname_params)).resolve()
            obj_absdir = (out_absdir / 'obj_{}_{}'.format(mcu, fcpu))

            tcflags = []
            for flag in env['compile_flags']:
                tcflags.append(flag.format(fcpu=fcpu))
            tenv['compile_flags'] = tcflags

            objects = self._build_objects(tenv, obj_absdir, module) 
            
            out_name = self.setup.output_pattern.format(**outname_params)

            if module.packaging == 'executable':
                result = self._link(tenv, objects, False, out_absdir, out_name)
            if module.packaging == 'shared':
                result = self._link(tenv, objects, True, out_absdir, out_name)
            if module.packaging == 'static':
                result = self._ar_objects(tenv, objects, out_absdir, out_name)
                
            return (result == 0)

    # VSCode support
    def gen_task_params(self, trg):
        fcpus = trg.env.get('fcpu', [])

        return [(trg.name, str(fcpu)) for fcpu in fcpus]
    
    def gen_config(self, trg_name, fcpu):
        return {}