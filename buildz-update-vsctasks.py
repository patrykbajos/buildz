from buildz_utils import get_dict_with_value, get_build_conf
from vscode import VSCode
from toolchains.avr_gcc_toolchain import AvrGccToolchain

build_conf = get_build_conf()
vsc = VSCode()
targets = build_conf["targets"]
toolchains = build_conf["toolchains"]

for target_name in targets:
    target = targets[target_name]
    toolchain_name = target["toolchain"]
    toolchain = toolchains[toolchain_name]
    
    if toolchain["type"] == "avr-gcc":
        toolchain_variables = target["toolchain_variables"]
        fcpus = toolchain_variables["fcpu"]
        mcu = toolchain_variables["mcu"]
        tasks = vsc.tasks_json["tasks"]

        for fcpu in fcpus:
            task = {}
            label = "select {} {}".format(mcu, fcpu)
            cmd = "python3 -m buildz-select-vsctarget {} {}".format(mcu, fcpu)
            task["type"] = "shell"
            task["label"] = label
            task["command"] = cmd
            tasks.append(task)
vsc.save_tasks()