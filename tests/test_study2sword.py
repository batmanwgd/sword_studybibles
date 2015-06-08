"""
    Copyright (C) 2014 Tuomas Airaksinen.
    See LICENCE.txt
"""

from study2sword.study2sword import *
from bs4 import BeautifulSoup

def test_overlapping_1():
    class options:
        title = 'ESVN'
        work_id = 'ESVN'

    osistext = BeautifulSoup("""
        <osisText>
        <div annotateRef="Gen.1.1-Gen.1.4" annotateType="commentary"><reference>blah1</reference></div>
        <div annotateRef="Gen.1.2-Gen.1.4" annotateType="commentary"><reference>blah2</reference></div>
        <div annotateRef="Gen.1.3" annotateType="commentary"><reference>blah3</reference></div>
        </osisText>
    """, 'xml')

    s = Stydy2Osis(options)
    s.root_soup = osistext
    s.fix_overlapping_ranges(osistext)
    result = osistext.prettify()
    print result
    com1, com2, com3 = osistext.find_all('div', annotateType='commentary')
    assert com1['annotateRef'] == "Gen.1.1"
    assert com2['annotateRef'] == "Gen.1.2 Gen.1.4"
    assert com3['annotateRef'] == "Gen.1.3"

    link1, link2, link3 = [i.find('list', cls='reference_links') for i in [com1,com2,com3]]
    assert not link1
    assert 'blah1' in link2.text
    assert 'blah3' not in link2.text
    assert 'blah1' in link3.text
    assert 'blah2' in link3.text

def test_merge_comments():
    class options:
        title = 'ESVN'
        work_id = 'ESVN'

    osistext = BeautifulSoup("""
        <osisText>
        <div annotateRef="Gen.1.1-Gen.1.4" annotateType="commentary"><reference>blah1</reference></div>
        <div annotateRef="Gen.1.2-Gen.1.4" annotateType="commentary"><reference>blah2</reference></div>
        <div annotateRef="Gen.1.2" annotateType="commentary"><reference>blah3</reference></div>
        <div annotateRef="Gen.1.3" annotateType="commentary"><reference>blah4</reference></div>
        </osisText>
    """, 'xml')

    s = Stydy2Osis(options)
    s.root_soup = osistext
    s.fix_overlapping_ranges(osistext)
    result = osistext.prettify()
    print result
    com1, com2, com3 = osistext.find_all('div', annotateType='commentary')
    assert com1['annotateRef'] == "Gen.1.1"
    assert com2['annotateRef'] == "Gen.1.2 Gen.1.4" #merged comments 2 % 3
    assert com3['annotateRef'] == "Gen.1.3"

    link1, link2, link3 = [i.find('list', cls='reference_links') for i in [com1,com2,com3]]
    assert not link1
    assert 'blah1' in link2.text
    assert 'blah3' not in link2.text
    assert 'blah1' in link3.text
    assert 'blah2' in link3.text

    #print result
def test_expand_ranges():
    assert expand_ranges("Gen.2.4-Gen.2.6") == "Gen.2.4 Gen.2.5 Gen.2.6"
    assert expand_ranges("Gen.1.30-Gen.2.1") == "Gen.1.30 Gen.1.31 Gen.2.1"
    assert expand_ranges("Gen.50.25-Exod.1.2") == "Gen.50.25 Gen.50.26 Exod.1.1 Exod.1.2"
    assert expand_ranges("Gen.50.1-Gen.50.26") + ' ' + expand_ranges("Exod.1.1-Exod.2.5") == expand_ranges('Gen.50.1-Exod.2.5')
    assert '1Chr.1.1' not in expand_ranges('1Chr.10.1-2Chr.9.31')
    assert expand_ranges("Gen.2.4-Gen.2.6 Gen.1.30-Gen.2.1") == "Gen.1.30 Gen.1.31 Gen.2.1 Gen.2.4 Gen.2.5 Gen.2.6"

def test_first_last_reference():
    assert first_reference('Gen.1.1-Gen.1.5') == ('Gen', 1, 1)
    assert last_reference('Gen.1.1-Gen.1.5') == ('Gen', 1, 5)
    assert first_reference('Gen.1.1-Gen.1.5 Gen.2.1') == ('Gen', 1, 1)
    assert last_reference('Gen.1.1-Gen.1.5 Gen.2.1') == ('Gen', 2, 1)
    assert first_reference('Gen.1.1-Gen.1.5 Gen.2.1-Gen.2.2') == ('Gen', 1, 1)
    assert last_reference('Gen.1.1-Gen.1.5 Gen.2.1-Gen.2.2') == ('Gen', 2, 2)

def test_parse_studybible_reference():
    assert parse_studybible_reference('n66002001-66003022.66002001-66003022') == 'Rev.2.1-Rev.3.22 Rev.2.1-Rev.3.22'
    assert parse_studybible_reference('n66002001a-66003022b') == 'Rev.2.1-Rev.3.22'
    assert parse_studybible_reference('n66002001-66003022') == 'Rev.2.1-Rev.3.22'
    assert parse_studybible_reference('n66001013') == 'Rev.1.13'
    assert parse_studybible_reference('n02023001-02023003.02023006-02023008') == 'Exod.23.1-Exod.23.3 Exod.23.6-Exod.23.8'

def test_ref():
    assert Ref('Rev.1.1') > Ref('Jude.1.1')
    assert Ref('Rev.1.2') > Ref('Rev.1.1')
    assert Ref('Rev.2.1') > Ref('Rev.1.1')
    assert Ref('Gen.1.1') < Ref('Jude.1.1')
    assert '%s' % Ref('Gen.1.1') == 'Gen.1.1'
    assert '%s' % Ref('Jude.1.1') == 'Jude.1.1'
    assert Ref('Gen.1.1') == Ref('Gen.1.1')
    assert Ref('Gen.1.1') in [Ref('Gen.1.1')]
    assert Ref('Gen.1.1') in {Ref('Gen.1.1'): 1}
    assert sorted([Ref('Gen.1.1'), Ref('Gen.2.1')]) == [Ref("Gen.1.1"), Ref("Gen.2.1")]
    assert sorted([Ref('Gen.1.1'), Ref('Exod.2.1')]) == [Ref("Gen.1.1"), Ref("Exod.2.1")]
    assert sorted([Ref('Rev.1.1'), Ref('Exod.2.1')]) == [Ref("Exod.2.1"), Ref("Rev.1.1")]