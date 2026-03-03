import datetime
from collections import OrderedDict

from lxml import etree

from pydict2xml import Dict2XML


def _xml_string(root_name, data, force_cdata=False):
    """Helper to get XML string without declaration."""
    return Dict2XML(root_name, data, force_cdata=force_cdata).to_xml_string(
        xml_declaration=False, pretty_print=False
    ).decode("UTF-8")


class TestEmptyDict:
    def test_empty_dict(self):
        result = _xml_string("books", {})
        assert result == "<books/>"


class TestTextValues:
    def test_direct_text(self):
        result = _xml_string("book", {"@text": 1984})
        assert result == "<book>1984</book>"

    def test_child_text(self):
        result = _xml_string("books", {"book": 1984})
        assert result == "<books><book>1984</book></books>"


class TestCdata:
    def test_cdata_key(self):
        result = _xml_string("title", {"@cdata": "Foundation"})
        assert "<![CDATA[Foundation]]>" in result

    def test_force_cdata(self):
        result = _xml_string("book", {"@text": "1984"}, force_cdata=True)
        assert "<![CDATA[1984]]>" in result


class TestAttributes:
    def test_attributes_only(self):
        data = {"@attributes": {"type": "fiction", "year": 2011, "bestsellers": True}}
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["type"] == "fiction"
        assert root.attrib["year"] == "2011"
        assert root.attrib["bestsellers"] == "true"

    def test_attributes_with_text(self):
        data = {"@attributes": {"type": "fiction"}, "@text": 1984}
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["type"] == "fiction"
        assert root.text == "1984"

    def test_attributes_with_child(self):
        data = {"@attributes": {"type": "fiction"}, "book": 1984}
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["type"] == "fiction"
        assert root.find("book").text == "1984"


class TestChildren:
    def test_nested_children(self):
        data = {"@attributes": {"type": "fiction"}, "book": 1984}
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        assert root.find("book").text == "1984"

    def test_list_children(self):
        data = {
            "@attributes": {"type": "fiction"},
            "book": ["1984", "Foundation", "Stranger in a Strange Land"],
        }
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        books = root.findall("book")
        assert len(books) == 3
        assert books[0].text == "1984"
        assert books[1].text == "Foundation"
        assert books[2].text == "Stranger in a Strange Land"


class TestSerialization:
    def test_bool_true(self):
        data = {"@attributes": {"available": True}}
        result = _xml_string("book", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["available"] == "true"

    def test_bool_false(self):
        data = {"@attributes": {"available": False}}
        result = _xml_string("book", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["available"] == "false"

    def test_none_value(self):
        data = {"@attributes": {"available": None}}
        result = _xml_string("book", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["available"] == ""

    def test_datetime(self):
        dt = datetime.datetime(2023, 6, 15, 12, 30, 0)
        data = {"@text": dt}
        result = _xml_string("timestamp", data)
        assert "2023-06-15T12:30:00" in result


class TestComplexExample:
    def test_ordered_dict_books(self):
        data = OrderedDict(
            {
                "@attributes": {"type": "fiction"},
                "book": [
                    {
                        "@attributes": {
                            "author": "George Orwell",
                            "available": None,
                        },
                        "title": "1984",
                        "isbn": 973523442132,
                    },
                    {
                        "@attributes": {
                            "author": "Isaac Asimov",
                            "available": False,
                        },
                        "title": {"@cdata": "Foundation"},
                        "price": "$15.61",
                        "isbn": 57352342132,
                    },
                    {
                        "@attributes": {
                            "author": "Robert A Heinlein",
                            "available": True,
                        },
                        "title": {"@cdata": "Stranger in a Strange Land"},
                        "price": {
                            "@attributes": {"discount": "10%"},
                            "@text": "$18.00",
                        },
                        "isbn": 341232132,
                    },
                ],
            }
        )
        result = _xml_string("books", data)
        root = etree.fromstring(result.encode())
        assert root.attrib["type"] == "fiction"
        books = root.findall("book")
        assert len(books) == 3
        assert books[0].attrib["author"] == "George Orwell"
        assert books[0].attrib["available"] == ""
        assert books[1].attrib["available"] == "false"
        assert books[2].attrib["available"] == "true"
        assert books[2].find("price").attrib["discount"] == "10%"
        assert books[2].find("price").text == "$18.00"


class TestEtreeObject:
    def test_get_etree_object(self):
        d = Dict2XML("root", {"child": "value"})
        obj = d.get_etree_object()
        assert isinstance(obj, etree._Element)
        assert obj.tag == "root"


class TestXmlDeclaration:
    def test_with_declaration(self):
        result = Dict2XML("root", {}).to_xml_string(xml_declaration=True).decode("UTF-8")
        assert result.startswith("<?xml")

    def test_without_declaration(self):
        result = Dict2XML("root", {}).to_xml_string(xml_declaration=False).decode("UTF-8")
        assert not result.startswith("<?xml")
