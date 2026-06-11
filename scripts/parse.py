import zipfile
import xml.etree.ElementTree as ET

docx_path = r'f:\HACKATHONS\FAR AWAY\RAVEN_FAR_AWAY_2026.docx'
try:
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        xml_content = docx_zip.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)
        with open('docx_output.txt', 'w', encoding='utf-8') as f:
            for p in paragraphs:
                texts = p.findall('.//w:t', ns)
                if texts:
                    f.write(''.join([t.text for t in texts if t.text]) + '\n')
                else:
                    f.write('\n')
except Exception as e:
    with open('docx_output.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
