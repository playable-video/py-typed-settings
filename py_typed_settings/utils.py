# -*- coding: utf-8 -*-

"""
Utility functions
"""

from __future__ import print_function

from ast import AST, Assign, ClassDef, Load, Name, Num, Store, Str, Tuple
from collections import OrderedDict
from copy import deepcopy
from functools import partial
from importlib import import_module
from operator import itemgetter, methodcaller
from sys import version_info

import yaml
from six import string_types

if version_info[0] == 2:
    from ast import Str as Constant
    from ast import Str as NameConstant
    from itertools import imap as map

    iteritems = methodcaller("iteritems")
else:
    from ast import Constant, NameConstant

    iteritems = methodcaller("items")

unit_types = string_types + (int, float, complex)

PY_GTE_3_8 = version_info[:2] >= (3, 8)
PY_LT_3_9 = version_info[:2] < (3, 9)

# https://restrictedpython.readthedocs.io/en/latest/contributing/changes_from35to36.html
TYPE_ANNOTATE = version_info[:2] >= (3, 6)
if TYPE_ANNOTATE:
    from ast import AnnAssign

maybe_type_comment = {"type_comment": None} if PY_GTE_3_8 else {}


class SingleLineComment(AST):
    def __init__(self, value, *args, **kwargs):
        """
        Construct a single line comment

        :param value: Comment
        :type value: ```str```
        """
        super(SingleLineComment, self).__init__(*args, **kwargs)
        self.value = value


if PY_LT_3_9:
    from astor import SourceGenerator

    class SourceGeneratorWithComments(SourceGenerator):
        def visit_SingleLineComment(self, node):
            self.write(node.value)

    _to_code = partial(
        getattr(import_module("astor"), "to_source"),
        source_generator_class=SourceGeneratorWithComments,
    )
else:
    from ast import _Unparser

    class SourceGeneratorWithComments(_Unparser):
        def visit_SingleLineComment(self, node):
            self.write(node.value)

    def _to_code(ast_obj):
        _unparser = SourceGeneratorWithComments()
        return _unparser.visit(ast_obj)


def to_code(node):
    """
    Convert the AST input to Python source string

    :param node: AST node
    :type node: ```AST```

    :return: Python source
    :rtype: ```str```
    """
    # ^Not `to_code = getattr…` so docstring can be included^
    return _to_code(node)


def assert_f(expr, msg=None):
    if msg is None:
        assert expr
    else:
        assert expr, msg
    return True  # expr


def set_value(value, kind=None):
    """
    Creates a `Constant` on Python >= 3.8 otherwise more specific AST type

    :param value: AST node
    :type value: ```Any```

    :param kind: AST node
    :type kind: ```Optional[Any]```

    :return: Probably a string, but could be any constant value
    :rtype: ```Union[Constant, Num, Str, NameConstant]```
    """
    if (
        value is not None
        and isinstance(value, str)
        and len(value) > 2
        and value[0] + value[-1] in frozenset(('""', "''"))
    ):
        value = value[1:-1]
    elif value in frozenset(("true", "True")):
        value = True
    elif value in frozenset(("false", "FALSE")):
        value = False

    if PY_GTE_3_8:
        return Constant(kind=kind, value=value, constant_value=None, string=None)
    elif isinstance(value, string_types):
        return Str(s=value, constant_value=None, string=None, type_comment=kind)
    elif isinstance(value, (int, float, complex)):
        return Num(n=value, constant_value=None, string=None, type_comment=kind)
    elif isinstance(value, (bool, type(None))):
        return NameConstant(
            value=value,
            constant_value=None,
            string=None,
            type_comment=type(value).__name__,
        )
    else:
        raise TypeError(value)


def generate_tuple(values):
    """
    Generate tuple of scalars with `type_comment`

    :param values: Dictionary with a single key to a collection of values
    :type values: ```Dict[str, Union[list, tuple]]```

    :return: ast.Tuple
    :rtype: ```Tuple```
    """
    keys = tuple(values.keys())
    assert len(keys) == 1
    types = []

    varname = Name(keys[0], Store())
    elts = [
        types.append(type(value).__name__) or set_value(value)
        for value in values[keys[0]]
    ]
    kind = (
        (
            lambda t: "Tuple{}".format(
                "[Union[{}]]".format(",".join(t)) if len(t) > 1 else "[{}]".format(t[0])
            )
        )(sorted(frozenset(types)))
        if types
        else None
    )

    if kind is not None and TYPE_ANNOTATE:
        return AnnAssign(
            annotation=Name(kind, Load()),
            simple=1,
            target=varname,
            value=Tuple(
                ctx=Load(),
                elts=elts,
            ),
            expr=None,
            expr_annotation=None,
            expr_target=None,
        )
    else:
        return Assign(
            targets=[varname],
            value=Tuple(
                ctx=Load(),
                elts=elts,
                type_comment=kind,
            ),
            ctx=Load(),
            lineno=None,
        )


def generate_container(d, name):
    """
    Generate `class` with potentially nested `class`es to represent a dictionary but enable:
    - Code-completion
    - Dot access

    :param d: Dictionary to turn into `class`
    :type d: ```dict```

    :param name: Key to use as `class` name
    :type name: ```str```

    :return: ast.ClassDef
    :rtype: ```ClassDef```
    """

    def one(key_val):
        key, val = key_val
        if isinstance(val, unit_types):
            kind = None if val is None else type(val).__name__
            varname, value = Name(key.replace("-", "_"), Load()), set_value(
                val, kind=kind
            )
            if TYPE_ANNOTATE and kind is not None:
                return AnnAssign(
                    annotation=Name(kind, Load()),
                    simple=1,
                    target=varname,
                    value=value,
                    expr=None,
                    expr_annotation=None,
                    expr_target=None,
                    **maybe_type_comment
                )
            else:
                return Assign(
                    targets=[varname],
                    value=value,
                    expr=None,
                    lineno=None,
                    **maybe_type_comment
                )
        elif isinstance(val, dict):
            return generate_container(val, key)
        elif isinstance(val, (tuple, list)):
            return generate_tuple(d)
        else:
            raise NotImplementedError(type(d).__name__)

    return ClassDef(
        bases=[Name("object", Load())],
        body=list(map(one, iteritems(d))),
        decorator_list=[],
        keywords=[],
        name=name,
        expr=None,
        identifier_name=None,
    )


def list_of_dict_to_classes(list_of_dict, name, all_providers, tier):
    """
    Converts a list of `dict`s into `class`es

    :param list_of_dict: List of dictionaries where all members—except `name`—are to be turned into `class` members
    :type list_of_dict: ```List[dict]``

    :param name: Key to use that will then be used as `class` name
    :type name: ```str``

    :param all_providers: List to accumulate all external `class` names for generating `__all__`
    :type all_providers: ```List[str]```

    :param tier: Tier, defaults to env var TIER if set else 'dev'
    :type tier: ```str```

    :return: Generated `class`es as an iterable
    :rtype: ```Iterable[ClassDef]``
    """

    def get_properties_always_fallback(provider_, tier_):
        """
        `dev` sometimes contains more properties than the current tier… merge here

        :param provider_: dictionary with `tier` keys
        :type provider_: ```dict```

        :param tier_: Tier, always has a `dev` option
        :type tier_: ```Optional[str]```

        :return: dict at tier, potentially merged with the `dev` tier if it has keys not present at non-dev tier
        :rtype: ```dict``
        """
        if tier_ in ("dev", None) or tier not in provider_:
            return provider_["dev"]

        diff_hit = frozenset(provider_[tier].keys()) ^ frozenset(
            provider_["dev"].keys()
        )
        if not diff_hit:
            return provider_[tier]
        d = deepcopy(provider_[tier])
        d.update({k: provider_["dev"][k] for k in diff_hit})
        return d

    return (
        generate_container(
            get_properties_always_fallback(provider, tier),
            name=(lambda s: all_providers.append(s) or s)(provider[name].upper()),
        )
        for provider in sorted(list_of_dict, key=itemgetter(name))
    )


def emit_sorted_yaml(filename, settings):
    """
    Helper function to emit sorted YAML. Only used on-demand.
    """

    def name_first(d, name="name"):
        o = OrderedDict()
        o[name] = d.pop(name)
        o.update(d)
        return o

    settings.update(
        {
            "constants": tuple(
                map(
                    partial(name_first, name="name"),
                    sorted(settings["constants"], key=itemgetter("name")),
                )
            ),
            "providers": tuple(
                map(
                    partial(name_first, name="provider"),
                    sorted(settings["providers"], key=itemgetter("provider")),
                )
            ),
        }
    )

    def ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
        class OrderedDumper(Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()
            )

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwds)

    with open(filename, "wt") as f:
        ordered_dump(settings, stream=f, Dumper=yaml.SafeDumper)
    return f


# reload(settings_gen)  # Ensure you call this after running `update_settings`


__all__ = [
    "to_code",
    "SingleLineComment",
    "list_of_dict_to_classes",
    "TYPE_ANNOTATE",
    "set_value",
]
