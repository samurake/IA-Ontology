import unicodedata
from zeep import Client # SOAP Client
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

class RDFProcessor:

    def __init__(self, xml_preprocesare, document_name):
        self.xml_preprocesare = xml_preprocesare
        self.document_name = document_name
        self.replace_diacritics(document_name)

    def get_rdf(self):
        print self.process_soap_result(self.document_name)
        return self.convert_rdf(self.process_soap_result(self.document_name))

    def find_negation(self, phrase, wordid):
        x = wordid
        word_id = str(x).split('.')[1]
        connected_words = []
        for child in phrase:
            if word_id == child.attrib["head"] and child.attrib["deprel"] == "neg." or child.attrib["deprel"] == "refl.":
                connected_words.append(child.attrib)
        return connected_words

    def grab_xml(self, text):
        client = Client('http://nlptools.info.uaic.ro/WebFdgRo/FdgParserRoWS?wsdl')
        result = client.service.parseText(text)
        return result


    def generate_relation(self, phrase, wordid, list):
        x = wordid
        word_id = str(x).split('.')[1]
        for child in phrase:
            if word_id == child.attrib["head"]:
                list.append(child.attrib)
                self.generate_relation(phrase, child.attrib["id"], list)

    def generate_words_relation(self, phrase, wordid):
        x = wordid
        prop_id = str(x).split('.')[0]
        word_id = str(x).split('.')[1]
        connected_words = []
        for child in phrase:
            if word_id == child.attrib["head"]:
                connected_words.append(child.attrib)
        return connected_words


    def find_roots(self, phrase, wordid):
        x = wordid
        word_id = str(x).split('.')[1]
        connected_words = []
        for child in phrase:
            if word_id == child.attrib["head"] and child.attrib["deprel"] == "ROOT" and "POS" in child.attrib:
                connected_words.append(child.attrib)
        return connected_words


    def process_soap_result(self, striped_document):
        return_list = []
        f = open(striped_document, 'r')
        data = f.read().decode('utf-8').strip().split('\n')
        f.close()
        data_collection = []
        for text_to_be_transformed in data:
            callback_result_from_Parser = self.grab_xml(text_to_be_transformed).encode('utf-8').strip()
            root = ET.fromstring(str(callback_result_from_Parser))
            for phrase in root:
                current_list = []
                for child in phrase:
                    child.attrib["text"] = child.text
                    if 'EXTRA' in child.attrib and child.attrib['EXTRA'] == 'NotInDict':
                        continue
                    if 'POS' in child.attrib \
                            and ((child.attrib['POS'] == 'VERB' and child.attrib['deprel'] == 'aux.')
                                 or (child.attrib['POS'] == 'VERB' and child.attrib['deprel'] == 'ROOT')
                                 or (child.attrib['POS'] == 'VERB' and child.attrib[
                                    'deprel'] == 'ROOT' and self.find_roots(phrase, child.attrib["id"]))):
                        current_list.append(
                            [child.attrib] + self.find_negation(phrase, child.attrib["id"]) + self.find_roots(phrase,
                                                                                                    child.attrib[
                                                                                                                      "id"]))
                        connected_words = self.generate_words_relation(phrase, child.attrib["id"])
                        for word in connected_words:
                            sentence = []
                            sentence.append(word)
                            self.generate_relation(phrase, word["id"], sentence)
                            current_list.append(sentence)
                return_list.append(current_list)

            new_list = []
            for i in range(0, len(return_list)):
                prop = []
                for j in range(0, len(return_list[i])):
                    tmp_list = []
                    for x in range(0, len(return_list[i][j])):
                        tmp_list.append(
                            (return_list[i][j][x]["text"], return_list[i][j][x]["deprel"], return_list[i][j][x]["id"]))
                    tmp_list = sorted(tmp_list, key=lambda tup: int(str(tup[2]).split('.')[1]))
                    prop.append(tmp_list)
                new_list.append(prop)

            for i in range(0, len(new_list)):
                ret = []
                subject = [None]
                noun = [None]
                object = [None]
                if (len(new_list[i])) > 0:
                    noun = new_list[i][0]
                else:
                    continue
                for j in range(1, len(new_list[i])):
                    for k in range(0, len(new_list[i][j])):
                        if (new_list[i][j][k][1] == "sbj."):
                            subject = new_list[i][j]
                            continue
                        if new_list[i][j][k][1] == 'n.pred.' or new_list[i][j][k][1] == 'c.d.' or new_list[i][j][k][
                            1] == 'a.adj.' or new_list[i][j][k][1] == 'coord.' or new_list[i][j][k][1] == 'a.subst.' or \
                                        new_list[i][j][k][1] == 'prep.':
                            object = new_list[i][j]
                ret.append((subject, noun, object))

            data_collection.append(ret)
        return data_collection


    def replace_diacritics(self, document_name):
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


    def convert_rdf(self, properties):
        rdf = ET.Element('rdf:RDF')
        rdf.set("xmlns:rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdf.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")

        for list in properties:
            for value in list:
                if (value[0][0] != None and value[1][0] != None and value[2][0] != None):
                    subject = ""
                    for subject_elements in value[0]:
                        subject += subject_elements[0] + " "
                    characteristic = ""

                    for charcateristics_elemnts in value[2]:
                        characteristic += charcateristics_elemnts[0] + " "
                    noun = ""

                    for element_lista_predicat in value[1]:
                        noun += element_lista_predicat[0] + " "
                    rdf_description = ET.SubElement(rdf, 'rdf:Description')

                    subjetcs = ET.SubElement(rdf_description, 'rdf:' + value[0][0][1])
                    subjetcs.text = subject.rstrip()

                    nouns = ET.SubElement(rdf_description, 'rdf:' + value[1][0][1])
                    nouns.text = noun.rstrip()

                    objects = ET.SubElement(rdf_description, 'rdf:' + value[2][0][1])
                    objects.text = characteristic.rstrip() + '\n'

        return tostring(rdf)


if __name__ == "__main__":
    rdf_processor = RDFProcessor('hfdsghfgsdjfh', 'test.txt')
    print rdf_processor.get_rdf()