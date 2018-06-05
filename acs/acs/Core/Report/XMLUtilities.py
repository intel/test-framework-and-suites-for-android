from lxml import etree

XML_DOC_TEST = etree.Element("Test")
ELEM_DOC_TEST = etree.SubElement(XML_DOC_TEST, "test")


def _is_valid_xml_char_ordinal(i):
    # Check if we can write it in lxml
    # Previous check may not be enough
    try:
        ELEM_DOC_TEST.set("test", i)
        is_valid = True
    except ValueError:
        is_valid = False

    return is_valid


def clean_xml_text(text):
    """
    Cleans string from invalid xml chars

    Solution was found there::

    http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    """
    return ''.join(c for c in text if _is_valid_xml_char_ordinal(c))


def pretty_print_xml(xml_file):
    """
    This function will give the XML file a pretty format
    :param xml_file: file to be formatted
    :return:
    """
    assert xml_file is not None
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)
    tree = etree.parse(xml_file, parser)
    tree.write(xml_file, pretty_print=True, encoding='utf-8')
