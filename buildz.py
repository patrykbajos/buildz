from pyavrutils import AvrGcc
from buildz_utils import *

cc = AvrGcc()
cc.optimize_for_size()

bc = get_build_conf()
cc.includes = bc.includes
cc.includes.extend(bc.modules)

for target_name in bc.targets:
    cc.mcu = target_name
    print('Processing target {}...'.format(target_name))

    for module in bc.modules:
        print('    processing module {}'.format(module))
        mc = get_module_conf(module)
        files = ['{}/{}'.format(module, f) for f in mc.files]

        for f_cpu in bc.targets[target_name].f_cpus:
            name_params = {
                'module': str(module),
                'build_type': str(bc.build_type),
                'mcu': str(target_name),
                'f_cpu': int(f_cpu)
            }

            cc.output = bc.output_pattern.format(**name_params)
            cc.f_cpu = int(f_cpu)
            print(cc.includes)
            cc.build(files)