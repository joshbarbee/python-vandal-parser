import argparse
from pyanalyze.manager import VandalManager
from pyanalyze.heuristics.load_heuristics import get_heuristics
from logging import getLogger, basicConfig, INFO

basicConfig(level=INFO)

logger = getLogger(__name__)

parser = argparse.ArgumentParser(description="Vandal Python Analyzer")

parser.add_argument(
    "action",
    help="Whether to run once and output to file or run continuously",
    choices=["cli", "file"],
)
parser.add_argument("--config", help="Config file")
parser.add_argument("--ipc", help="Path to Geth IPC socket", default="/tmp/geth.ipc")
parser.add_argument(
    "--heuristics", help="Heuristics to run. If not specified, all heuristics will be run. Separate multiple heuristics with a comma"
)
parser.add_argument("--heuristic-dir", help="Directory to load custom heuristics from")

cli_group = parser.add_argument_group("Continuous Options")
cli_group.add_argument("--block", help="Block to start from", default="latest")
file_group = parser.add_argument_group("One-shot Options")
file_group.add_argument(
    "--output",
    help="Output directory. If not set, heuristic output is just to stdout",
)
file_group.add_argument("--tx", help="Transaction hash to analyze")

args = parser.parse_args()

if args.heuristics and args.heuristic_dir:
    heuristics = get_heuristics(args.heuristics, args.heuristic_dir)
elif args.heuristics:
    heuristics = get_heuristics(args.heuristics)
else:
    heuristics = get_heuristics()

if args.action == "file" and not args.tx:
    parser.error("--tx is required when running in file mode")

if args.action == "cli":
    logger.info("Starting Vandal Analyzer in CLI mode")

    if args.block != 'latest':
        args.block = int(args.block)

    manager = VandalManager(args.ipc, args.block)

    for heuristic in heuristics:
        h = heuristic()
        manager.register_heuristic(h)

    try:
        manager.run_cli(args.block)
    except KeyboardInterrupt:
        logger.info("Exiting...")
        manager.stop()
       
if args.action == "file" and args.tx:
    logger.info("Starting Vandal Analyzer in file mode")
    manager = VandalManager(args.ipc, args.block, args.output)

    for heuristic in heuristics:
        h = heuristic()
        manager.register_heuristic(h)

    manager.run_file(args.tx)
    logger.info("Analysis complete")
