import json
import subprocess
import re

def get_module_conf(module):
    return json.load(open('./{}/module.json'.format(module)))

def get_build_conf():
    return json.load(open('./buildz.json'))

def get_dict_with_value(dict_, label, value):
    return [x for x in dict_ if x[label] == value]

def nodupl_append_dict_to_list(lst, label, value):
    val_key = value[label]
    lst.clear()
    for e in lst
    


def get_cmd_matches(args, pattern, stdin=None):
    proc = subprocess.run(args, 
    stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , text=True)
    
    if proc.returncode != 0:
        return None

    return re.findall(pattern, proc.stdout, re.M)