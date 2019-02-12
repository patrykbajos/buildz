from schema import Schema, Optional

class Toolchain():
    _schema = Schema({
        'type': str,
        'output_dir': str,
        'output_pattern': str,
        'conf': {
            Optional(str): object
        },
        'env': {
            Optional(str): object
        }
    })

    def __init__(self, name, params):
        vd = self._schema.validate(params)

        self.name = name
        self.type = vd['type']
        self.output_dir = vd['output_dir']
        self.output_pattern = vd['output_pattern']
        self.conf = vd['conf']
        self.env = vd['env']

        
        