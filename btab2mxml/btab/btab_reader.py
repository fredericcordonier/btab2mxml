

class BtabReaderBadReadModeException(Exception):
    pass


class BtabReader:
    def __init__(self, input_file_name):
        self.read_index = 0
        self.input_file = open(input_file_name)
        self.end_of_file = False
        self.buffer = ''
        self.staff_line_index = 0
        self.staff_line_length = 0
        self.staff_lines = [[]]

    def read_line(self):
        if len(self.buffer) == 0:
            self.buffer = self.input_file.readline()
        if self.buffer is None:
            self.end_of_file = True
            return ''
        self.buffer = self.buffer.replace('\n', '')
        return self.buffer

    def consume_line(self):
        self.buffer = ''

    def get_next_score_symbol(self):
        if self.staff_line_index == self.staff_line_length:
            # Buffer entirely read --> refill
            self.staff_lines = []
            line = ''
            while len(line) == 0:
                line = self.read_line().replace('\n', '')
                self.consume_line()
            while line:
                if (line == 'end') or ((len(line) > 0) and (line[0] == '=')):
                    # End of score
                    line = None
                else:
                    self.staff_lines.append(line)
                    line = self.read_line()
                    self.consume_line()
            if len(self.staff_lines) > 0:
                lines_length = max([len(line) for line in self.staff_lines])
                # Adjust lines length
                self.staff_lines = [line.ljust(lines_length, ' ') for line in self.staff_lines]
                self.staff_line_length = lines_length
            self.staff_line_number = len(self.staff_lines)
            self.staff_line_index = 0
        if self.staff_line_length == 0 or len(self.staff_lines) == 0:
            # End of score
            return None
        symbol = ''.join([l[self.staff_line_index] for l in self.staff_lines])
        self.staff_line_index += 1
        return symbol

    def is_eof(self):
        return self.end_of_file
