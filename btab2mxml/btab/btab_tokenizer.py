import logging
from btab2mxml.btab.token import *

class BtabTokenizer:
    durations = 'wWhHqQeEsS'
    note_paths = {
    '\\': GlissDownToken,
    'H': HammerOnToken,
    'h': HammerOnToken,
    'p': PullOffToken,
    '/': GlissUpToken,
    '^': BendToken,
    }

    def __init__(self, reader):
        self.reader = reader
        self.current_state = self.header
        self.symbol_buffer = []
        self.token_buffer = []
        self.in_repetition = False
        self.nb_strings = 0
        self.frets_buffer = []
        self.header_buf = []
        self.fret_buf = []

    def get_next_token(self):
        """ Return and consume the next token.
        """
        token = None
        while token is None:
            if len(self.token_buffer) > 0:
                token = self.token_buffer[0]
                del(self.token_buffer[0])
            else:
                token = self.current_state()

        logging.debug(f'btab_tokenizer: sending token {str(token)}')
        return token

    def header(self):
        line = self.reader.read_line()
        if self.reader.is_eof():
            return EndToken(line)
        if len(line) > 0 and line[0] == ' ':
            self.current_state = self.count_strings
            return HeaderLineToken('')
        elif len(line) > 0 and 'Rush:' in line:
            self.reader.consume_line()
            return TitleToken(line.replace('Rush: ', ''))
        elif len(line) > 0 and 'Transcribed' in line:
            self.reader.consume_line()
            return CopyrightToken(line.replace('Transcribed by', '').strip())
        self.reader.consume_line()
        return HeaderLineToken(line)

    def count_strings(self):
        if self.reader.is_eof():
            return EndToken()
        symbol = self.reader.get_next_score_symbol()
        while symbol is not None and len(symbol) != 0:
            self.symbol_buffer.append(symbol)
            if '|' in symbol:
                self.nb_strings = symbol.count('|')
                self.token_buffer.append(NbStringsToken(self.nb_strings))
                self.current_state = self.score
                return
            symbol = self.reader.get_next_score_symbol()

    def _split_symbol(self, symbol):
        # Header may contain duration or tie symbol (+)
        header = symbol[0].strip()
        # Strings will contain fretted positions or various transition signs
        frets = symbol[1:]
        return (header, frets)

    def _consume_measure(self, header, frets):
        header_buf = header
        self.symbol_buffer = []
        self.token_buffer.append(MeasureBarToken())
        end_symbol = False
        while not end_symbol:
            symbol = self.reader.get_next_score_symbol()
            if symbol is None or len(symbol) == 0:
                # End of score --> skip to next state
                self.symbol_buffer.append(symbol)
                end_symbol = True
            else:
                header, frets = self._split_symbol(symbol)
                header_buf += header
                if (frets == '||||') or (frets == '+||+') or (frets == '-|||'):
                    end_symbol = False
                    if len(header_buf) > 0:
                        self.token_buffer.append(RepetionNumberToken(header_buf.replace('x', '')))
                elif (frets == '-' * self.nb_strings) and (len(header) == 0):
                    end_symbol = True
                elif '**' in frets:
                    self.token_buffer.append(StartRepetitionToken())
                else:
                    end_symbol = True
                    self.symbol_buffer.append(symbol)

    def _get_next_symbol(self):
        if len(self.symbol_buffer) > 0:
            # Treat postponed symbols
            symbol = self.symbol_buffer[0]
            del(self.symbol_buffer[0])
        else:
            symbol = self.reader.get_next_score_symbol()
            if self.reader.is_eof():
                return self.token_buffer.append(EndToken())
        return symbol

    def _send_symbol(self):
        if len(self.frets_buffer) > 0:
            if (len(self.frets_buffer) == 1) and ('rest' in self.frets_buffer[0]):
                self.token_buffer.append(RestToken(self.frets_buffer))
            else:
                value = [''.join([s[j].replace('-', '').strip() for s in self.frets_buffer]) 
                        for j in range(0, len(self.frets_buffer[0]))]
                if 'rest' in value:
                    value = ''.join([v for v in value if len(v) > 0]).strip()
                    self.token_buffer.append(LongRestToken(value))
                elif 'R' in value:
                    self.token_buffer.append(RestToken(self.frets_buffer))
                else:
                    self.token_buffer.append(NoteToken(value))
            self.frets_buffer = []

    def score(self):
        symbol = self._get_next_symbol()
        if symbol is None or len(symbol) == 0:
            # End of score --> skip to next state
            self.current_state = self.end
            return None

        symbol = symbol[-(self.nb_strings+1):]
        header, strings = self._split_symbol(symbol)
        # Here I get the transition paths
        paths = [p for p in BtabTokenizer.note_paths.keys() if p in strings]
        trailer_token = None
        if header == '+':
            symbol = symbol.replace('+', ' ')
            # First consume the potential symbol bufferized
            if (strings != '-' * self.nb_strings) and (len(paths) == 0):
                self.frets_buffer.append(symbol)
                # '+' is is considered as end of symbol, so force symbol treatment below
                strings = '-' * self.nb_strings
            header = ''
            # Then append the tie
            trailer_token = TieToken('Tie')
        elif header == '^':
            symbol = symbol.replace('^', ' ')
            # First consume the potential symbol bufferized
            if (strings != '-' * self.nb_strings) and (len(paths) == 0):
                # Bufferize the content of symbol
                self.frets_buffer.append(symbol)
                # '^' is is considered as end of symbol, so force symbol treatment below
                strings = '-' * self.nb_strings
            header = ''
            trailer_token = TrioletToken('Triolet')
        if (strings == '-' * self.nb_strings):
            if (len(header) == 0):
                # Pure separator: end of "note"
                self._send_symbol()
            elif header in self.durations:
                # New note --> send previous note and store current symbol 
                self._send_symbol()
                self.token_buffer.append(TiedNoteToken(header))
            else:
                # Just bufferize the symbol
                self.frets_buffer.append(symbol)
        elif (strings == '||||') or (strings == '+||+') or (strings == '-|||'):
            self._send_symbol()
            self._consume_measure(header, strings)
        elif '::' in strings:
            if len(self.frets_buffer) == 0:
                logging.error('Invalid time signature')
            self.token_buffer.append(TimeSignatureToken(self.frets_buffer))
            self.frets_buffer = []
        elif '**' in strings:
            self.token_buffer.append(EndRepetitionToken())
        elif len(paths) > 0:
            self._send_symbol()
            self.token_buffer.append(BtabTokenizer.note_paths[paths[0]]())
        else:
            self.frets_buffer.append(symbol)
        if trailer_token is not None:
            self.token_buffer.append(trailer_token)
        return None

    def end(self):
        return EndToken()
