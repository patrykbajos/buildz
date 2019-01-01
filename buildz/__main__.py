import sys

from buildz.frontend.buildzself import BuildzSelfFrontend
from buildz.frontend.vscode import VSCodeFrontend
from buildz.toolchain.factory import factory_named_toolchain
from buildz.utils import route_args

def factory_frontend(name):
    if name == 'build':
        return BuildzSelfFrontend()
    if name == 'vscode':
        return VSCodeFrontend()
    return None

def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print('Please specify at least one argument.')
        return 0

    front_name = args[0]
    front_args = args[1:]

    front = factory_frontend(front_name)
    route_args(front_args, front._route)
    return 0

if __name__ == "__main__":
    result = main()
    sys.exit(result)
