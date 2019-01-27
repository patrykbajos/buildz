import os.path
import re
import platform
import subprocess
from copy import deepcopy
from pathlib import Path

from schema import Optional, Schema, SchemaError

from buildz.toolchain.generic import GenericToolchain
from buildz.utils import (find_re_it_in_list, get_buildz_mod, get_cmd_matches,
                          merge, merge_envs, get_abs_mod_path, resolve_rel_paths_list)


class GccToolchain(GenericToolchain):
    _conf_sch_val = deepcopy(GenericToolchain._conf_sch_val)
    _env_sch_val = deepcopy(GenericToolchain._env_sch_val)

    _conf_sch_val.update({
        'gcc_path': str
    })
    _env_sch_val.update({
        Optional('compile_flags'): [str],
        Optional('link_flags'): [str],
        Optional('includes'): [str],
        Optional('defines'): [str]
    })

    def __init__(self, conf, env):
        super().__init__(conf, env)
    
    # gcc -xc -E -v /dev/null
    def get_includes(self):
        args = [self.conf['gcc_path'], '-xc', '-E', '-v', os.devnull]
        args.extend(self.env.get('flags', []))

        incl_start_regex = r' *#include <\.\.\.> search starts here: *'
        incl_end_regex = r' *End of search list\. *'

        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , text=True)
        lines = proc.stdout.splitlines()
    
        start_it = find_re_it_in_list(incl_start_regex, lines)
        if start_it == None:
            return []

        end_it = find_re_it_in_list(incl_end_regex, lines, start_it)
        if end_it == None:
            return []

        # theres no paths between them
        if (end_it - start_it) == 1:
            return []

        return lines[start_it+1 : end_it]

    # gcc -dM -E - $flags 0</dev/null 
    # avr-gcc -mmcu= -DF_CPU= -dM -E - $flags 0</dev/null
    def get_defines(self, env):
        def_regex = r'^ *#define +(.+?) +(.+?) *$'
        temp_env = merge(self.env, env)

        args = [self.conf['gcc_path'], '-dM', '-E', '-']
        args.extend(temp_env.get('flags', []))
        matches = get_cmd_matches(args, def_regex, subprocess.DEVNULL)

        if not matches:
            return []

        # matches is tuple of (defname:str, defvalue:str)
        return matches

    def is_valid(self):
        env_sch = Schema(self._env_sch_val)
        conf_sch = Schema(self._conf_sch_val)

        return env_sch.is_valid(self.env) and conf_sch.is_valid(self.conf)

    # TODO extract submethods
    def build_mod(self, build_type, mod_name, tch_name, tch, trg_name, trg_env):
        try:
            mod = get_buildz_mod(mod_name)
        except FileNotFoundError:
            print('GccToolchain.build_mod(): Not found module.')
            return
        except:
            print("GccToolchain.build_mod(): Unexpeced error getting build module.")
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

        compile_flags = env.get('compile_flags', [])
        link_flags = env.get('link_flags', [])
        incls = ['-I'+x for x in env_incls]

        out_name_params = {
            'build_type': build_type,
            'module_name': mod_name,
            'target_name': trg_name,
            'target_toolchain': tch_name,
            'env': deepcopy(env)
        }

        out_absdir = Path(tch['output_dir'].format(**out_name_params)).resolve()
        out_name = tch['output_pattern'].format(**out_name_params)
        defs = ['-D'+d.format(**out_name_params) for d in env_defs]

        # compiling
        obj_abspaths = []
        mod_absdir = get_abs_mod_path(mod_name).parent
        os.makedirs(str(out_absdir), exist_ok=True)
        gcc_pathstr = self.conf['gcc_path']

        for f_pathstr in mod['files']:
            with Path(f_pathstr) as f_path:
                if f_path.is_absolute():
                    continue

                obj_abspath = out_absdir / 'obj' / f_path.with_suffix('.o')
                obj_abspaths.append(obj_abspath)
                in_abspath = mod_absdir / f_pathstr

                comp_args = [ gcc_pathstr, '-c', '-o', str(obj_abspath)]
                comp_args.extend(compile_flags)
                comp_args.extend(defs)
                comp_args.extend(incls)
                comp_args.append(str(in_abspath))

                comp_proc = subprocess.run(comp_args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                if comp_proc.returncode == 0:
                    print("GccToolchain.build_mod(): GCC compiled {} with no errors.".format(f_pathstr))
                else:
                    print('GccToolchain.build_mod(): GCC returned with errors for file {}:\n'.format(f_pathstr), comp_proc.stdout, '\n')

        # linking
        if(platform.system() == 'Windows'):
            bin_ext = '.exe'
        else:
            bin_ext = ''
        
        for obj_abspath in obj_abspaths:
            os.makedirs(str(obj_abspath.parent), exist_ok=True)

        bin_abspath = out_absdir / str(out_name+bin_ext)

        link_args = [gcc_pathstr]
        link_args.extend(link_flags)
        link_args.extend(['-o', str(bin_abspath)])
        link_args.extend(obj_abspaths)
        link_proc = subprocess.run(link_args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if link_proc.returncode == 0:
            print("GccToolchain.build_mod(): GCC linking returned with no errors.")
        else:
            print('GccToolchain.build_mod(): GCC returned with errors for file {}:\n'.format(f_pathstr), link_proc.stdout, '\n')
            
        return (link_proc.returncode == 0)

    # VSCode support
    def gen_tasks(self, trg_name, trg):
        return [
            (trg_name)
        ]
    
    def gen_config(self, trg_name):
        return {}