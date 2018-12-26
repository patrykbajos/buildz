from buildz.toolchain.generic import GenericToolchain
from buildz.utils import get_cmd_matches, get_buildz_mod, merge

from schema import Schema, SchemaError, Optional
import subprocess
from pathlib import Path
import os.path

class GccToolchain(GenericToolchain):
    _conf_sch_val = {
        "gcc_path": str
    }

    _env_sch_val = {
        Optional("flags"): [str],
        Optional("includes"): [str],
        Optional("defines"): [str]
    }

    _def_regex = r'^ *#define +(.+?) +(.+?) *$'
    _incl_regex = r'^ *#include <...> search starts here: *$'

    def get_includes(self, env):
        # gcc -xc -E -v -        
        args = [self._conf['gcc_path'], '-xc', '-E', '-v', '-']
        args.extend(self._env.get('flags', []))

        matches = get_cmd_matches(args, self._incl_regex)

        if not matches or not isinstance(matches, list):
            return []

        # i is : separated string of includes
        i = str(matches[0])
        return i.split(':')

    def get_defines(self, env):
        # gcc -dM -E - $flags 0</dev/null 
        # avr-gcc -mmcu= -DF_CPU= -dM -E - $flags 0</dev/null
        l_env = merge(self._env, env)

        args = [self._conf['gcc_path'], '-dM', '-E', '-']
        args.extend(l_env.get('flags', []))
        matches = get_cmd_matches(args, self._def_regex, subprocess.DEVNULL)

        if not matches:
            return []

        # matches is tuple of (defname:str, defvalue:str)
        return matches

    def is_valid(self):
        return self._env_sch.is_valid(self._env) and self._conf_sch.is_valid(self._conf)

    def build_mod(self, mod_name, out_dir, toolchain_name, toolchain, env):
        try:
            mod = get_buildz_mod(mod_name)
        except FileNotFoundError:
            print('GccToolchain.build_mod(): Not found module.')
            return
        except:
            print("GccToolchain.boild_mod(): Unexpeced error getting build module.")
            return

        mod_envs = mod.get('env', {})
        mod_env = self._env_sch.validate(mod_envs.get(toolchain_name, {}))
        mod_files = mod.get('files', [])

        try:
            lenv = merge(env, mod_env)
        except:
            lenv = env

        defs = ['-D'+x for x in lenv.get('defines', [])]
        incls = ['-I'+x for x in lenv.get('includes', [])]
        flgs = lenv.get('flags', [])
        gcc_path = self._conf['gcc_path']

        for f_path in mod_files:
            f_name = os.path.basename(f_path)
            out_name = os.path.splitext(f_name)[0] + '.o'
            out_path = '{}/{}'.format(out_dir, out_name)

            args = [ gcc_path, '-c', f_path ]
            args.extend(flgs)
            args.extend(defs)
            args.extend(incls)
            args.extend(['-o', out_path])

            proc = subprocess.run(args, check=False, stderr=subprocess.STDOUT, text=True)

            if proc.returncode == 0:
                print("GccToolchain.build_mod(): GCC returnet with no errors.")
            else:
                print('GccToolchain.build_mod(): GCC returned with errors:\n', proc.stdout, '\n')
            
        return

    def __init__(self, conf, env):
        self._set_conf(conf)
        self._set_env(env)
