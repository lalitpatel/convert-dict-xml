# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pydict2xml** — a Python library that converts dicts to XML (`Dict2XML`) and XML back to dicts (`XML2Dict`) using lxml. PyPI package name: `pydict2xml`, import name: `pydict2xml`.

## Commands

```bash
pip install -e ".[dev]"       # Install in development mode
pytest                        # Run all tests
pytest tests/test_dict2xml.py # Run Dict2XML tests only
pytest -k test_bool_true      # Run a single test by name
python -m build               # Build sdist and wheel into dist/
twine check dist/*            # Validate package metadata
```

## Architecture

- `src/pydict2xml/__init__.py` — single version source (`__version__`), re-exports `Dict2XML` and `XML2Dict`
- `src/pydict2xml/dict2xml.py` — `Dict2XML` class: recursively converts a dict to an `lxml.etree.Element`. Special dict keys: `@attributes`, `@text`, `@cdata`. Lists become sibling elements. `force_cdata` wraps all text in CDATA.
- `src/pydict2xml/xml2dict.py` — `XML2Dict` class: parses XML into a dict. Single-child lists are flattened. Text-only dicts are collapsed to strings. Supports `ordered_dict=True` and `strip_namespaces=True`.
- Build system: hatchling (configured in `pyproject.toml`), version read dynamically from `__init__.py`

## Key Conventions

- Dict2XML shallow-copies each dict level before popping `@attributes`, `@text`, `@cdata` — input dicts are not mutated
- `_serialize_value` handles bool→"true"/"false", None→"", datetime→isoformat
- XML2Dict flattens single-element lists and text-only dicts automatically
