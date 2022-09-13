py_typed_settings
=================
![Python version range](https://img.shields.io/badge/python-2.7%20|%203.6%20|%203.7%20|%203.8%20|%203.9%20|%203.10%20|%203.11.0b5-blue.svg)
[![License](https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Generate typed settings.py from settings.yaml in Python 2, 3.

Useful for fully type-safe settings, with code-completion. E.g., `import settings; print(settings.AWS.bucket.value)`

## Example YAML input

```yaml
constants:
  - name: cors_origin
    dev:
      origins:
        - 'http://localhost:8080'
        - '*'
    remote-dev:
      origins:
        - 'https://api-dev.example.com'
    prod:
      origins:
        - 'https://api.example.com'

providers:
  - provider: aws
    dev:
      bucket:
        value: bucket-dev
    remote-dev:
      bucket:
        value: bucket-dev
    prod:
      bucket:
        value: bucket-prod
```

## Example output (Python 2.7)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GENERATED! Do not manually edit. Modify 'settings.yaml' instead (then run `./settings_schema_gen.py`)
# (different tiers can be targeted with this script by setting the `TIER` env var; defaults to 'dev')

from typing import List, Tuple, Union


#############
# Providers #
#############


class AWS(object):
    class bucket(object):
        value = 'bucket-dev'  # type: str


#############
# Constants #
#############


class CORS_ORIGIN(object):
    origins = 'http://localhost:8080', '*'  # type: Tuple[str]


__all__ = ['AWS', 'CORS_ORIGIN']  # type: List[str]
```

## Example output (Python 3)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GENERATED! Do not manually edit. Modify 'settings.yaml' instead (then run `./settings_schema_gen.py`)
# (different tiers can be targeted with this script by setting the `TIER` env var; defaults to 'dev')

from typing import List, Tuple, Union


#############
# Providers #
#############


class AWS(object):
    class bucket(object):
        value: str = 'bucket-dev'


#############
# Constants #
#############


class CORS_ORIGIN(object):
    origins: Tuple[str] = ('http://localhost:8080', '*')


__all__: List[str] = ['AWS', 'CORS_ORIGIN']
```

## Install dependencies

    pip install -r requirements.txt

## Install package

    pip install .
