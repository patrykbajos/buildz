import json
import platform

from buildz.toolchain.factory import factory_named_toolchain
from buildz.utils import (get_buildz_conf, get_dicts_with_value,
                          append_unique_dict_to_list)


class VSCodeFrontend():
    __vsc_plat_dict = {
        'Linux': 'Linux',
        'Darwin': 'Mac',
        'Windows': 'Win32'
    }

    __tasks_path = '.vscode/tasks.json'
    __cpp_prop_path = '.vscode/c_cpp_properties.json'

    def __init__(self):
        plat_sys = platform.system()
        self.__vsc_sys_name = self.__vsc_plat_dict.get(plat_sys)

        if not self.__vsc_sys_name:
            raise OSError('Unsupported system platform: {}, supported: {}.'.format(plat_sys, list(self.__vsc_plat_dict)))

        tasks_file = open(self.__tasks_path, 'r')
        prop_file = open(self.__cpp_prop_path, 'r')
        self.__tasks_dict = json.load(tasks_file)
        self.__prop_dict = json.load(prop_file)
        
        tasks_file.close()
        prop_file.close()
        return

    def __save_tasks_file(self):
        tasks_file = open(self.__tasks_path, 'w')
        json.dump(self.__tasks_dict, tasks_file, indent=4)
        tasks_file.close()

    def update_tasks(self):
        try:
            bz_conf = get_buildz_conf()
        except Exception as e:
            print('VSCodeFrontend.update_tasks(): Error getting buildz config.\n', e)
            return

        trgs = bz_conf['targets']
        tchs = bz_conf['toolchains']

        build_task = {
            'label': 'BuildZ Build',
            'type': 'shell',
            'command': 'python -m buildz build',
            'problemMatcher': []
        }

        upd_task = {
            'label': 'BuildZ Update Tasks',
            'type': 'shell',
            'command': 'python -m buildz vscode update tasks',
            'problemMatcher': []
        }

        sel_tasks = []
        for trg_name, trg in trgs.items():
            tch_handle = factory_named_toolchain(trg['toolchain'], tchs)
            sel_trg_params = tch_handle.gen_task_params(trg_name, trg)
            sel_params_str = ' '.join(sel_trg_params)

            sel_task = {
                'label': 'BuildZ Select Task ' + sel_params_str,
                'type': 'shell',
                'command': 'python -m buildz select ' + sel_params_str,
                'problemMatcher': []
            }
            sel_tasks.append(sel_task)

        tasks_list = self.__tasks_dict.get('tasks', [])

        # TODO task list changing check

        append_unique_dict_to_list(tasks_list, 'label', build_task)
        append_unique_dict_to_list(tasks_list, 'label', upd_task)
        for sel_task in sel_tasks:
            append_unique_dict_to_list(tasks_list, 'label', sel_task)

        self.__save_tasks_file()
        return

    def select_target(self, trg_name, *trg_args):
        cpp_prop = self.__prop_dict
        bz_conf = get_buildz_conf()

        confs = cpp_prop['configurations']

        trg_conf = bz_conf['targets'][trg_name]
        tch_name = trg_conf['toolchain']
        tchs = bz_conf['toolchains']

        tch_handler = factory_named_toolchain(tch_name, tchs)

        defines = tch_handler.get_defines(env)
        includes = tch_handler.get_includes(env)

        
        # TODO target selection


        return

    _route = {
        'update': {
            'tasks': update_tasks
        },
        'select': {
            'target': select_target
        }
    }


