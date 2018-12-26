from schema import Schema, SchemaError

class GenericToolchain():
    _env_sch_val = {}
    _conf_sch_val = {}

    def _set_env(self, env):
        try:
            env_sch = Schema(self._env_sch_val)
            self._env = env_sch.validate(env)
        except SchemaError as e:
            print('AbstractToolchain._set_env(): Error validating env.\n', e)
            self._env = {}
            raise ValueError("AbstractToolchain._set_env(): Invalid env.")
        return

    def _set_conf(self, conf):
        try:
            conf_sch = Schema(self._conf_sch_val)
            self._conf = conf_sch.validate(conf)
        except SchemaError as e:
            print('AbstractToolchain._set_conf(): Error setting conf.\n', e)
            self._conf = {}
            raise ValueError('AbstractToolchain._set_conf: Invalid conf.')
        return