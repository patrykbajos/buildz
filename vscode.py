import platform
import json

class VSCode():
    system_dict = {
        'Linux': 'Linux',
        'Darwin': 'Mac',
        'Windows': 'Win32'
    }

    def __init__(self):
        tasks_file = open('./.vscode/tasks.json', 'r+')
        prop_file = open('./.vscode/c_cpp_properties.json', 'r+')

        sys = platform.system()

        if not sys in self.system_dict:
            print('Unsupported platform system: {}'.format(sys))
            exit

        self.conf_name = self.system_dict[sys]

        self.tasks_json = json.load(tasks_file)
        self.props = json.load(prop_file)

    def save_tasks(self):
        tasks_file = open('./.vscode/tasks.json', 'w')
        json.dump(self.tasks_json, tasks_file, indent=4)
