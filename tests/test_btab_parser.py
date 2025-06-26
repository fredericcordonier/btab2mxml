import unittest
from unittest.mock import MagicMock
from btab2mxml.btab.btab_parser import BtabParser
from btab2mxml.btab.token import *
import music21

# Mock tokens to return values expected by the test
class MockNbStringsToken(NbStringsToken):
    def get_value(self):
        return 4

class MockNoteToken(NoteToken):
    def get_value(self):
        return ['q','', '', '0', '']

class MockChordToken(NoteToken):
    def get_value(self):
        return ['w', '', '7', '0', '']

class MockChordWithGhostToken(NoteToken):
    def get_value(self):
        return ['w', '', '7', '0', 'x']

class MockPullOffToken(PullOffToken):
    def get_value(self):
        return ''
    
class MockGhostNoteToken(NoteToken):
    def get_value(self):
        return ['s', '', 'x', '', '']

class MockCopyrightToken(CopyrightToken):
    def get_value(self):
        return 'Test copyright'

# Create and return a mock tokenizer with given tokens
def get_tokenzier(tokens):
    mock_tokenizer = MagicMock()
    mock_tokenizer.get_next_token.side_effect = tokens
    return mock_tokenizer

# Tests class
class TestBtabParser(unittest.TestCase):
    def test_parse_single_note(self):
        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),  # Strings number
            MeasureBarToken(),     # Start of measure
            MockNoteToken(),       # One note "q0"
            EndToken()             # End
        ])

        parser = BtabParser(mock_tokenizer)
        parser.parse()

        self.assertIsNotNone(parser.current_measure)
        notes = list(parser.current_measure.notes)
        self.assertEqual(len(notes), 1)

        note = notes[0]
        self.assertIsInstance(note, music21.note.Note)
        self.assertEqual(note.duration.type, 'quarter')
        self.assertEqual(int(note.pitch.ps), 45)

    def test_ghost_note(self):
        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),
            MeasureBarToken(),
            MockGhostNoteToken(),
            EndToken()
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()
        self.assertIsNotNone(parser.current_measure)
        notes = list(parser.current_measure.notes)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].notehead, 'x')


    def test_chord(self):
        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),  # Strings number
            MeasureBarToken(),     # Start measure
            MockChordToken(),      # One note "q0"
            EndToken()             # End
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()

        self.assertIsNotNone(parser.current_measure)
        notes = list(parser.current_measure.notes)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertIsInstance(note, music21.chord.Chord)
        self.assertEqual(note.duration.type, 'whole')
        pitches = note.pitches
        self.assertEqual(len(pitches), 2)
        self.assertEqual(int(pitches[0].ps), 57)
        self.assertEqual(int(pitches[1].ps), 45)

        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),  # Strings number
            MeasureBarToken(),     # Start measure
            MockChordWithGhostToken(),
            EndToken()
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()

        self.assertIsNotNone(parser.current_measure)
        notes = list(parser.current_measure.notes)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertIsInstance(note, music21.chord.Chord)
        self.assertEqual(note.duration.type, 'whole')
        notes = note.notes
        self.assertEqual(notes[-1].notehead, 'x')

    def test_pull_off(self):
        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),
            MeasureBarToken(),
            MockNoteToken(),
            MockPullOffToken(),
            MockNoteToken(),
            EndToken()
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()

    def test_copyright(self):
        mock_tokenizer = get_tokenzier([
            MockCopyrightToken(),
            EndToken()             # End
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()
        self.assertIsNotNone(parser.score.metadata.copyright)
        self.assertEqual(parser.score.metadata.copyright, 'Translation copyright: Test copyright')

    def test_bend(self):
        mock_tokenizer = get_tokenzier([
            MockNbStringsToken(),
            MeasureBarToken(),
            MockNoteToken(),
            BendToken(),
            EndToken()
        ])
        parser = BtabParser(mock_tokenizer)
        parser.parse()

        self.assertIsNotNone(parser.current_measure)
        notes = list(parser.current_measure.notes)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        expr = [e for e in parser.current_measure.elements if isinstance(e, music21.expressions.TextExpression)]
        self.assertEqual(len(expr), 1)
        self.assertEqual(expr[0].content, '~')

class TestBtabParserMeasureOverflow(unittest.TestCase):
    def test_measure_duration_overflow_warning(self):
        # 5 notes 'q0' (quarter notes) = 5 * 1/4 = 1.25 > 1.0 (4/4)
        tokenizer = MagicMock()
        tokenizer.get_next_token.side_effect = [
            MockNbStringsToken(),       # Nb strings
            MeasureBarToken(),          # Start of measure
            MockNoteToken(['q', '0']),  # 1st note
            MockNoteToken(['q', '0']),  # 2nd note
            MockNoteToken(['q', '0']),  # 3rd note
            MockNoteToken(['q', '0']),  # 4th note
            MockNoteToken(['q', '0']),  # 5th note (overflow)
            MeasureBarToken(),          # Closes the measure (triggers check)
            EndToken()
        ]

        parser = BtabParser(tokenizer)
        parser.current_time_signature = '4/4'  # Force to 4/4
        with self.assertLogs(level='WARNING') as log:
            parser.parse()

        self.assertTrue(any("Duration of measure" in msg for msg in log.output))


if __name__ == '__main__':
    unittest.main()
