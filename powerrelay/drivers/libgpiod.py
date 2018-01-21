import sys
from ctypes import *
from ctypes.util import find_library
from .gpio import *

gpiod = CDLL(find_library("gpiod"))

NAME_ARRAY = c_char * 32
CONSUMER_ARRAY = c_char * 32

class gpiod_line(Structure):
    pass

class gpiod_chip(Structure):
    pass

gpiod_line_p = POINTER(gpiod_line)
gpiod_chip_p = POINTER(gpiod_chip)

chip_open_by_path = gpiod.gpiod_chip_open_by_name
chip_open_by_path.argtypes = [c_char_p]
chip_open_by_path.restype = gpiod_chip_p

chip_open_by_name = gpiod.gpiod_chip_open_by_name
chip_open_by_name.argtypes = [c_char_p]
chip_open_by_name.restype = gpiod_chip_p

chip_open_by_number = gpiod.gpiod_chip_open_by_number
chip_open_by_number.argtypes = [c_uint]
chip_open_by_number.restype = gpiod_chip_p

chip_close = gpiod.gpiod_chip_close
chip_close.argtypes = [gpiod_chip_p]
chip_close.restype = None

chip_num_lines = gpiod.gpiod_chip_num_lines
chip_num_lines.argtypes = [gpiod_chip_p]
chip_num_lines.restype = c_uint

chip_name = gpiod.gpiod_chip_name
chip_name.argtypes = [gpiod_chip_p]
chip_name.restype = c_char_p

chip_get_line = gpiod.gpiod_chip_get_line
chip_get_line.argtypes = [gpiod_chip_p, c_uint]
chip_get_line.restype = POINTER(gpiod_line)

line_release = gpiod.gpiod_line_release
line_release.argtypes = [gpiod_line_p]
#line_is_used = gpiod.gpiod_line_is_used
#line_is_used.argtypes = [gpiod_line_p]
#line_is_used.restype = c_bool

line_active_state = gpiod.gpiod_line_active_state
line_active_state.argtypes = [gpiod_line_p]
line_active_state.restype = c_int

line_is_open_drain = gpiod.gpiod_line_is_open_drain
line_is_open_drain.argtypes = [gpiod_line_p]
line_is_open_drain.restype = c_bool

line_is_open_source = gpiod.gpiod_line_is_open_drain
line_is_open_source.argtypes = [gpiod_line_p]
line_is_open_source.restype = c_bool

line_get_direction = gpiod.gpiod_line_direction
line_get_direction.argtypes = [gpiod_line_p]
line_get_direction.restype = c_int

line_get_value = gpiod.gpiod_line_get_value
line_get_value.argtypes = [gpiod_line_p]
line_get_value.restype = c_int

line_set_value = gpiod.gpiod_line_set_value
line_set_value.argtypes = [gpiod_line_p]
line_set_value.restype = c_int


#
# Request
#
class gpiod_request_config(Structure):
    _fields_ = [('consumer', c_char_p),
                ('request_type', c_int),
                ('flags', c_int)]

gpiod_request_p = POINTER(gpiod_request_config)

line_request = gpiod.gpiod_line_request
line_request.argtypes = [gpiod_line_p, gpiod_request_p, c_int]
line_request.restype = c_int

line_request_input = gpiod.gpiod_line_request_input
line_request_input.argtypes = [gpiod_line_p, c_char_p]
line_request_input.restype = c_int

line_request_output = gpiod.gpiod_line_request_output
line_request_output.argtypes = [gpiod_line_p, c_char_p, c_int]
line_request_output.restype = c_int


#
# libgpiod implementation
#
class GPIO(BaseGPIO):
    """ Initialize GPIO """
    def __init__(self, chip):
        super().__init__()
        if not isinstance(chip, str):
            raise ValueError("chip must be a string")

        self.chipname = chip
        try:
            self.chip = chip_open_by_name(chip.encode())
            if not self.chip:
                raise RuntimeError("failed to open chip")
            self.chip_lines = chip_num_lines(self.chip)
        except:
            pass

    def lines(self):
        """ Read the available lines on the chip """
        if self.chip == None:
            raise ValueError("error")
        else:
            return chip_num_lines(self.chip)

    def setup(self, line, mode):
        """Set the input or output mode for a specified line.  Mode should be
        either OUT or IN."""
        if line > self.chip_lines:
            raise ValueError("invalid line offset")
        line = chip_get_line(self.chip, line)
        if mode == OUT:
            line_request_output(line, "GPIO", 0)
        else:
            line_request_input(line, "GPIO")

    def output(self, line, value):
        """Set the specified line the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high)."""
        raise NotImplementedError

    def input(self, line):
        """Read the specified line and return HIGH/true if the line is pulled high,
        or LOW/false if pulled low."""
        raise NotImplementedError

    def set_high(self, line):
        """Set the specified line HIGH."""
        self.output(line, HIGH)

    def set_low(self, line):
        """Set the specified line LOW."""
        self.output(line, LOW)

    def is_high(self, line):
        """Return true if the specified line is pulled high."""
        return self.input(line) == HIGH

    def is_low(self, line):
        """Return true if the specified line is pulled low."""
        return self.input(line) == LOW

    def is_output(self,line):
        """Return true if the line has direction output"""
        raise NotImplementedError

    def is_input(self,line):
        """Return true if the line has direction input"""
        return not(is_output(line))

    def value(self,line):
        """Return the current value of the line"""
        raise NotImplementedError
