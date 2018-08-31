from toolchains.gcc_toolchain import GccToolchain

class AvrGccToolchain(GccToolchain):
    def get_includes(self, flags):
        return GccToolchain.get_includes(self, flags)

    def get_defines(self, flags, mcu, fcpu):
        mcu_flag = "-mmcu={}".format(mcu)
        fcpu_flag = "-DF_CPU={}".format(fcpu)
        flags.append(mcu_flag)
        flags.append(fcpu_flag)
        return GccToolchain.get_defines(self, flags)
    
    def get_env_defines(self, flags, env):
        mcu = env["mcu"]
        fcpus = env["fcpu"]

        out = {}
        for fcpu in fcpus:
            out["{}_{}".format(mcu, fcpu)] = self.get_defines(flags, mcu, fcpu)

        return out
