from pathlib import Path
from schema import Schema
import json

from buildz.config.build import Build
from buildz.config.toolchain import Toolchain
from buildz.config.target import Target

class BZConfig():
    _schema = Schema({
        'build': Build._schema,
        'modules': [str],
        'toolchains': {
            str: Toolchain._schema
        },
        'targets': {
            str: Target._schema
        }
    })

    def __init__(self, params):
        vd = self._schema.validate(params)

        self.build = Build(vd['build'])
        self.modules = vd['modules']

        tch = self.toolchains = {}
        for tchname, tchparams in vd['toolchains'].items():
            tch[tchname] = Toolchain(tchname, tchparams)

        trg = self.targets = {}
        for trgname, trgparams in vd['targets'].items():
            trg[trgname] = Target(trgname, trgparams)

    def toolchain(self, name):
        return self.toolchains[name]

    def target(self, name):
        return self.targets[name]

    @classmethod
    def from_file(self, name='buildz.json'):
        path = Path(name)

        if not path.is_file():
            raise FileNotFoundError('Config.from_file(): Not found buildz.json config.')

        try:
            data = json.load(path.open())
            return BZConfig(data)
        except Exception as e:
            raise ValueError('Config.from_file(): Could not serialize or validate buildz config.', e)
