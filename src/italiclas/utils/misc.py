"""Misc utilities (local dependencies allowed)."""

import argparse
import logging
from collections.abc import Iterable

from italiclas.config import info
from italiclas.logger import console_handler, logger


# ======================================================================
def common_args(
    arg_parser: argparse.ArgumentParser | None = None,
    description: str = "",
    arguments: Iterable[str] = frozenset(
        ["help", "version", "verbose", "quiet", "log", "force"],
    ),
) -> argparse.ArgumentParser:
    """Handle command-line application arguments.

    Arguments:
        arg_parser: The argument parser.
            If None, initialize a standard argument parser.
        description: The description to use in the help.
            Defaults to "".
        arguments: The arguments to add.
            Defaults to frozenset(
                ["help", "version", "verbose", "quiet", "log", "force"],).


    Returns:
        The enriched argument parser.

    """
    # :: Create Argument Parser
    if arg_parser is None:
        arg_parser = argparse.ArgumentParser(
            description=description,
            epilog=f"v.{info.version} - {info.author}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False,
        )
    # :: Add POSIX standard arguments
    arguments = set(arguments)
    if "help" in arguments:
        arg_parser.add_argument("-h", "--help", action="help")
    if "version" in arguments:
        arg_parser.add_argument(
            "--ver",
            "--version",
            version=(
                f"{info.name} - ver. {info.version}"
                f"\nCopyright (C) {info.year} - {info.author}"
                f"\nLicense: {info.license}"
                f"\n{info.description}"
            ),
            action="version",
        )
    if "verbose" in arguments:
        arg_parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="increase the level of verbosity [%(default)s]",
        )
    if "quiet" in arguments:
        arg_parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="override log/verbose args to suppress logging [%(default)s]",
        )
    # :: Add additional arguments
    if "log" in arguments:
        arg_parser.add_argument(
            "-l",
            "--log",
            metavar="LEVEL",
            default="INFO",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
            type=str.upper,
            help="set the base logging level [%(default)s]",
        )
    if "force" in arguments:
        arg_parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="force new processing [%(default)s]",
        )
    return arg_parser


# ======================================================================
def cli_logging(args: argparse.Namespace, summary: str) -> None:
    """Perform common logging tasks for CLI scripts.

    Args:
        args: The arguments passed to the CLI script.
        summary: The summary of CLI script.

    """
    if args.quiet:
        logger.removeHandler(console_handler)
    else:
        logger.setLevel(getattr(logging, args.log))
        logger.setLevel(logger.getEffectiveLevel() - 5 * args.verbose)
    logger.debug("%s.args=%s", __name__, vars(args))
    logger.info(summary)
