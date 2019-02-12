
from schema import Schema, Or, Optional

class Target():
    _schema = Schema({
        'modules': Or('all', []),
        'toolchain': str,
        'env': {
            Optional(str): object
        }
    })

    def __init__(self, name, params):
        vd = self._schema.validate(params)

        self.name = name
        self.modules = vd['modules']
        self.toolchain = vd['toolchain']
        self.env = vd['env']