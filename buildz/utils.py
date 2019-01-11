import json
import re
import subprocess
import types
from copy import deepcopy
from os import getcwd
from pathlib import Path

from schema import And, Optional, Or, Schema, SchemaError, Use, Const

_buildz_mod_schema = Schema({
    'files': [str],
    Optional('env'): {
        Optional(str): object
    }
})

_buildz_schema = Schema({
    'build': {
        'type': Or('release', 'debug'),
        'targets': Or('all', [str]),
    },
    'modules': [str],
    'toolchains': {
        str: {
            'type': str,
            'output_dir': str,
            'output_pattern': str, 
            Optional('env'): {
                Optional(str): object
            },
            Optional('conf'): {
                Optional(str): object
            }
        }
    },
    'targets': {
        str: {
            'modules': Or('all', [str]),
            'toolchain': str,
            Optional('env'): {
                Optional(str): object
            }
        }
    }
})

def get_abs_mod_path(mod_name):
    mod_path = Path(mod_name + '/module.json')

    if not mod_path.is_file():
        raise FileNotFoundError('get_abs_mod_path(): Could not find module {}.'.format(mod_name))

    return mod_path.resolve()

def get_buildz_mod(mod_name):
    mod_path = get_abs_mod_path(mod_name)

    try:
        data = json.load(mod_path.open())
        return _buildz_mod_schema.validate(data)
    except:
        raise ValueError('get_buildz_mod(): Could not serialize or validate module {}.'.format(mod_name))

def get_buildz_conf():
    buildz_path = Path('buildz.json')

    if not buildz_path.is_file():
        raise FileNotFoundError('get_buildz(): Not found buildz.json config.')

    try:
        data = json.load(buildz_path.open())
        return _buildz_schema.validate(data)
    except Exception as e:
        raise ValueError('get_buildz(): Could not serialize or validate buildz config.', e)

def get_dicts_with_value(dict_, label, value):
    return [x for x in dict_ if label in x and x[label] == value]

def append_unique_dict_to_list(lst, key, value):
    key_val = value[key]

    # find iterators of duplicates
    dupl_it = []
    for it, elem in enumerate(lst):
        if elem.get(key) == key_val:
            dupl_it.append(it)

    # remove duplicates from end to begin
    dupl_it.sort(reverse=True)
    for it in dupl_it:
        del lst[it]

    lst.append(value)
    return

def merge(a, b, str_separator=None):
    if type(a) != type(b):
        raise TypeError

    if isinstance(a, (tuple, list)):
        return a + b
    if isinstance(a, dict):
        out = deepcopy(a)

        for key in b.keys():
            if key in a:
                out[key] = merge(a[key], b[key], str_separator=str_separator)
            else:
                out[key] = b[key]
    if isinstance(a, str):
        if str_separator:
            return str(a + str_separator + b)
        else:
            return b
    if isinstance(a, (int, float, complex)):
        return b
    return b

def merge_envs(tch_env, mod_env, trg_env, env_sch_val):
    env_sch = Schema(env_sch_val)

    try:
        temp_env = merge(tch_env, mod_env)
        temp_env = merge(temp_env, trg_env)
    except:
        temp_env = tch_env

    return env_sch.validate(temp_env)

def get_cmd_matches(args, pattern, stdin=None):
    proc = subprocess.run(args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , text=True)
    
    if proc.returncode != 0:
        return None

    return re.findall(pattern, proc.stdout, re.M)

def find_re_it_in_list(pattern, input, start=0, stop=-1, flags=0):
    length = len(input)
    
    if length == 0:
        return None

    end_it = max(0, length - 1)

    if start >= end_it:
        return None

    if stop<0:
        stop = length

    if stop <= start:
        return None

    for it in range(max(0, start), min(stop, length)):
        elem = input[it]
        match = re.match(pattern, elem, flags)
        if match:
            return it

def route_args(next_args, route, class_instance=None):
        if type(route) is types.FunctionType:
            if class_instance:
                route(class_instance, *next_args)
            else:
                route(*next_args)
            return
        if type(route) is types.MethodType:
            route(class_instance, *next_args)
            return

        if len(next_args) < 1:
            return

        way_name = next_args[0]
        way = route.get(way_name)

        if way is None:
            return

        next_args = next_args[1:]

        if type(way) is types.FunctionType:
            if class_instance:
                way(class_instance, *next_args)
            else:
                way(*next_args)
            return
        if type(way) is types.MethodType:
            way(*next_args)
            return
        if type(way) is dict:
            route_args(next_args, way, class_instance)
