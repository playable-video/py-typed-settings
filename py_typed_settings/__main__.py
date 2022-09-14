#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from argparse import ArgumentParser
from ast import parse
from os import environ, path
from sys import version_info

from py_typed_settings.settings_schema_gen import update_settings

if version_info[0] == 2:
    from itertools import ifilter as filter

# From https://github.com/Suor/funcy/blob/0ee7ae8/funcy/funcs.py#L34-L36
def rpartial(func, *args):
    """Partially applies last arguments."""
    return lambda *a: func(*(a + args))


with open(path.join(path.dirname(__file__), "__init__.py")) as f:
    __description__ = (lambda const: const.value if version_info > (3, 6) else const.s)(
        parse(
            "".join(filter(rpartial(str.startswith, "__description__"), f.readlines()))
        )
        .body[0]
        .value
    )


def is_valid_file(parser, arg):
    return arg if path.isfile(arg) else parser.error("FileNotFound {}".format(arg))


def _build_parser():
    """
    Parser builder

    :returns: instanceof ArgumentParser
    :rtype: ```ArgumentParser```
    """
    parser = ArgumentParser(description=__description__)
    parser.add_argument(
        "--version",
        action="version",  # version="%(prog)s {}".format(__version__)
    )

    parser.add_argument(
        "-i",
        "--input-yaml",
        help="settings.yaml (input) filepath",
        type=lambda x: is_valid_file(parser, x),
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-py",
        help="settings.py (output) filepath",
        type=str,
        required=True,
    )

    return parser


def main(cli_argv=None, return_args=False):
    """
    Run the CLI parser

    :param cli_argv: CLI arguments. If None uses `sys.argv`.
    :type cli_argv: ```Optional[List[str]]```

    :param return_args: Primarily use is for tests. Returns the args rather than executing anything.
    :type return_args: ```bool```

    :returns: the args in dict form if return_args else `update_settings` return type
    :rtype: ```Optional[dict]```
    """
    _parser = _build_parser()
    args = _parser.parse_args(args=cli_argv)
    if return_args:
        return args
    return update_settings(
        input_yaml=args.input_yaml,
        to_py=args.output_py,
        tier=environ.get("TIER", "dev"),
    )


def entrypoint():
    """
    Run entrypoint when `__name__` is `"__main__"`
    """
    if __name__ == "__main__":
        main()


entrypoint()
