import music21

class Token:
    default_value = ''
    def __init__(self, value=None):
        self.value = value

    def get_value(self):
        if self.value is None:
            return self.default_value
        else:
            return self.value
    
    def __str__(self):
        return f'{self.__class__.__name__} {str(self.get_value())}'

class EndToken(Token):    default_value = 'End'
class HeaderLineToken(Token):  pass
class CopyrightToken(HeaderLineToken): pass
class NoteToken(Token):pass
class TiedNoteToken(Token): pass
class RestToken(Token):
    def __init__(self, value):
        super().__init__()
        if len(value) == 1:
            self.value = value[0].strip()[0]
class LongRestToken(Token):
    def __init__(self, value):
        self.value = ''.join([v for v in value if v.isdigit()])

class TrioletToken(Token):pass
class MeasureBarToken(Token): default_value = 'Measure Bar'
class StartRepetitionToken(Token): default_value = 'Start repetition'
class EndRepetitionToken(Token): default_value = 'End repetition'
class RepetionNumberToken(Token):pass
class TimeSignatureToken(Token):
    def __init__(self, value):
        ts_string = [''.join(t[i] for t in value if t[i] != '-') for i in range(1, len(value[0]))]
        ts_string = [t for t in ts_string if len(t.strip()) > 0]
        self.value = '/'.join(t for t in ts_string)

    def get_value(self):
        return self.value
    
class NbStringsToken(Token): pass
class TieToken(Token): default_value = 'Tie'
class GlissDownToken(Token): default_value = 'Glissando'
class HammerOnToken(Token): default_value = music21.articulations.HammerOn()
class PullOffToken(Token): default_value = music21.articulations.PullOff()
class GlissUpToken(Token): default_value = 'Glissando'
