from schema import Schema, Or

class Build():
    _schema_val = {
        'type': Or('release', 'debug'),
        'targets': Or('all', [str])
    }

    _schema = Schema(_schema_val)

    def __init__(self, params):
        vd = self._schema.validate(params)

        self.type = vd['type']
        self.targets = vd['targets']