import json
import re
import subprocess
import types
from copy import deepcopy
from pathlib import Path

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
        return out
    if isinstance(a, str):
        if str_separator:
            return str(a + str_separator + b)
        else:
            return b
    if isinstance(a, (int, float, complex)):
        return b
    return b

def merge_envs(tch_env, mod_env, trg_env, envsch):
    try:
        temp_env = merge(tch_env, mod_env)
        temp_env = merge(temp_env, trg_env)
    except:
        temp_env = tch_env

    return envsch.validate(temp_env)

def resolve_rel_paths_list(pthstr_list, parent_dirstr):
    parent_dir = Path(parent_dirstr)
    out_list = []

    for pthstr in pthstr_list:
        pth = Path(pthstr)
        
        if pth.is_absolute():
            out_list.append(str(pth))

        pth = parent_dir / pth
        pth.resolve()
        out_list.append(str(pth))

    return out_list

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
            route(*next_args)
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
