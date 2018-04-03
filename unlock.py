#!/usr/bin/env python

import configparser
import logging

import sys

from unlocker.client import ServerUnlocker
from unlocker.argparser import parser


def main():
    args = parser.parse_args(sys.argv[1:])

    logger = logging.getLogger('unlocker')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler = logging.StreamHandler(sys.stderr) if not args.logfile else logging.FileHandler(args.logfile)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(server)s] %(message)s'))
    logger.addHandler(handler)

    config = configparser.ConfigParser()
    config.read(args.config)
    required_args = ('host', 'port', 'ssh_private_key', 'known_hosts', 'cryptsetup_passphrase')

    if not config.sections():
        sys.stderr.write('No servers specified in the conf file.\n')
        sys.exit(1)

    for section in config.sections():
        for arg in required_args:
            if not config.get(section, arg, fallback=None):
                sys.stderr.write('Invalid configuration. Section [{section}] is missing required argument "{arg}"\n'.format(section=section, arg=arg))
                sys.exit(1)

        # validate port number
        try:
            config.getint(section, 'port', fallback=None)
        except ValueError:
            sys.stderr.write('Invalid configuration. Invalid port config for server [{section}]\n'.format(section=section))
            sys.exit(1)

    unlocker = ServerUnlocker([config[section] for section in config.sections()])
    unlocker.run_forever()


if __name__ == '__main__':
    main()
