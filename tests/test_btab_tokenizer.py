# test_btab_tokenizer.py

import unittest
from btab.btab_tokenizer import BtabTokenizer
from btab.token import *

test_header = """
Last Updated 5-8-12

start
    
"""

test_copyright_tab = """Transcribed by Sean Jones
"""
test_copyright_tokens = [
    (CopyrightToken, 'Sean Jones')
]
test_copyright = [
    (test_copyright_tab, test_copyright_tokens)
]

double_measure_bar_tab = """
   
||-
||-
||-
||-
"""
double_measure_bar_tokens = [
    (MeasureBarToken, None)
]
double_measure_bar = (double_measure_bar_tab, double_measure_bar_tokens)

time_sig_4_4 = """
     
|----
|-4:-
|-4:-
|----
"""
time_sig_13_8 = """
      
|-----
|-13:-
|--8:-
|-----
"""
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
test_repeat = [
    (test_repeat_tab, test_repeat_tokens),
    (test_repeat2_tab, test_repeat2_tokens)
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

rest_measures_tab = """
               
||---8 mm.--|--
||---rest---|--
||----------|--
||----------|--
"""
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
            self.staff_line_index = 0
            self.staff_line_number = len(self.staff_lines)
            self.staff_line_length = len(self.staff_lines[0])
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


if __name__ == '__main__':
    unittest.main()
