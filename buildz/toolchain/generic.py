from schema import Schema, SchemaError


class GenericToolchain():
    _env_sch_val = {}
    _conf_sch_val = {}

    def __init__(self, conf, env):
        self.__env = {}
        self.__conf = {}

        self.env = env
        self.conf = conf

    @property
    def env(self):
        return self.__env

    @env.setter
    def env(self, env):
        try:
            env_sch = Schema(self._env_sch_val)
            self.__env = env_sch.validate(env)
        except SchemaError as e:
            print('AbstractToolchain.env(): Error validating env.\n', e)
            self.__env = {}
            raise ValueError("AbstractToolchain.env(): Invalid env.")

    @property
    def conf(self):
        return self.__conf

    @conf.setter
    def conf(self, conf):
        try:
            conf_sch = Schema(self._conf_sch_val)
            self.__conf = conf_sch.validate(conf)
        except SchemaError as e:
            print('AbstractToolchain.conf(): Error setting conf.\n', e)
            self.__conf = {}
            raise ValueError('AbstractToolchain.conf: Invalid conf.')
