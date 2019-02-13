import os.path
import re
import platform
import subprocess
from copy import deepcopy
from pathlib import Path

from schema import Optional, Schema, SchemaError, Or

from buildz.toolchain.generic import GenericToolchain
from buildz.utils import find_re_it_in_list, get_cmd_matches, merge, merge_envs, resolve_rel_paths_list


class GccToolchain(GenericToolchain):
    _confsch = Schema(merge(GenericToolchain._confsch._schema, {
        'gcc_path': str,
        'ar_path': str,
        'ld_path': str
    }))

    _envsch = Schema(merge(GenericToolchain._envsch._schema, {
        Optional('compile_flags'): [str],
        Optional('optimization'): Or(0, 1, 2, 3, 's'),
        Optional('includes'): [str],
        Optional('defines'): [str],

        Optional('build_type'): str,
        Optional('debug_level'): Or(0, 1, None, 3),

        Optional('link_flags'): [str],
        Optional('link_dirs'): [str],
        Optional('link'): [str]
    }))

    __execext = {
        'Windows': '.exe',
        'Linux': ''
    }

    __sharedext = {
        'Windows': '.dll',
        'Linux': '.so'
    }

    def __init__(self, toolchain_setup):
        super().__init__(toolchain_setup)
    
    def default_includes(self):
        # gcc -xc -E -v /dev/null
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

    def defines(self, uf_env):
        # gcc -dM -E - $flags 0</dev/null 
        def_regex = r'^ *#define +(.+?) +(.+?) *$'
        temp_env = merge(self.env, uf_env)

        args = [self.conf['gcc_path'], '-dM', '-E', '-']
        args.extend(temp_env.get('flags', []))
        matches = get_cmd_matches(args, def_regex, subprocess.DEVNULL)

        if not matches:
            return []

        # matches is tuple of (defname:str, defvalue:str)
        return matches

    def _unifiedflags_env(self, env):
        incls = env.get('includes', [])
        defs = env.get('defines', [])
        opt = env.get('optimization', 3)

        build_type = env.get('build_type', 'release')
        debug_level = env.get('debug_level', None)

        fl = []
        if build_type == 'debug':
            fl.append('-g' + debug_level)
            fl.append('-D_DEBUG')
        if build_type == 'release':
            fl.append('-DNDEBUG')

        fl.append('-O' + str(opt))
        fl.extend(['-D' + d for d in defs])
        fl.extend(['-I' + i for i in incls])

        return {
            'compile_flags': fl
        }

    def build_mod(self, config, module, target):
        mod_env = module.envs.get(target.toolchain, {})

        name_params = {
            'build_type': config.build.type,
            'module_name': module.name,
            'target_name': target.name,
            'target_toolchain': target.toolchain
        }

        norm_tchenv = self._normalize_env(self.env, os.getcwd(), name_params)
        norm_modenv = self._normalize_env(mod_env, module.absdir, name_params)
        norm_trgenv = self._normalize_env(target.env, os.getcwd(), name_params)

        env = merge_envs(norm_tchenv, norm_modenv, norm_trgenv, self._envsch)
        uf_env = self._unifiedflags_env(env)
        env = merge(env, uf_env)

        out_absdir = Path(self.setup.output_dir.format(**name_params)).resolve()
        obj_absdir = (out_absdir / 'obj')

        objects = self._build_objects(env, obj_absdir, module) 
        
        out_name = self.setup.output_pattern.format(**name_params)

        if module.packaging == 'executable':
            result = self._link(env, objects, False, out_absdir, out_name)
        if module.packaging == 'shared':
            result = self._link(env, objects, True, out_absdir, out_name)
        if module.packaging == 'static':
            result = self._ar_objects(env, objects, out_absdir, out_name)
        
        return (result == 0)

    def _normalize_env(self, env, path, name_params):
        tenv = deepcopy(env)

        for key, val in tenv.items():
            if isinstance(val, list):
                temp = []
                for elem in val:
                    if isinstance(elem, str):
                        temp.append(elem.format(**name_params))
                    else:
                        temp.append(elem)
                tenv[key] = temp
            if isinstance(val, str):
                tenv[key] = val.format(**name_params)

        tenv['includes'] = resolve_rel_paths_list(env.get('includes', []), path)
        tenv['link_dirs'] = resolve_rel_paths_list(env.get('link_dirs', []), path)

        return tenv

    def _build_objects(self, uf_env, objs_absdir, module):
        gcc = self.conf['gcc_path']
        
        flags = uf_env.get('compile_flags', [])

        objs_absdir = Path(objs_absdir)
        os.makedirs(str(objs_absdir), exist_ok=True)
        obj_abspaths = []

        for fp_str in module.files:
            fp = Path(fp_str)

            if fp.is_absolute():
                obj_abspath = Path(objs_absdir) / (fp.stem + '.o')
                fp_abspath = fp
            else:
                obj_abspath = Path(objs_absdir) / fp.with_suffix('.o')
                fp_abspath = module.absdir / fp

            os.makedirs(obj_abspath.parent, exist_ok=True)

            # if obj is newer than source compilation is nonsense
            if obj_abspath.exists():
                obj_mtime = obj_abspath.stat().st_mtime
                src_mtime = fp_abspath.stat().st_mtime

                if src_mtime < obj_mtime:
                    continue

            args = [gcc, '-c', '-o', str(obj_abspath)]
            args.extend(flags)
            args.append(fp_abspath)

            proc = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            if proc.returncode == 0:
                print("[GCC] Compiled {} without errors.".format(fp_str))
            else:
                print('[GCC] Returned with errors for file {}:\n'.format(fp_str), proc.stdout)
                break

            obj_abspaths.append(obj_abspath)
        return obj_abspaths

    def _link(self, env, obj_abspaths, shared, exe_absdir, exe_name):
        if shared:
            ext = self.__sharedext[platform.system()]
            exe_name = ('lib' + exe_name)
        else:
            ext = self.__execext[platform.system()]
    
        exe_absdir = Path(exe_absdir)

        if shared:
            exe_abspath = exe_absdir / (exe_name + ext)
        else:
            exe_abspath = exe_absdir / (exe_name + ext)

        ld = self.conf['ld_path']
        link_dirs = ['-L ' + l for l in self.env.get('link_dirs', [])]
        link = ['-l ' + l for l in self.env.get('link', [])]
        link_flags = self.env.get('link_flags', [])

        args = [ld]
        
        if shared:
            if platform.system() == 'Windows':
                args.append('--dll --output-def {}'.format(exe_absdir / (exe_name + '.def')))
            if platform.system() == 'Linux':
                args.append('-shared -soname={}'.format(exe_name + ext))

        args.extend(link_dirs)
        args.extend(link_flags)
        args.extend(link)
        args.extend(['-o', str(exe_abspath)])
        args.extend(obj_abspaths)

        proc = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if proc.returncode == 0:
            print("[LINKER] Linked {} without errors.".format(exe_name+ext))
        else:
            print('[LINKER] Returned errors for file {}:\n'.format(exe_name+ext), proc.stdout, '\n')

        return proc.returncode

    def _ar_objects(self, env, obj_abspaths, a_absdir, a_name):
        a_name = ('lib' + a_name + '.a')
        a_abspath = Path(a_absdir) / a_name

        ar = self.conf['ar_path']

        args = [ar]
        args.extend(['-r', str(a_abspath)])
        args.extend(obj_abspaths)

        proc = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if proc.returncode == 0:
            print("[AR] Archived without errors.")
        else:
            print('[AR] Failed for file {}:\n'.format(a_name), proc.stdout, '\n')

        return proc.returncode

    # VSCode support
    def gen_tasks(self, target):
        return [
            (target.name)
        ]
    
    def gen_config(self, target):
        return {}