# test_btab_tokenizer.py

import unittest
from btab2mxml.btab.btab_tokenizer import BtabTokenizer
from btab2mxml.btab.token import *

test_header = \
"Last Updated 5-8-12 \n" \
"\n" \
"start\n" \
"  \n"


test_copyright_tab = """Transcribed by Sean Jones
"""
test_copyright_tokens = [
    (CopyrightToken, 'Sean Jones')
]
test_copyright = [
    (test_copyright_tab, test_copyright_tokens)
]

double_measure_bar_tab = \
"   \n" \
"||-\n" \
"||-\n" \
"||-\n" \
"||-\n"
double_measure_bar_tokens = [
    (MeasureBarToken, None)
]
double_measure_bar = (double_measure_bar_tab, double_measure_bar_tokens)

time_sig_4_4 = \
"     \n" \
"|----\n" \
"|-4:-\n" \
"|-4:-\n" \
"|----\n"
time_sig_13_8 = \
"      \n" \
"|-----\n" \
"|-13:-\n" \
"|--8:-\n" \
"|-----\n"
time_sig_tokens_4_4 = [
    (MeasureBarToken, None),
    (TimeSignatureToken, '4/4'),
]
time_sig_tokens_13_8 = [
    (MeasureBarToken, None),
    (TimeSignatureToken, '13/8'),
]
test_time_signature = [
    (time_sig_4_4, time_sig_tokens_4_4),
    (time_sig_13_8, time_sig_tokens_13_8)
]

test_notes_tab = """
    w h q e s h
||----0----------
||------2-----10-
||--------7------
||--0-------0----
"""
test_notes_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['w', '',  '', '',  '0']),
    (NoteToken, ['h', '0', '',  '',  '']),
    (NoteToken, ['q', '', '2',  '',  '']),
    (NoteToken, ['e', '', '',   '7', '']),
    (NoteToken, ['s', '', '',   '',  '0']),
    (NoteToken, ['h', '', '10', '',  '']),
]
test_notes = [
    (test_notes_tab, test_notes_tokens)
]

test_repeat_tab = """
                 5x
-||------||------||--------
-||*----*||*----*||--------
-||*----*||*----*||--------
-||------||------||--------
"""
test_repeat_tokens = [
    (MeasureBarToken, None),
    (StartRepetitionToken, None),
    (EndRepetitionToken, None),
    (MeasureBarToken, None),
    (StartRepetitionToken, None),
    (EndRepetitionToken, None),
    (MeasureBarToken, None),
    (RepetionNumberToken, '5'),
]
test_repeat2_tab = """
    h+Q e  3x E
||---------||---
||*-------*||---
||*-------*||---
||--3---0--||-5-
"""
test_repeat2_tokens = [
    (MeasureBarToken, None),
    (StartRepetitionToken, None),
    (NoteToken, None),
    (TieToken, None),
    (TiedNoteToken, None),
    (NoteToken, None),
    (EndRepetitionToken, None),
    (MeasureBarToken, None),
    (RepetionNumberToken, '3'),
    (NoteToken, None),
]
test_repeat3_tab = """
   w 37   E   7
+------+-------+-
|*-R--*|*-----*|-
|*----*|*-3---*|-
+------+-------+-
"""
test_repeat3_tokens = [
    (MeasureBarToken, None),
    (StartRepetitionToken, None),
    (RestToken, 'w'),
    (EndRepetitionToken, None),
    (MeasureBarToken, None),
    (RepetionNumberToken, '37'),
    (StartRepetitionToken, None),
    (NoteToken, ['E', '', '', '3', '']),
    (EndRepetitionToken, None),
    (MeasureBarToken, None),
    (RepetionNumberToken, '7')
]
test_repeat = [
    (test_repeat_tab, test_repeat_tokens),
    (test_repeat2_tab, test_repeat2_tokens),
    (test_repeat3_tab, test_repeat3_tokens)
]

test_tie_tab = """
   e+h       Q      +h e+  e
-|---------|-------|-----|---
-|---------|-------|---7-|---
-|-0-------|-------|-----|---
-|---------|-0-----|-----|---
"""
test_tie_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['e','', '', '0', '']),
    (TieToken, None),
    (TiedNoteToken, 'h'),
    (MeasureBarToken, None),
    (NoteToken, ['Q', '', '', '', '0']),
    (MeasureBarToken, None),
    (TieToken, None),
    (TiedNoteToken, 'h'),
    (NoteToken, ['e', '', '7', '', '']),
    (TieToken, None),
    (MeasureBarToken, None),
    (TiedNoteToken, 'e'),
]
test_tie = [
    (test_tie_tab, test_tie_tokens),
]

rest1_tab = \
"  q e q \n" \
"+-------\n" \
"|---R---\n" \
"|-3---3-\n" \
"+-------\n"
rest1_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['q', '', '', '3', '']),
    (RestToken, 'e'),
    (NoteToken, ['q', '', '', '3', '']),
]
rest1_test = [
    (rest1_tab, rest1_tokens),
]

rest_measures_tab = \
"               \n" \
"||---8 mm.--|--\n" \
"||---rest---|--\n" \
"||----------|--\n" \
"||----------|--\n"
rest_measures_tokens = [
    (MeasureBarToken, None),
    (LongRestToken, '8'),
    (MeasureBarToken, None),
]
rest_measures = [
    (rest_measures_tab, rest_measures_tokens),
]

chord_tab = """
   w
-|-----
-|-7---
-|-0---
-|-----
"""
chord_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['w', '', '7', '0', ''])
]
chord = [
    (chord_tab, chord_tokens)
]

title_tab = """Rush: A Passage to Bangkok
From the album 2112 (Mercury Records)
Copyright 1976 Core Music Publishing
Music By Lee and Lifeson
Lyrics by Peart
"""
title_tokens = [
    (TitleToken, 'A Passage to Bangkok'),
    (HeaderLineToken, None),
    (HeaderLineToken, None),
    (HeaderLineToken, None),
    (HeaderLineToken, None),
    (HeaderLineToken, None),
]
title_test = [
    (title_tab, title_tokens),
]

triplet_tab = """
   e  e  s^ s^ s^
-|-14-12-11-12-11-
-|----------------
-|----------------
-|----------------
"""
triplet_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['e', '14', '', '', '']),
    (NoteToken, ['e', '12', '', '', '']),
    (NoteToken, ['s', '11', '', '', '']),
    (TrioletToken, None),
    (NoteToken, ['s', '12', '', '', '']),
    (TrioletToken, None),
    (NoteToken, ['s', '11', '', '', '']),
    (TrioletToken, None),
]
triplet2_tab = """
   e  e  s^ s^ s^
-|-14-12-11-12-1\-
-|----------------
-|----------------
-|----------------
"""
triplet2_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['e', '14', '', '', '']),
    (NoteToken, ['e', '12', '', '', '']),
    (NoteToken, ['s', '11', '', '', '']),
    (TrioletToken, None),
    (NoteToken, ['s', '12', '', '', '']),
    (TrioletToken, None),
    (NoteToken, ['s', '1', '', '', '']),
    (GlissDownToken, None),
    (TrioletToken, None),
]
triplet_test = [
    (triplet_tab, triplet_tokens),
    (triplet2_tab, triplet2_tokens),
]

gliss_under_tie_tab = "    e e+  e    \n" \
r"-|------|------" "\n" \
r"-|------|------" "\n" \
r"-|--5-5\|------" "\n" \
r"-|------|------" "\n" \
r""
gliss_under_tie_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['e', '', '', '5', '']),
    (NoteToken, ['e', '', '', '5', '']),
    (GlissDownToken, None),
    (TieToken, None),
    (MeasureBarToken, None),
    (TiedNoteToken, None)
]
gliss_under_tie_test = [
    (gliss_under_tie_tab, gliss_under_tie_tokens)
]

ghost_tab = \
"   e s e s e s   \n" \
"-|---------------\n" \
"-|-7-x-5-x-4-x---\n" \
"-|---------------\n" \
"-|---------------\n"
ghost_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['e', '', '7', '', '']),
    (NoteToken, ['s', '', 'x', '', '']),
    (NoteToken, ['e', '', '5', '', '']),
    (NoteToken, ['s', '', 'x', '', '']),
    (NoteToken, ['e', '', '4', '', '']),
    (NoteToken, ['s', '', 'x', '', '']),
]
ghost_test = [
    (ghost_tab, ghost_tokens),
]

bend_tab = \
"    s s  s  \n" \
"-|----------\n" \
"-|--5-6^-5--\n" \
"-|----------\n" \
"-|----------\n"
bend_tokens = [
    (MeasureBarToken, None),
    (NoteToken, ['s', '', '5', '', '']),
    (NoteToken, ['s', '', '6', '', '']),
    (BendToken, None),
    (NoteToken, ['s', '', '5', '', '']),
]
bend_test = [
    (bend_tab, bend_tokens),
]

# Mock reader
class MockReader:
    def __init__(self, header = '', staff_lines=''):
        if header == '':
            self.lines = []
        else:
            self.lines = header.split('\n')
        self.index = 0
        if len(staff_lines) > 0:
            self.staff_lines = [s for s in staff_lines.split('\n') if len(s)>0]
            self.staff_line_length = max([len(s) for s in self.staff_lines])
            self.staff_lines = [s.ljust(self.staff_line_length) for s in self.staff_lines]
            self.staff_line_index = 0
            self.staff_line_number = len(self.staff_lines)
        else:
            self.staff_line_index = 0
            self.staff_line_length = 0

    def read_line(self):
        if self.index < len(self.lines):
            return self.lines[self.index]
        return ''

    def is_eof(self):
        return self.index >= len(self.lines)

    def consume_line(self):
        self.index += 1

    def get_next_score_symbol(self):
        if self.staff_line_index == self.staff_line_length:
            return None
        symbol = ''.join([l[self.staff_line_index] for l in self.staff_lines])
        self.staff_line_index += 1
        return symbol

# Test class
class TestBtabTokenizer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_header_token(self):
        reader = MockReader(test_header)
        tokenizer = BtabTokenizer(reader)
        token = tokenizer.get_next_token()
        self.assertIsInstance(token, HeaderLineToken)

    def _test_token(self, test_defs, header=False):
        for test_def in test_defs:
            tokens = []
            if header:
                reader = MockReader(test_def[0])
            else:
                reader = MockReader(test_header,
                                    test_def[0])
            tokenizer = BtabTokenizer(reader)
            token = tokenizer.get_next_token()
            while not isinstance(token, EndToken):
                if (not header) and isinstance(token, HeaderLineToken) or isinstance(token, NbStringsToken):
                    pass
                else:
                    tokens.append(token)
                token = tokenizer.get_next_token()
            self.assertSequenceEqual([t[0] for t in test_def[1]],
                                [t.__class__ for t in tokens])
            for test_index in range(len(test_def[1])):
                if test_def[1][test_index][1] is not None:
                    self.assertEqual(test_def[1][test_index][1], tokens[test_index].get_value())

    def test_multi_measure_bar(self):
        self._test_token([double_measure_bar])

    def test_time_sig(self):
        self._test_token(test_time_signature)

    def test_notes(self):
        self._test_token(test_notes)

    def test_repeats(self):
        self._test_token(test_repeat)

    def test_ties(self):
        self._test_token(test_tie)

    def test_rest(self):
        self._test_token(rest1_test)
        self._test_token(rest_measures)

    def test_end_token(self):
        reader = MockReader()
        tokenizer = BtabTokenizer(reader)
        token = tokenizer.get_next_token()
        self.assertIsInstance(token, EndToken)

    def test_copyright(self):
        reader = MockReader(test_copyright_tab)
        tokenizer = BtabTokenizer(reader)
        token = tokenizer.get_next_token()
        self.assertIsInstance(token, CopyrightToken)
        self.assertEqual(token.get_value(), test_copyright_tokens[0][1])

    def test_title(self):
        self._test_token(title_test, header=True)

    def test_triplet(self):
        self._test_token(triplet_test)

    def test_glissando(self):
        self._test_token(gliss_under_tie_test)

    def test_mute(self):
        self._test_token(ghost_test)

    def test_bend(self):
        self._test_token(bend_test)

if __name__ == '__main__':
    unittest.main()
