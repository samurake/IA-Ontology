from zeep import Client
import xml.etree.ElementTree as ET


def replace_diacritics(document_name):
    f = open(document_name, 'r')
    data = f.read().decode('utf-8')
    data = data.lower()

    text = unicodedata.normalize('NFD', data)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")

    f.close()

    f = open(document_name, 'w')
    f.write(text)
    f.close()


def grab_xml(text):
    client = Client('http://nlptools.info.uaic.ro/WebFdgRo/FdgParserRoWS?wsdl')
    result = client.service.parseText(text)

    return result

if __name__ == '__main__':
    sentences = ['ana are mere.', 'ana are caise.', 'ane are bani de dat.']

    for sentence in sentences:

        xmlResult = grab_xml(sentence)
        root = ET.fromstring(xmlResult.encode('utf-8').strip())

        for phrase in root:
            for child in phrase:
                pass
