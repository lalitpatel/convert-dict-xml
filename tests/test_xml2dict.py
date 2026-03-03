from collections import OrderedDict

from lxml import etree

from pydict2xml import XML2Dict


class TestSimpleElements:
    def test_text_only(self):
        xml = b"<book>1984</book>"
        result = XML2Dict(xml).to_dict()
        assert result == "1984"

    def test_empty_element(self):
        xml = b"<book/>"
        result = XML2Dict(xml).to_dict()
        assert result == {}


class TestAttributes:
    def test_attributes_only(self):
        xml = b'<book type="fiction"/>'
        result = XML2Dict(xml).to_dict()
        assert "@attributes" in result
        assert result["@attributes"]["type"] == "fiction"

    def test_attributes_with_text(self):
        xml = b'<book type="fiction">1984</book>'
        result = XML2Dict(xml).to_dict()
        assert result["@attributes"]["type"] == "fiction"
        assert result["@text"] == "1984"


class TestNestedChildren:
    def test_single_child(self):
        xml = b"<books><book>1984</book></books>"
        result = XML2Dict(xml).to_dict()
        assert result["book"] == "1984"

    def test_multiple_children(self):
        xml = b"<books><book>1984</book><book>Foundation</book></books>"
        result = XML2Dict(xml).to_dict()
        assert isinstance(result["book"], list)
        assert len(result["book"]) == 2
        assert result["book"][0] == "1984"
        assert result["book"][1] == "Foundation"


class TestListFlattening:
    def test_single_child_flattened(self):
        xml = b"<books><book>1984</book></books>"
        result = XML2Dict(xml).to_dict()
        # Single child should be flattened (not a list)
        assert result["book"] == "1984"

    def test_multiple_children_kept_as_list(self):
        xml = b"<books><book>A</book><book>B</book><book>C</book></books>"
        result = XML2Dict(xml).to_dict()
        assert isinstance(result["book"], list)
        assert len(result["book"]) == 3


class TestOrderedDict:
    def test_ordered_dict(self):
        xml = b'<book type="fiction">1984</book>'
        result = XML2Dict(xml).to_dict(ordered_dict=True)
        assert isinstance(result, OrderedDict)

    def test_regular_dict(self):
        xml = b'<book type="fiction">1984</book>'
        result = XML2Dict(xml).to_dict(ordered_dict=False)
        assert isinstance(result, dict)
        assert not isinstance(result, OrderedDict)


class TestRoundTrip:
    def test_round_trip(self):
        from pydict2xml import Dict2XML

        original = {
            "@attributes": {"type": "fiction"},
            "book": [
                {"title": "1984", "isbn": "973523442132"},
                {"title": "Foundation", "isbn": "57352342132"},
            ],
        }
        xml_bytes = Dict2XML("books", original.copy()).to_xml_string(xml_declaration=False)
        result = XML2Dict(xml_bytes).to_dict()
        assert result["@attributes"]["type"] == "fiction"
        assert isinstance(result["book"], list)
        assert len(result["book"]) == 2


class TestEtreeObject:
    def test_get_etree_object(self):
        xml = b"<root><child>value</child></root>"
        obj = XML2Dict(xml).get_etree_object()
        assert isinstance(obj, etree._Element)
        assert obj.tag == "root"


class TestComplexXml:
    def test_complex_books(self):
        xml = b"""<books type="fiction">
          <book available="" author="George Orwell">
            <isbn>973523442132</isbn>
            <title>1984</title>
          </book>
          <book available="false" author="Isaac Asimov">
            <price>$15.61</price>
            <isbn>57352342132</isbn>
            <title>Foundation</title>
          </book>
          <book available="true" author="Robert A Heinlein">
            <price discount="10%">$18.00</price>
            <isbn>341232132</isbn>
            <title>Stranger in a Strange Land</title>
          </book>
        </books>"""
        result = XML2Dict(xml).to_dict()
        assert result["@attributes"]["type"] == "fiction"
        assert isinstance(result["book"], list)
        assert len(result["book"]) == 3
        assert result["book"][0]["@attributes"]["author"] == "George Orwell"
        assert result["book"][1]["title"] == "Foundation"
        assert result["book"][2]["price"]["@attributes"]["discount"] == "10%"
        assert result["book"][2]["price"]["@text"] == "$18.00"
