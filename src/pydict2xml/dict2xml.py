#!/usr/bin/env python
# coding: utf-8


import datetime
import logging
from collections import OrderedDict
from typing import Any

from lxml import etree

logger = logging.getLogger("dict2xml")


class Dict2XML(object):
    """
    Converts a Python dictionary to XML using the lxml.etree library
    For more info on see: http://lxml.de/tutorial.html
    """
    _xml = None

    def __init__(self, root_node_name, dictionary, force_cdata=False):
        """
        Converts a Python dictionary to XML using the lxml.etree library
        :param root_node_name: name of the root node
        :param dictionary: instance of a dict object that needs to be converted
        :param force_cdata: if true, all the text nodes will be wrapped in <!CDATA[[ ]]>
        """
        self._xml = etree.Element(root_node_name)
        self._convert(self._xml, dictionary, force_cdata=force_cdata)

    def to_xml_string(self, encoding='UTF-8', pretty_print=True, xml_declaration=True):
        """
        Convert the etree object into string
        :param encoding: specify the encoding for the XML String. Default 'UTF-8'
        :param pretty_print: pretty print the XML wth indentation. Default True
        :param xml_declaration: Print the XML Declaration tag in the output. Default True
        :return: XML string
        """
        return etree.tostring(self._xml, xml_declaration=xml_declaration, pretty_print=pretty_print,
                              encoding=encoding, method='xml')

    def get_etree_object(self):
        return self._xml

    def _convert(self, node, value, force_cdata=False):
        """
        Recursively traverse the dictionary to convert it to an XML
        :param node: the parent XML node
        :param value: value of the Node
        :param force_cdata: if true, all the text nodes will be wrapped in <!CDATA[[ ]]>
        :return: None
        """
        logger.debug("Parent Tag {} {}".format(node.tag, self._to_string(node)))
        logger.debug("Value {}".format(value))
        if isinstance(value, dict):
            if '@attributes' in value:
                logger.debug("Found @attributes")
                attributes = value.pop('@attributes')
                for key in attributes.keys():
                    attributes[key] = self._serialize_value(attributes[key])
                node.attrib.update(attributes)
            if '@text' in value:
                logger.debug("Found @text")
                if force_cdata:
                    node.text = etree.CDATA(self._serialize_value(value.pop('@text')))
                else:
                    node.text = self._serialize_value(value.pop('@text'))
            if '@cdata' in value:
                logger.debug("Found @cdata")
                node.text = etree.CDATA(self._serialize_value(value.pop('@cdata')))
            for key, val in value.items():
                logger.debug('Creating sub node ' + key)
                sub_node = etree.SubElement(node, key)
                self._convert(sub_node, val, force_cdata)
        elif isinstance(value, list):
            # array of nodes
            tag = node.tag
            parent = node.getparent()  # remove the current code as we will recreate an array of nodes below
            parent.remove(node)
            for val in value:
                sub_node = etree.SubElement(parent, tag)
                self._convert(sub_node, val, force_cdata)
        else:
            # text node
            if force_cdata:
                node.text = etree.CDATA(self._serialize_value(value))
            else:
                node.text = self._serialize_value(value)

    @staticmethod
    def _to_string(node):
        """
        Helper method to pretty print xml nodes
        :param node: etree XML Node to be printed.
        :return: string
        """
        return etree.tostring(node, xml_declaration=False, pretty_print=True, encoding='UTF-8', method='xml')

    @staticmethod
    def _serialize_value(value: Any):
        """Returns the serialized value to be used in XML"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, type(None)):
            return ''
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return str(value)
