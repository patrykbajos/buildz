from buildz.toolchain.gcc import GccToolchain

from pyavrutils import AvrGcc
from schema import Optional

class AvrGccToolchain(GccToolchain):
    def get_defines(self, flags, mcu, fcpu):
        lflags = []
        if 'flags' in self._env:
            lflags.extend(self._env.get('flags'))
        lflags.extend(flags)
        lflags.append("-mmcu={}".format(mcu))
        lflags.append("-DF_CPU={}".format(fcpu))

        return GccToolchain.get_defines(self, lflags)

    def build_mod(self, mod_name, out_dir, toolchain_name, toolchain, trg_env):

        # TODO: Module relative or abs paths
            files = ['{}/{}'.format(mod_name, fp) for fp in mc.files]

            for f_cpu in trg_env.f_cpus:
                name_params = {
                    'mod': str(module),
                    'build_type': str(bc.build_type),
                    'mcu': str(tg_name),
                    'f_cpu': int(f_cpu)
                }

                cc.output = bc.output_pattern.format(**name_params)
                cc.f_cpu = int(f_cpu)
                print(cc.includes)
                cc.build(files)
    
    def __init__(self, conf, env):
        self._env_sch._schema.update({
            Optional("mcu"): str,
            Optional("fcpu"): [int]
        })
        super().__init__(conf, env)
