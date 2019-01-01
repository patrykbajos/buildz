import json
import platform

from buildz.toolchain.factory import factory_named_toolchain
from buildz.utils import (get_buildz_conf, get_dicts_with_value,
                          nodupl_append_dict_to_list)


class VSCodeFrontend():
    __vsc_sys_name_dict = {
        'Linux': 'Linux',
        'Darwin': 'Mac',
        'Windows': 'Win32'
    }

    tasks_path = '.vscode/tasks.json'
    cpp_prop_path = '.vscode/c_cpp_properies.json'

    def __init__(self):
        tasks_file = open(self.tasks_path, 'r')
        cpp_prop_file = open(self.cpp_prop_path, 'r')

        local_sys_name = platform.system()
        if not local_sys_name in self.__vsc_sys_name_dict:
            print('Unsupported platform system: {}'.format(local_sys_name))
            exit

        self.vsc_sys_name = self.__vsc_sys_name_dict[local_sys_name]
        self.cpp_prop_conf_name = self.vsc_sys_name
        self.tasks_json = json.load(tasks_file)
        self.cpp_prop_json = json.load(cpp_prop_file)
        
        tasks_file.close()
        cpp_prop_file.close()
        return

    def save_tasks_file(self):
        tasks_file = open(self.tasks_path, 'w')
        json.dump(self.tasks_json, tasks_file, indent=4)
        tasks_file.close()

    def gen_tasks(self):
        try:
            build_conf = get_buildz_conf()
        except Exception as exc:
            print('VSCodeFrontend.update_tasks(): Error getting buildz config.\n', exc)
            return

        targets = build_conf['targets']
        toolchains = build_conf['toolchains']

        for trg_name, target in targets.items():
            tch_name = target['toolchain']
            tch_handle = factory_named_toolchain(tch_name, toolchains)

            tasks = self.tasks_json['tasks']

            #TODO update tasks

        self.save_tasks_file()
        return

    def select_target(self, trg_name):
        conf_base = self.cpp_prop_json

        env = conf_base['env']
        confs = conf_base['configurations']

        return

    _route = {
        'update': {
            'tasks': gen_tasks
        },
        'select': {
            'target': select_target
        }
    }


