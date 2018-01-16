from zeep import Client
import xml.etree.ElementTree as ET

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
