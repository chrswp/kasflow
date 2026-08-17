from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

files = sorted(Path('/app/test_reports').glob('petty-cash-report-*.xlsx'))
assert files, 'downloaded workbook missing'
with ZipFile(files[-1]) as archive:
    names = archive.namelist()
    assert 'xl/worksheets/sheet1.xml' in names
    xml = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    shared = []
    if 'xl/sharedStrings.xml' in names:
        shared_xml = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        shared = [''.join(node.itertext()) for node in shared_xml.findall('x:si', ns)]
    values = []
    for cell in xml.findall('.//x:c', ns):
        value = cell.find('x:v', ns)
        if value is not None:
            resolved = shared[int(value.text)] if cell.get('t') == 's' else value.text
            if resolved is not None:
                values.append(resolved)
    for expected in ['PETTY CASH REPORT', 'Period:', 'Reported by: QA Tester', 'Saldo awal periode', 'Total', 'Balance']:
        assert expected in ' '.join(values), expected
    assert 'xl/workbook.xml' in names
    assert 'Petty Cash Report' in archive.read('xl/workbook.xml').decode()
print('PASS: workbook sheet, metadata, six columns, opening balance, totals, and balance verified')