
# BUILDZ

Small build system made for ModularOS project and AVR firmwares.

## Dependencies

* Python 3
Dependent on use:
* gcc `pacman -S gcc` or `apt-get install gcc`
* avr-gcc `pacman -S avr-gcc` or `apt-get install avr-gcc`

## Use

### Main config
The main configration file is `buildz.json`. It must be placed in project root directory.
Structure of the config is:
```json
{
    "build": {
        "type": "",
        "targets": ""
    },
    "modules": [],
    "toolchains": {
        "toolchain": {
            "type": "",
            "output_dir": "build/{build_type}",
            "output_pattern": "{module_name}",
            "conf": {},
            "env": {}
        }
    },
    "targets": {
        "target": {
            "modules": "all",
            "toolchain": "toolchain",
            "env": {
            
            }
        }
    }
}
```
`build.type`: Can be `"release"` or `"debug"` as for now.
`modules`: It is a list of project modules. Module name is equivalent to directory in project root. Module directory must contain `module.json` file.
`toolchains`: Dictionary of toolchains used by project. Dictionary key is used to identify toolchain in config. Toolchain must have:
    `type`: It can be `"GccToolchain"` or `"AvrGccToolchain"`.
    `output_dir`: It can be project relative or absolute path where outputs should be placed. It can use some of variables.
    `output_pattern`: It is output file name pattern. It can use some of variables.
    `conf`: It is compiler config dictionary. It cannot change for all of targets and is dependent on toolchain type.
    `env`: It is compiler config that can change. Can be placed in target, module or toolchain config. Its content depends on toolchain type. It can use some of variables.
    Variables to use in `env`, `output_dir` or in `output_pattern`:
    `build_type`, `target_name`, `target_toolchain`, `module_name`
`targets`: It is dictionary of targets. Key is name of target. Target is corresponding to procesor, platform etc. but can be whathever you wants.
    `modules`: It can be list of modules that can be compiled for target. Additionaly it can be just string `"all"`.
    `toolchain`: It is one of keys from `@buildz.toolchains`.
    `env`: It is target dependent part of compiler env. It can use the same variables as `toolchain.env`. It is compiler specific.


### Module Config file
Must be placed in `{project-root}/{module-name}/module.json`
```json
{
    "files": [],
    "envs": {
        "toolchain": {
        }
    },
    "packaging": ""
}
```
`files`: It is list of module directory relative files or can be an absolute path.
`envs`: Module env can change according to used toolchain. The key of `envs` dict must be one of `{buildz.json}.toolchains` keys.
`packaging`: It is toolchain specific. For GCC and for avr-gcc it can be `executable`, `static` or `shared`.

## Toolchains

### GccToolchain
Conf must be dict of variables such as:
    `gcc_path`: On Linux usually it is `/usr/bin/gcc`. If you have configured OS env it can be just `gcc`.
    `ld_path`: On Linux usually it is `/usr/bin/ld`. If you have configured OS env it can be just `ld`.
    `ar_path`: On Linux usually it is `/usr/bin/ar`. If you have configured OS env it can be just `ar`.

Env variables are:
    `optimization`: Default is `3`. It can be `0`, `1`,`2`,`3` or `"s"`.
    `compiler_flags`: Default is `[]`. It it list of strings, each string per flag.

    `includes`: Default is `[]`. It is list of strings. Strings can be absolute, root relative (if defined in `toolchain.env` or `target.env`) or module relative (if defined in `module.envs`) paths. It can use `env` parameters.
    `defines`: Default is `[]`. It is list of strings. Strings can be absolute, root relative (if defined in `toolchain.env` or `target.env`) or module relative (if defined in `module.envs`) paths. It can use `env` parameters.

    `build_type`: Default is `release`. It can be `release` or `debug`.
    `debug_level`: Default is `None`. It can be `0`, `1`, `None`, `3`.

    `link_flags`: Default is `[]`. It it list of strings, each string per flag.
    `link_dirs`: Default is `[]`. It is list of strings. Strings can be absolute, root relative (if defined in `toolchain.env` or `target.env`) or module relative (if defined in `module.envs`) paths. It can use `env` parameters.
    `link`: Default is `[]`. It is list of strings. Each of string is library name which should be linked.

### AvrGccToolchain
Conf must be dict of variables such as:
    The same as for `GccToolchain`.
Env variables are:
    The same as for `GccToolchain`.
    Additionally they are:
    `mcu`: It is string containing  mcu name.
    `fcpu`: Default is `[1000000]`. It is list of integers. It is use for target compilation.

Additional variables are available for `output_dir` and `output_pattern`. They are:
    `mcu`: string
    `fcpu`: integer
