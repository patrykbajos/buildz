from buildz.utils import get_dicts_with_value, get_buildz_conf, nodupl_append_dict_to_list
from buildz.toolchain.avrgcc import AvrGccToolchain
import platform
import json

class VSCodeFrontend():
    vsc_sys_name_dict = {
        'Linux': 'Linux',
        'Darwin': 'Mac',
        'Windows': 'Win32'
    }

    tasks_file_path = '.vscode/tasks.json'
    cpp_prop_file_path = '.vscode/c_cpp_properies.json'

    def __init__(self):
        tasks_file = open(self.tasks_file_path, 'r')
        cpp_prop_file = open(self.cpp_prop_file_path, 'r')

        local_sys_name = platform.system()
        if not local_sys_name in self.vsc_sys_name_dict:
            print('Unsupported platform system: {}'.format(local_sys_name))
            exit

        self.vsc_sys_name = self.vsc_sys_name_dict[local_sys_name]
        self.cpp_prop_conf_name = self.vsc_sys_name
        self.tasks_json = json.load(tasks_file)
        self.cpp_prop_json = json.load(cpp_prop_file)
        
        tasks_file.close()
        cpp_prop_file.close()
        return

    def save_tasks_file(self):
        tasks_file = open(self.tasks_file_path, 'w')
        json.dump(self.tasks_json, tasks_file, indent=4)
        tasks_file.close()
        return

    def update_tasks(self):
        try:
            build_conf = get_buildz_conf()
        except Exception as exc:
            print('VSCodeFrontend.update_tasks(): Error getting buildz config.\n', exc)
            return

        targets = build_conf['targets']
        toolchains = build_conf['toolchains']

        for target_name, target in targets.items():
            toolchain_name = target['toolchain']
            toolchain = toolchains.get(toolchain_name, None)

            if not toolchain:
                print('VSCodeFrontend.update_tasks(): Target {} uses toolchain {} wich does not exist.')
                break
            
            # toolchain is now safe structure

            toolchain_type = toolchain['type']
            toolchain_handler = None

            if toolchain_type == 'gcc':
                toolchain_handler = GccToolchain(toolchain['env'])
            if toolchain_type == 'avr-gcc':
                toolchain_handler = AvrGccToolchain(toolchain['env'])

            tasks = self.tasks_json['tasks']
            tch_tasks = toolchain_handler.get_select_target_task()

            for fcpu in fcpus:
                task = {}
                label = 'select {} {}'.format(mcu, fcpu)
                cmd = "python3 -m buildz vscode updatetasks \"{}\" {} {}".format(path, mcu, fcpu)
                task["type"] = "shell"
                task["label"] = label
                task["command"] = cmd
                nodupl_append_dict_to_list(tasks, "label", task)

        self.save_tasks_file()
        return

    def select_target(self):
        return

    def run(self, mod_args):
        return