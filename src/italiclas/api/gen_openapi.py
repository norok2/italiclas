#!/usr/bin/env python3
"""Generate OpenAPI specifications."""

import argparse
import functools
import logging
from pathlib import Path
from typing import Literal

from fastapi.openapi.utils import get_openapi

from italiclas.api.main import app
from italiclas.config import info
from italiclas.logger import logger
from italiclas.utils import misc, stopwatch


def gen_openapi_specs(
    ext: Literal["json", "yaml"] = "yaml",
    filename: str = "openapi",
    dirpath: Path = info.base_dir,
    *,
    force: bool = False,
) -> Path:
    """Generate and export OpenAPI specifications.

    Args:
        ext: The OpenAPI extension (and output format).
            Defaults to "json".
        filename: The output file name (without extension).
            Defaults to "openapi".
        dirpath: The output dir path.
            Defaults to info.base_dir.
        force: Force new computation.
            Defaults to False.

    Returns:
        The output filepath.

    Example:
        >>> gen_openapi_specs()  # doctest: +SKIP
        PosixPath('openapi.yaml')

    """
    filepath = dirpath / f"{filename}.{ext}"

    if ext in "json":
        import json

        exporter = functools.partial(json.dump, indent=2)
    elif ext == "yaml":
        import yaml

        exporter = functools.partial(yaml.dump, indent=2)

    if force or not filepath.is_file():
        logger.info("Export OpenAPI specs to '%s'", filepath)
        openapi_specs = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        with filepath.open("w") as file_obj:
            exporter(openapi_specs, file_obj)
    return filepath


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "-e",
        "--ext",
        metavar="EXT",
        type=str,
        help="the output extension [%(default)s]",
        default="yaml",
    )
    arg_parser.add_argument(
        "-o",
        "--filename",
        metavar="NAME",
        type=str,
        help="the output file name [%(default)s]",
        default="openapi",
    )
    arg_parser.add_argument(
        "-d",
        "--dirpath",
        metavar="PATH",
        type=Path,
        help="the working dir [%(default)s]",
        default=info.base_dir,
    )
    return arg_parser


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def main() -> None:
    """Execute main script."""
    # : init args and add common parameters
    arg_parser = misc.common_args(description=__doc__)
    # : add script parameters
    arg_parser = more_args(arg_parser)
    args = arg_parser.parse_args()

    misc.cli_logging(args, __doc__.strip())

    to_skip = {"log", "verbose", "quiet"}
    kws = {
        k: v
        for k, v in vars(args).items()
        if k not in to_skip and v is not None
    }
    gen_openapi_specs(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
