from schema import Schema, SchemaError


class GenericToolchain():
    _envsch = Schema({})
    _confsch = Schema({})

    def __init__(self, tchsetup):
        self.__setup = tchsetup
        self.__valid = self.__validate_setup()

    def __validate_setup(self):
        try:
            self.__setup.env = self._envsch.validate(self.__setup.env)
        except SchemaError as e:
            print('GenericToolchain(): Error validating env.\n', e)
            raise ValueError("AbstractToolchain: Invalid env.")

        try:
            self.__setup.conf = self._confsch.validate(self.__setup.conf)
        except SchemaError as e:
            print('GenericToolchain(): Error validating conf.\n', e)
            raise ValueError('AbstractToolchain.conf: Invalid conf.')

        return True

    def build_mod(self, config, toolchain, module, target):
        pass

    def is_valid(self):
        return self.__valid

    @property
    def setup(self):
        return self.__setup

    @property
    def env(self):
        return self.__setup.env

    @property
    def conf(self):
        return self.__setup.conf
