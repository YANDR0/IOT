import json
import os
from pathlib import Path
from lxml import etree



def convert_field_data(json_file: str | Path, xml_output: str | Path):
    with open(json_file) as f:
        data = json.load(f)
    
    root = etree.Element('additional')
    interval = etree.SubElement(root, 'interval', begin="0", end="3600")
    
    for direction in data['directions']:
        total = sum([t['count'] for t in direction['to']])
        for target in direction['to']:
            prob = target['count'] / total
            etree.SubElement(
                interval, 
                'edgeRelation',
                attrib={
                    'from': direction['from'],
                    'to': target['edge'],
                    'probability': str(round(prob, 2))
                }
            )
    
    etree.ElementTree(root).write(xml_output, pretty_print=True, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    convert_field_data('./data/fieldwork_data.json', './assets/turn_definitions.add.xml')