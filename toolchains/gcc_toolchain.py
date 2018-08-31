import subprocess
from buildz_utils import get_cmd_matches

class GccToolchain():
    def get_includes(self, flags):
        args = [self.gcc_path, '-xc', '-E', '-###', '-']
        args.extend(flags)

        pattern = r'^ *LIBRARY_PATH *= *(.*?) *$'
        matches = get_cmd_matches(args, pattern)

        if not isinstance(matches, list):
            return []

        if not matches:
            return []

        # i is : separated string of includes
        i = str(matches[0])
        return i.split(':')

    def get_defines(self, flags):
        # gcc -dM -E - $flags 0</dev/null 
        # avr-gcc -mmcu= -DF_CPU= -dM -E - $flags 0</dev/null 

        args = [self.gcc_path, '-dM', '-E', '-']
        args.extend(flags)
        pattern =  r'^ *#define +(.+?) +(.+?) *$'
        matches = get_cmd_matches(args, pattern, subprocess.DEVNULL)

        if not isinstance(matches, list):
            return []

        if not matches:
            return []

        defines = []
        for m in matches:
            # m is tuple of (defname, defvalue), change it to str defname=defvalue
            if isinstance(m, tuple):
                defines.append('{}={}'.format(m[0], m[1]))

        return defines
    
    def __init__(self, gcc_path):
        self.gcc_path = gcc_path

