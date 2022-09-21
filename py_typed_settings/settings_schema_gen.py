# -*- coding: utf-8 -*-

from __future__ import print_function

from ast import Assign, ImportFrom, List, Load, Module, Name, Store, alias
from itertools import chain
from itertools import imap as map
from os import environ, path
from sys import version_info

import yaml

from py_typed_settings.utils import (
    TYPE_ANNOTATE,
    SingleLineComment,
    list_of_dict_to_classes,
    set_value,
    to_code,
)

if version_info[0] == 2:
    from ast import AST as AnnAssign
else:
    from ast import AnnAssign


def module_from_yaml_at_tier(
    input_yaml, tier, namespace  # =environ.get("TIER", "dev"),
):
    """
    Construct a new settings module (in memory AST)

    :param input_yaml: settings.yaml (input) filepath
    :type input_yaml: ```str```

    :param tier: Tier, defaults to env var TIER if set else 'dev'
    :type tier: ```Optional[str]```

    :param namespace: Environment variable to change `tier`
    :type namespace: ``str``

    :return: Module of settings
    :rtype: ```Module```
    """
    if tier is None:
        tier = environ.get(tier, "dev")
    with open(input_yaml, "rt") as f:
        settings = yaml.safe_load(f)
    all_providers = []
    settings_gen_mod = Module(
        body=list(
            chain.from_iterable(
                (
                    (
                        SingleLineComment("#!/usr/bin/env python\n"),
                        SingleLineComment("# -*- coding: utf-8 -*-\n\n"),
                        SingleLineComment(
                            "# GENERATED! Do not manually edit. "
                            "Modify 'settings.yaml' instead (then run `./{}`)\n".format(
                                path.basename(__file__)
                            )
                        ),
                        SingleLineComment(
                            "# (different tiers can be targeted with this"
                            " script by setting the `{}` env var; defaults to 'dev')\n".format(
                                namespace
                            )
                        ),
                        ImportFrom(
                            module="typing",
                            names=[
                                alias(name="List", asname=None),
                                alias(name="Tuple", asname=None),
                                alias(name="Union", asname=None),
                            ],
                            level=0,
                        ),
                        SingleLineComment(
                            "\n".join(
                                (
                                    "\n",
                                    "#############",
                                    "# Providers #",
                                    "#############\n".format(path.basename(__file__)),
                                )
                            )
                        ),
                    ),
                    list_of_dict_to_classes(
                        settings["providers"], "provider", all_providers, tier
                    ),
                    (
                        SingleLineComment(
                            "\n".join(
                                (
                                    "",
                                    "#############",
                                    "# Constants #",
                                    "#############\n",
                                )
                            )
                        ),
                    ),
                    list_of_dict_to_classes(
                        settings["constants"], "name", all_providers, tier
                    ),
                    (
                        AnnAssign(
                            annotation=Name(
                                "List[str]",
                                Load(),
                            ),
                            simple=1,
                            target=Name("__all__", Store()),
                            value=List(ctx=Load(), elts=[]),
                            expr=None,
                            expr_annotation=None,
                            expr_target=None,
                        )
                        if TYPE_ANNOTATE
                        else Assign(
                            targets=[Name(ctx=Store(), id="__all__")],
                            value=List(
                                ctx=Load(),
                                elts=[],
                                type_comment="List[str]",
                            ),
                            ctx=Load(),
                            lineno=None,
                        ),
                    ),
                )
            )
        ),
        stmt=None,
        type_ignores=[],
    )
    settings_gen_mod.body[-1].value.elts = list(map(set_value, sorted(all_providers)))
    return settings_gen_mod


def update_settings(input_yaml, to_py, tier, namespace):
    """
    Update the settings module by statically code-generating it (to disk)

    :param input_yaml: Input yaml filename
    :type input_yaml: ```str```

    :param to_py: Output python filename
    :type to_py: ```str```

    :param namespace: Environment variable to change `tier`
    :type namespace: ``str``

    :param tier: Tier, defaults to 'dev'
    :type tier: ```str```
    """
    settings_gen_mod = module_from_yaml_at_tier(input_yaml, tier, namespace)

    with open(to_py, "wt") as f:
        f.write(to_code(settings_gen_mod))


__all__ = ["module_from_yaml_at_tier", "to_code", "update_settings"]
