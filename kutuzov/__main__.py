import argparse
import json
import sys

import kutuzov


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('modules', nargs='+')
    parser.add_argument(
        '-f', 
        '--flavor',
        default='sphinx',
        choices=('sphinx', 'gensim'),
        help='The docstring flavor to expect.',
    )
    args = parser.parse_args()

    info = []
    for m in args.modules:
        info.extend(kutuzov.probe_module(m, flavor=args.flavor))

    json.dump(info, sys.stdout, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
