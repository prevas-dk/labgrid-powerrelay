OUT     = 0
IN      = 1
HIGH    = True
LOW     = False

class GPIOLineInUsedError(Exception):
    pass

class GPIOInvalidLineError(Exception):
    pass

class BaseGPIO():
    """
        Base class for implementing simple digital IO for a platform.
        Implementors are expected to subclass from this and provide an implementation
        of the setup, output, and input functions.
    """
    def lines(self):
        """ Returns the number of lines """
        raise NotImplementedError

    def setup(self, chip, line, mode):
        """Set the input or output mode for a specified line.  Mode should be
        either OUT or IN."""
        raise NotImplementedError

    def output(self, chip, line, value):
        """Set the specified line the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high)."""
        raise NotImplementedError

    def input(self, chip, line):
        """Read the specified line and return HIGH/true if the line is pulled high,
        or LOW/false if pulled low."""
        raise NotImplementedError

    def set_high(self, chip, line):
        """Set the specified line HIGH."""
        self.output(chip,line, HIGH)

    def set_low(self, chip, line):
        """Set the specified line LOW."""
        self.output(chip,line, LOW)

    def is_high(self, chip, line):
        """Return true if the specified line is pulled high."""
        return self.input(chip,line) == HIGH

    def is_low(self, chip, line):
        """Return true if the specified line is pulled low."""
        return self.input(chip,line) == LOW

    def is_output(self, chip, line):
        """Return true if the line has direction output"""
        raise NotImplementedError

    def is_input(self, chip, line):
        """Return true if the line has direction input"""
        return not(is_output(chip,line))

    def value(self,chip, line):
        """Return the current value of the line"""
        raise NotImplementedError
