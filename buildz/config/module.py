from pathlib import Path
from schema import Schema, Optional
import json

class Module():
    _schema = Schema({
        "files": [],
        "envs": {
            Optional(str): {
                Optional(str): object
            }
        },
        "packaging": str
    })

    def __init__(self, name, params):
        vd = self._schema.validate(params)

        self.name = name
        self.abspath = Module.abs_path(name)
        self.absdir = self.abspath.parent
        self.filename = self.abspath.name

        self.files = vd['files']
        self.envs = vd['envs']
        self.packaging = vd['packaging']

    def env(self, name):
        return self.envs.get(name, {})

    @classmethod
    def abs_path(self, mod_name):
        mod_path = Path(mod_name + '/module.json')

        if not mod_path.is_file():
            raise FileNotFoundError('Module.abs_path(): Could not find module {}.'.format(mod_name))

        return mod_path.resolve()

    @classmethod
    def from_file(self, mod_name):
        path = Module.abs_path(mod_name)

        try:
            data = json.load(path.open())
            return Module(mod_name, data)
        except:
            raise ValueError('Module.from_file(): Could not serialize or validate module {}. Expected path: {}'.format(mod_name, path))


