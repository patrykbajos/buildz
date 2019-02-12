from schema import Schema, Or

class Build():
    _schema = Schema({
        'type': Or('release', 'debug'),
        'targets': Or('all', [str])
    })

    def __init__(self, params):
        vd = self._schema.validate(params)

        self.type = vd['type']
        self.targets = vd['targets']