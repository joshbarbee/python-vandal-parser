import argparse
from analyzer.manager import VandalManager


parser = argparse.ArgumentParser(description='Vandal Python Analyzer')

parser.add_argument('action', help='Whether to run once and output to file or run continuously', choices=['cli', 'file'])
parser.add_argument('--config', help='Config file')
parser.add_argument('--ipc', help='Path to Geth IPC socket', default='/tmp/geth.ipc')
parser.add_argument('--heuristic', help='Heuristic to run. If not specified, all heuristics will be run')

cli_group = parser.add_argument_group('Continuous Options')
cli_group.add_argument('--block', help='Block to start from', default='latest')

file_group = parser.add_argument_group('One-shot Options')
file_group.add_argument('--output', help='Output directory', default='output/')
file_group.add_argument('--tx', help='Transaction hash to analyze')

args = parser.parse_args()

if args.action == 'cli':
    manager = VandalManager(args.ipc, args.block)
    
    try:
        manager.run_cli(args.block)
    except KeyboardInterrupt:
        manager.stop()
        print('Exiting...')
if args.action == 'file' and args.tx:
    manager = VandalManager(args.ipc, args.block, args.output)
    manager.run_file(args.tx, args.output, args.heuristic)
    print('Analysis complete')