"""Convert XML to a Python dictionary using lxml."""

import re
from collections import OrderedDict

from lxml import etree

_NS_PATTERN = re.compile(r'\{[^}]+\}')


class XML2Dict:
    """
    Converts XML to a Python dictionary using the lxml.etree library.
    For more info see: http://lxml.de/tutorial.html
    """

    def __init__(self, xml, ns_clean=True, strip_namespaces=False):
        """
        :param xml: XML string or bytes to parse
        :param ns_clean: passed to lxml's XMLParser to clean up redundant
            namespace declarations. Does not affect tag names in the output dict.
        :param strip_namespaces: if True, remove namespace URIs from tag names
            (e.g. "{http://example.com}child" becomes "child"). Default False.
        """
        parser = etree.XMLParser(ns_clean=ns_clean, remove_blank_text=True)
        self._xml = etree.XML(xml, parser)
        self._strip_namespaces = strip_namespaces

    def to_dict(self, ordered_dict=False):
        """
        Convert the parsed XML to a Python dictionary.

        :param ordered_dict: if True, return an OrderedDict instead of a dict
        :return: dict or OrderedDict representation of the XML
        """
        return self._convert(self._xml, ordered_dict)

    def get_etree_object(self):
        """Return the underlying lxml.etree.Element."""
        return self._xml

    def _tag_name(self, tag):
        """
        Return the tag name, stripping namespace URI if strip_namespaces is enabled.

        :param tag: tag string, potentially with namespace like "{uri}name"
        :return: cleaned tag name
        """
        if self._strip_namespaces:
            return _NS_PATTERN.sub('', tag)
        return tag

    def _convert(self, node, ordered_dict=False):
        """
        Recursively convert an XML node to a dictionary.

        :param node: the XML node to convert
        :param ordered_dict: if True, use OrderedDict
        :return: dict, OrderedDict, or string for text-only nodes
        """
        xml_dict = OrderedDict() if ordered_dict else {}

        # add attributes and text nodes
        if len(node.attrib):
            xml_dict['@attributes'] = dict(node.attrib)
        if node.text:
            xml_dict['@text'] = node.text

        # add children if any
        if len(node):
            for child in node:
                tag = self._tag_name(child.tag)
                if tag not in xml_dict:
                    # collect children into a list; single-element lists are flattened below
                    xml_dict[tag] = []
                xml_dict[tag].append(self._convert(child, ordered_dict))

            # flatten single-element lists
            for key, value in xml_dict.items():
                if isinstance(value, list) and len(value) == 1:
                    xml_dict[key] = value[0]

        # flatten the dict if it just has the @text key
        if len(xml_dict) == 1 and '@text' in xml_dict:
            xml_dict = xml_dict['@text']

        return xml_dict
