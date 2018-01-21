import sys
from .gpio import *

gpio_chips = [
    {
        0: {'direction': OUT, 'value': 0},
        1: {'direction': OUT, 'value': 1}
    },
    {
        0: {'direction': OUT, 'value': 0},
        1: {'direction': OUT, 'value': 1}
    }
]

class GPIO(BaseGPIO):
    """ Initialize GPIO """
    def __init__(self, chips):
        super().__init__()
        if not isinstance(chips, set):
            raise ValueError("chips must be a dict")

        self.chips = gpio_chips
        self.chip_lines = len(gpio_chips[0])

    def lines(self,chip):
        """ Read the available lines on the chip """
        if self.chip == None:
            raise ValueError("error")
        else:
            return len(gpio_chips[chip])

    def setup(self,chip,line,mode):
        """
            Set the input or output mode for a specified line.  Mode should be
            either OUT or IN.
        """
        if len(self.chips[chip]) < line:
            raise ValueError("invalid line offset")
        chip_line = gpio_chips[chip][line]
        if mode == OUT:
            chip_line['direction'] = OUT
        else:
            chip_line['direction'] = IN

    def output(self,chip,line,value):
        """
            Set the specified line the provided high/low value.
            Value should be either HIGH/LOW or a boolean (true = high).
        """
        if line > len(self.chips[chip]):
            raise ValueError("invalid line offset")
        chip_line = gpio_chips[chip][line]
        if chip_line:
            chip_line['direction'] = OUT
            chip_line['value'] = value

    def input(self,chip,line):
        """
            Read the specified line and return HIGH/true if the line is pulled high,
            or LOW/false if pulled low.
        """
        if line > len(self.chips[chip]):
            raise ValueError("invalid line offset")
        chip_line = gpio_chips[chip][line]
        if chip_line:
            chip_line['direction'] = IN
            return chip_line['value']

    def set_high(self,chip,line):
        """Set the specified line HIGH."""
        self.output(chip,line, HIGH)

    def set_low(self,chip,line):
        """Set the specified line LOW."""
        self.output(chip,line, LOW)

    def is_high(self,chip,line):
        """Return true if the specified line is pulled high."""
        return self.input(chip,line) == HIGH

    def is_low(self,chip,line):
        """Return true if the specified line is pulled low."""
        return self.input(chip,line) == LOW

    def is_output(self,chip,line):
        """Return true if the line has direction output"""
        if line > len(self.chips[chip]):
            raise ValueError("invalid line offset")
        return gpio_chips[chip][line]['direction'] == OUT

    def is_input(self,chip,line):
        """Return true if the line has direction input"""
        return not(self.is_output(chip,line))

    def value(self,chip,line):
        """Return the current value of the line"""
        if line > len(self.chips[chip]):
            raise ValueError("invalid line offset")
        return gpio_chips[chip][line]['value']
