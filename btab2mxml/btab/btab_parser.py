import logging
from btab2mxml.btab.token import *
import music21

class BtabParser_InvalidDurationException(Exception):pass
class BtabParser_InvalidPitchException(Exception):pass


class MyPitch(music21.pitch.Pitch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ghost = False

class BtabParser:
    notes_duration = {
            'W': ('whole', 1, 48),
            'w': ('whole', 0, 32),
            'H': ('half', 1, 24),
            'h': ('half', 0, 16),
            'Q': ('quarter', 1, 12),
            'q': ('quarter', 0, 8),
            'E': ('eighth', 1, 6),
            'e': ('eighth', 0, 4),
            'S': ('16th', 1, 3),
            's': ('16th', 0, 2),
            't': ('32nd', 0, 1),
        }

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.nb_strings = 0
        self.score = music21.stream.Score(id='mainScore')
        self.score.insert(0, music21.metadata.Metadata())
        self.bass = music21.stream.Part(id='bass')
        pc = music21.clef.PitchClef()
        pc.sign = 'F'
        pc.line = 4
        self.bass.append(pc)
        self.current_measure = None
        self.repeated_measure = None
        self.measure_nb = 1
        self.empty_measure = True
        # Default time signature
        self.current_time_signature = None
        self.measure_duration = self._get_measure_duration()
        self.current_note = None
        self.triolet = []
        self.glissando = None
        self.expression = None
        self.last_header_token = ''

    def parse(self):
        token = self.tokenizer.get_next_token()
        # Skip header
        while isinstance(token, HeaderLineToken):
            self._handle_header_token(token)
            token = self.tokenizer.get_next_token()
        while not isinstance(token, NbStringsToken) and not isinstance(token, EndToken):
            token = self.tokenizer.get_next_token()
        self.nb_strings = token.get_value()
        string_pitches = ['E1', 'A1', 'D2', 'G2']
        if self.nb_strings == 5:
            string_pitches.insert(0, 'B0')
        self.bass.append(music21.instrument.ElectricBass(stringPitches=string_pitches))
        while not isinstance(token, EndToken):
            self._handle_token(token)
            token = self.tokenizer.get_next_token()

    def _handle_header_token(self, token):
        if isinstance(token, CopyrightToken):
            self.score.metadata.copyright = f'Translation copyright: {token.get_value()}'
        elif isinstance(token, TitleToken):
            self.score.metadata.title = token.get_value()
        elif (len(self.last_header_token) > 0) and token.get_value() == 'By Rush':
            self.score.metadata.title = self.last_header_token.strip()
        else:
            self.last_header_token = token.get_value()

    def _handle_token(self, token):
        if isinstance(token, MeasureBarToken):
            if self.current_measure is not None and not self.empty_measure:
                if self.current_time_signature is None:
                    self.current_time_signature = '4/4'
                    ts = music21.meter.TimeSignature(self.current_time_signature)
                    self.current_measure.insert(ts)
                total_duration = sum([n.duration.quarterLength 
                                      for n in self.current_measure.notes.activeElementList])
                if round(total_duration, 4) != self._get_measure_duration() / 8:
                    logging.warning(f'Duration of measure {self.measure_nb}: {total_duration},' \
                                    f' time signature is {self.current_time_signature}')
                self._add_measure()
            self.current_measure = music21.stream.Measure(self.measure_nb)
            self.measure_duration = self._get_measure_duration()

        elif isinstance(token, StartRepetitionToken):
            self.current_measure.leftBarline = music21.bar.Repeat(direction='start')

        elif isinstance(token, EndRepetitionToken):
            self.current_measure.rightBarline = music21.bar.Repeat(direction='end')
            self.repeated_measure = self.current_measure

        elif isinstance(token, RepetionNumberToken):
              # Add repetition text
            repeat_text = music21.expressions.TextExpression(f"{token.get_value()}x")
            repeat_text.style.alignHorizontal = 'center'
            repeat_text.placement = 'above'
            self.repeated_measure.insert(self.repeated_measure.highestTime, repeat_text)
            self.repeated_measure = None

        elif isinstance(token, TimeSignatureToken):
            self.current_time_signature = token.get_value()
            ts = music21.meter.TimeSignature(self.current_time_signature)
            ts.implicit = False
            if self.current_measure is not None:
                self.current_measure.insert(ts)

        elif isinstance(token, NoteToken):
            symbols = token.get_value()
            header = symbols[0][0]
            inserted = None
            try:
                duration = self._get_duration(header)
            except BtabParser_InvalidDurationException:
                logging.error(f'Invalid duration: {symbols}')
            except IndexError:
                logging.error(f'Invalid duration: {symbols}')
            else:
                nb_notes = [s for s in symbols[1:] if len(s) > 0]
                if len(nb_notes) > 1:
                    pitches = [[ '' if i != idx else val for i in range(len(symbols[1:])) ]
                                for idx, val in enumerate(symbols[1:]) if val != '']
                    try:
                        pitches = [self._get_pitch(p) for p in pitches]
                    except BtabParser_InvalidPitchException:
                        logging.error(f'Invalid pitch: {symbols}')
                        pitches = [MyPitch('C')]
                    inserted = music21.chord.Chord(pitches, duration=duration)
                    # Handle ghost notes
                    for n in inserted.notes:
                        if n.pitch.ghost:
                            n.notehead = 'x'
                else:
                    try:
                        pitch = self._get_pitch(symbols[1:])
                    except BtabParser_InvalidPitchException:
                        logging.error(f'Invalid pitch: {symbols}')
                        pitch = MyPitch('C')
                    inserted = music21.note.Note(pitch=pitch, duration=duration)
                    if pitch.ghost:
                        inserted.notehead = 'x'
                if inserted:
                    self.current_note = inserted
                    if self.glissando:
                        self._add_glissando(self.glissando, self.current_note)
                    self.current_measure.append(self.current_note)
                    if self.expression:
                        # Create slur
                        sl = music21.spanner.Slur([self.expression[0], self.current_note])
                        self.current_note.articulations.append(self.expression[1].get_value())
                        self.current_measure.insert(sl)

                        text = music21.expressions.TextExpression("h" if isinstance(self.expression[1], HammerOnToken) else "p")
                        text.style.alignHorizontal = 'center'
                        text.placement = 'above'
                        text.style.defaultY = 100
                        text.style.fontSize = 8
                        text.style.fontStyle = 'italic'
                        self.current_measure.insert(self.current_note.offset, text)

                        self.expression = None
                    self.empty_measure = False

        elif isinstance(token, TieToken):
            if self.current_note:
                self.current_note.tie = music21.tie.Tie('start')

        elif isinstance(token, TiedNoteToken):
            added = False
            if self.current_note and self.current_note.tie:
                try:
                    duration = self._get_duration(token.get_value())
                except BtabParser_InvalidDurationException:
                    logging.error(f'Invalid duration: {token.get_value()}')
                else:
                    if isinstance(self.current_note, music21.note.Rest):
                        self.current_note = music21.note.Rest(duration=duration)
                        self.current_measure.append(self.current_note)
                        self.empty_measure = False
                    elif isinstance(self.current_note, music21.note.Note):
                        self.current_note = music21.note.Note(pitch=self.current_note.pitch,
                                                            duration=duration)
                        self.current_measure.append(self.current_note)
                        self.empty_measure = False
                    elif isinstance(self.current_note, music21.chord.Chord):
                        self.current_note = music21.chord.Chord(self.current_note.pitches,
                                                                duration=duration)
                        self.current_measure.append(self.current_note)
                        self.empty_measure = False
                    else:
                        logging.error(f'Continued note (current={str(self.current_note)})')
            else:
                logging.error(f'continued note (measure {self.measure_nb})')

        elif isinstance(token, RestToken):
            duration = self._get_duration(token.get_value())
            self.current_note = music21.note.Rest(duration=duration)
            self.current_measure.append(self.current_note)
            self.empty_measure = False

        elif isinstance(token, LongRestToken):
            if self.current_measure is None:
                # Happens that a multi-measure rest is at beginning, without measure bar
                #   so current_measure may not be created
                self.current_measure = music21.stream.Measure(self.measure_nb)
                self.measure_nb += 1
                self.measure_duration = self._get_measure_duration()
            self.current_measure.leftBarline = music21.bar.Repeat(direction='start')

            durations = self._get_measure_durations()
            for d in durations:
                duration = self._get_duration(d)
                self.last_note = music21.note.Rest(duration=duration)
                self.current_measure.append(music21.note.Rest(duration=duration))

            # Add repetition text
            repeat_text = music21.expressions.TextExpression(f"{token.get_value()}x")
            repeat_text.style.alignHorizontal = 'center'
            repeat_text.placement = 'above'
            self.current_measure.insert(self.current_measure.highestTime, repeat_text)

            self.current_measure.rightBarline = music21.bar.Repeat(direction='end')
            self._add_measure()
            self.current_measure = music21.stream.Measure(self.measure_nb)


        elif isinstance(token, TrioletToken):
            self.current_note.duration.quarterLength = self.current_note.duration.quarterLength * 2 / 3
        
        elif isinstance(token, GlissDownToken) or isinstance(token, GlissUpToken):
            self.glissando = self.current_note

        elif isinstance(token, BendToken):
            bend = music21.expressions.TextExpression('~')
            bend.placement = 'above'  # place it above the note
            self.current_measure.insert(self.current_note.offset, bend)

        elif isinstance(token, NbStringsToken):
            self.nb_strings = token.get_value()

        elif isinstance(token, HammerOnToken) or isinstance(token, PullOffToken):
            if self.current_note is not None:
                self.expression = (self.current_note, token)

    def _add_measure(self):
            self.bass.append(self.current_measure)
            self.current_measure = music21.stream.Measure(self.measure_nb)
            self.empty_measure = True
            logging.debug(f'btab_parser: add measure {self.measure_nb}')
            self.measure_nb += 1

    def _add_glissando(self, note_from, note_to):
        a = music21.spanner.Glissando([note_from, note_to])
        a.lineType = 'solid'
        a.label = ''
        a.slideType = 'continuous'
        self.current_measure.append(a)
        self.glissando = None

    def _get_measure_duration(self):
        """ Compute the number of 32th notes fitting in a measure given the current
            time signature
        """
        if self.current_time_signature is not None:
            nom, denom = (int(d) for d in self.current_time_signature.split('/'))
            return nom * 32 / denom
        else:
            # Defaults to 4/4
            return 32

    def _get_measure_durations(self):
        """ Get the notes durations needed to fit one measure; used for measure-long rests.
        """
        durations = [(k, self.notes_duration[k][2]) for k in self.notes_duration.keys()]
        nom = self._get_measure_duration()
        index = 0
        returned = []
        out = False
        while not out:
            if nom >= durations[index][1]:
                returned.append(durations[index][0])
                nom -= durations[index][1]
            else:
                index += 1
            if nom == 0:
                out = True
        return returned

    def _get_duration(self, duration_str):
        durations = {
            'w': ('whole', 0),
            'W': ('whole', 1),
            'h': ('half', 0),
            'H': ('half', 1),
            'q': ('quarter', 0),
            'Q': ('quarter', 1),
            'e': ('eighth', 0),
            'E': ('eighth', 1),
            's': ('16th', 0),
            'S': ('16th', 1),
            't': ('32nd', 0),
            'T': ('32nd', 1)
        }
        if duration_str in durations.keys():
            duration = music21.duration.Duration(durations[duration_str][0],
                                                 dots=durations[duration_str][1])
        else:
            raise BtabParser_InvalidDurationException
        return duration
    
    def _get_pitch(self, frets):
        string_pitch = [55.0, 50.0, 45.0, 40.0, 35.0]
        if len(frets) == 0:
            raise BtabParser_InvalidPitchException
        fret = ''.join(frets)
        if fret:
            string = frets.index(fret)
        else:
            raise BtabParser_InvalidPitchException
        if '(' in fret:
            fret = fret.replace('(', '').replace(')', '')
            try:
                ret = MyPitch(string_pitch[string] + int(fret))
            except ValueError:
                raise BtabParser_InvalidPitchException
            else:
                logging.info(f'Appologiatura not supported')
                raise BtabParser_InvalidPitchException
        else:
            # Ghost note:
            if fret == 'x':
                ret = MyPitch(ps=string_pitch[string])
                ret.ghost = True
            else:
                try:
                    ret = MyPitch(ps=string_pitch[string] + int(fret))
                except ValueError:
                    raise BtabParser_InvalidPitchException
        # return music21.pitch.Pitch(ps=pitch)
        return ret

    def output(self, filename):
        if self.score.metadata.copyright is None:
            logging.warning('Score has no copyright')
        elif self.score.metadata.title is None:
            logging.warning('Title not found')
        self.score.insert(self.bass)
        self.score.write('musicxml', fp=filename)


if __name__ == "__main__":
    bp = BtabParser(None)
    bp.current_time_signature = '4/4'
    print('4/4')
    print(bp._get_measure_durations())
    bp.current_time_signature = '13/8'
    print('13/8')
    print(bp._get_measure_durations())
