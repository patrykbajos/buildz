from buildz.toolchain.avrgcc import AvrGccToolchain
from buildz.toolchain.gcc import GccToolchain

import json
import subprocess
import re
from pathlib import Path
from schema import Schema, SchemaError, Optional, And, Or, Use
from os import getcwd

_buildz_mod_schema = Schema({
    "files": [str],
    Optional("env"): {
        str: {}
    }
})

_buildz_schema = Schema({
    "build": {
        "build_type": ["release", "debug"],
        "targets": Or("all", [str]),
        "includes": [str]
    },
    "modules": [str],
    "toolchains": {
        str: {
            "type": str,
            "output_pattern": str, 
            Optional('env'): {},
            Optional('conf'): {}
        }
    },
    "targets": {
        str: {
            "modules": Or(str, [str]),
            "toolchain": str,
            Optional("env"): {}
        }
    }
})

def get_buildz_mod(mod_name):
    cwd = Path(getcwd())

    path_inglobal = Path('modules/{}.json'.format(mod_name))
    path_inmoddir = Path('{}/module.json'.format(mod_name))
    conf_path = Path()

    if path_inglobal.is_file():
        conf_path = path_inglobal
    elif path_inmoddir.is_file():
        conf_path = path_inmoddir
    else:
        raise FileNotFoundError('get_buildz_mod(): Could not find module {}.'.format(mod_name))

    try:
        data = json.load(conf_path.open())
        return _buildz_mod_schema.validate(data)
    except:
        raise ValueError('get_buildz_mod(): Could not serialize or validate module {}.'.format(mod_name))

def get_buildz_conf():
    buildz_path = Path('buildz.json')

    if not buildz_path.is_file():
        raise FileNotFoundError("get_buildz(): Not found buildz.json config.")

    try:
        data = json.load(buildz_path.open())
        return _buildz_schema.validate(data)
    except:
        raise ValueError('get_buildz(): Could not serialize or validate buildz config.')

def get_dicts_with_value(dict_, label, value):
    return [x for x in dict_ if label in x and x[label] == value]

def nodupl_append_dict_to_list(lst, key, value):
    key_val = value[key]

    # find iterators of duplicates
    dupl_i = []
    for i in range(len(lst)):
        elem = lst[i]
        if key in elem:
            if elem[key] == key_val:
                dupl_i.append(i)

    # remove duplicates from end to begin
    dupl_i.sort(reverse=True)
    for i in dupl_i:
        lst.remove(i)

    lst.append(value)
    return

def merge(a, b, str_separator=None):
    if type(a) != type(b):
        raise TypeError

    if isinstance(a, (tuple, list)):
        return a + b
    if isinstance(a, dict):
        out = a.copy()

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

def get_cmd_matches(args, pattern, stdin=None):
    proc = subprocess.run(args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , text=True)
    
    if proc.returncode != 0:
        return None

    return re.findall(pattern, proc.stdout, re.M)

def factory_toolchain(tch_name, tch_dict):
    tch = tch_dict.get(tch_name)

    if tch is None:
        raise KeyError('Missing toolchain {} in toolchains.'.format(tch_name))

    if tch.type == 'GccToolchain':
        return GccToolchain(tch.conf, tch.env)
    if tch.type == 'AvrGccToolchain':
        return AvrGccToolchain(tch.conf, tch.env)
        
    raise ValueError('Unknown toolchain type {} in toolchain {}.'.format(tch.type, tch_name))
