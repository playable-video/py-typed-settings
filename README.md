py_typed_settings
=================
![Python version range](https://img.shields.io/badge/python-2.7%20|%203.6%20|%203.7%20|%203.8%20|%203.9%20|%203.10%20|%203.11.0b5-blue.svg)
[![License](https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Generate typed settings.py from settings.yaml in Python 2, 3.

Useful for fully type-safe settings, with code-completion. E.g., `import settings; print(settings.AWS.bucket.value)`

## Command-line usage

```shell
usage: py_typed_settings [-h] [--version] -i INPUT_YAML -o OUTPUT_PY

Generate typed settings.py from settings.yaml in Python 2, 3

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -i INPUT_YAML, --input-yaml INPUT_YAML
                        settings.yaml (input) filepath
  -o OUTPUT_PY, --output-py OUTPUT_PY
                        settings.py (output) filepath
```

### Example
```shell
python -m py_typed_settings -i py_typed_settings/_data/settings.yaml -o py_typed_settings/settings_gen.py
```

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

## Developer

### Install dependencies

    python -m pip install -r requirements.txt

### Install package

    python -m pip install .

## End user

    python -m pip install https://api.github.com/repos/SamuelMarks/py-typed-settings/zipball/annotating#egg=py_typed_settings

---

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <https://opensource.org/licenses/MIT>)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
