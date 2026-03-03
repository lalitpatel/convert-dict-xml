# pydict2xml

[![PyPI version](https://img.shields.io/pypi/v/pydict2xml)](https://pypi.org/project/pydict2xml/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydict2xml)](https://pypi.org/project/pydict2xml/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Convert Python dicts to XML and back using [lxml](https://lxml.de/). Supports attributes and CDATA.

## Features

- **Dict to XML** — supports nested dicts, attributes, CDATA sections, and lists of sibling elements
- **XML to Dict** — parse XML back into plain dicts or `OrderedDict`
- **Type serialization** — `bool`, `None`, `datetime` handled automatically
- **Round-trip** — convert dict → XML → dict

## Installation

```bash
pip install pydict2xml
```

> **Note:** Requires [lxml](https://lxml.de/installation.html), which needs `libxml2` and `libxslt` system libraries on some platforms.

## Quick Start

### Dict to XML

```python
from pydict2xml import Dict2XML

data = {
    '@attributes': {'type': 'fiction'},
    'book': ['1984', 'Foundation']
}
xml = Dict2XML('books', data).to_xml_string(xml_declaration=False)
print(xml.decode())
```

```xml
<books type="fiction">
  <book>1984</book>
  <book>Foundation</book>
</books>
```

### XML to Dict

```python
from pydict2xml import XML2Dict

result = XML2Dict(xml).to_dict()
# {'@attributes': {'type': 'fiction'}, 'book': ['1984', 'Foundation']}
```

## Dict Conventions

Use special keys to control XML output:

| Key | Purpose | Example |
|-----|---------|---------|
| `@attributes` | Set XML attributes | `{'@attributes': {'id': '1'}}` → `<node id="1"/>` |
| `@text` | Set text content | `{'@text': 'hello'}` → `<node>hello</node>` |
| `@cdata` | Wrap text in CDATA | `{'@cdata': 'hello'}` → `<node><![CDATA[hello]]></node>` |
| *(list value)* | Sibling elements | `{'item': ['a', 'b']}` → `<item>a</item><item>b</item>` |

Use `force_cdata=True` to wrap **all** text nodes in CDATA sections.

### Text Nodes

Text can be set directly or via `@text`:

```python
books = {'book': 1984}
# or
books = {'book': {'@text': 1984}}
xml = Dict2XML('books', books).to_xml_string(xml_declaration=False)
print(xml.decode())
```

```xml
<books>
  <book>1984</book>
</books>
```

### Attributes

```python
books = {
    '@attributes': {'type': 'fiction'},
    'book': 1984
}
xml = Dict2XML('books', books).to_xml_string(xml_declaration=False)
print(xml.decode())
```

```xml
<books type="fiction">
  <book>1984</book>
</books>
```

### Multiple Children

Lists produce sibling elements with the same tag:

```python
books = {
    '@attributes': {'type': 'fiction'},
    'book': ['1984', 'Foundation', 'Stranger in a Strange Land']
}
xml = Dict2XML('books', books).to_xml_string(xml_declaration=False)
print(xml.decode())
```

```xml
<books type="fiction">
  <book>1984</book>
  <book>Foundation</book>
  <book>Stranger in a Strange Land</book>
</books>
```

### CDATA

```python
books = {
    'book': [
        {'title': '1984', 'isbn': 973534},
        {'title': {'@cdata': 'Foundation'}, 'price': '$15.61', 'isbn': 573234},
    ]
}
xml = Dict2XML('books', books).to_xml_string(xml_declaration=False)
print(xml.decode())
```

```xml
<books>
  <book>
    <isbn>973534</isbn>
    <title>1984</title>
  </book>
  <book>
    <price>$15.61</price>
    <isbn>573234</isbn>
    <title><![CDATA[Foundation]]></title>
  </book>
</books>
```

### Complex Example

```python
from collections import OrderedDict
from pydict2xml import Dict2XML

books = OrderedDict({
    '@attributes': {'type': 'fiction'},
    'book': [
        {
            '@attributes': {'author': 'George Orwell', 'available': None},
            'title': '1984',
            'isbn': 972132,
        },
        {
            '@attributes': {'author': 'Isaac Asimov', 'available': False},
            'title': {'@cdata': 'Foundation'},
            'price': '$15.61',
            'isbn': 5735232,
        },
        {
            '@attributes': {'author': 'Robert A Heinlein', 'available': True},
            'title': {'@cdata': 'Stranger in a Strange Land'},
            'price': {'@attributes': {'discount': '10%'}, '@text': '$18.00'},
            'isbn': 3412332,
        },
    ],
})
xml = Dict2XML('books', books).to_xml_string(xml_declaration=False)
print(xml.decode()
```

```xml
<books type="fiction">
  <book available="" author="George Orwell">
    <isbn>972132</isbn>
    <title>1984</title>
  </book>
  <book available="false" author="Isaac Asimov">
    <price>$15.61</price>
    <isbn>5735232</isbn>
    <title><![CDATA[Foundation]]></title>
  </book>
  <book available="true" author="Robert A Heinlein">
    <price discount="10%">$18.00</price>
    <isbn>3412332</isbn>
    <title><![CDATA[Stranger in a Strange Land]]></title>
  </book>
</books>
```

## API Reference

### `Dict2XML(root_node_name, dictionary, force_cdata=False)`

| Parameter | Description |
|-----------|-------------|
| `root_node_name` | Name of the root XML element |
| `dictionary` | The dict to convert |
| `force_cdata` | Wrap all text nodes in CDATA sections (default `False`) |

| Method | Returns |
|--------|---------|
| `to_xml_string(encoding='UTF-8', pretty_print=True, xml_declaration=True)` | XML as `bytes` |
| `get_etree_object()` | The underlying `lxml.etree.Element` |

### `XML2Dict(xml, ns_clean=True)`

| Parameter | Description |
|-----------|-------------|
| `xml` | XML string or bytes to parse |
| `ns_clean` | Remove namespace prefixes (default `True`) |

| Method | Returns |
|--------|---------|
| `to_dict(ordered_dict=False)` | `dict` (or `OrderedDict` if `ordered_dict=True`) |
| `get_etree_object()` | The underlying `lxml.etree.Element` |

## Contributing

```bash
git clone https://github.com/lalitpatel/dict2xml.git
cd dict2xml
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE) — Copyright (c) 2018 Lalit Patel
