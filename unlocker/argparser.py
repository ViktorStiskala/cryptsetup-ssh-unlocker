import argparse

parser = argparse.ArgumentParser(description='''
    Cryptsetup SSH server unlocker.
    This utility is repeatedly polling configured servers and tries to unlock the encrypted root partition using cryptsetup once the SSH connection is available.
''')

parser.add_argument('-c', '--config', required=False, default='config.ini', help='Path to config file - defaults to config.ini')
parser.add_argument('-v', '--verbose', required=False, action='store_true', help='Increase verbosity level to DEBUG')
parser.add_argument('--logfile', required=False, help='Path to log file. By default the log messages are printed to stderr')
