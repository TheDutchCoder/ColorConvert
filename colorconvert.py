# colorconvert
# Converts CSS hex colors to rgb values and rgb(a) to hex.

import sublime
import sublime_plugin
import re

# Converts CSS colors rgb(a) <-> hex
#
# Examples:
# #000
# #f0e
# #f2e094
# rgb(128, 0, 0)
# rgb(0, 9, 126)
# rgba(120, 34, 19, 0.2)
#
# To-do:
#   - color cycling
#   - color name support


class colorconvertCommand(sublime_plugin.TextCommand):
    """Converts a CSS hex color to rgba, or rgb(a) to hex.

    Attributes:
        sublime_plugin.TextCommand: Sublime Text 2 class basis.

    """

    def hexToRgb(self, str, str_len):
        """Converts a hex value to an rgb value.

        Attributes:
            self: The Regionset object.
            str: The selected string.
            str_len: Length of the selected string.

        """

        # If hex is shorthand, convert to a double value first.
        if str_len == 3:
            val_1 = (int(str[0:1] * 2, 16))
            val_2 = (int(str[1:2] * 2, 16))
            val_3 = (int(str[2:3] * 2, 16))

        else:
            val_1 = (int(str[0:2], 16))
            val_2 = (int(str[2:4], 16))
            val_3 = (int(str[4:6], 16))

        # Return the preformatted string with the new values.
        return 'rgb(%d, %d, %d)' % (val_1, val_2, val_3)

    def rgbToHex(self, rgb_match):
        """Converts an rgb(a) value to a hex value.

        Attributes:
            self: The Regionset object.
            rgb_match: The reg exp collection of matches.

        """

        # Convert all values to 10-base integers, strip the leading characters,
        # convert to hex and fill with leading zero's.
        val_1 = hex(int(rgb_match.group(1), 10))[2:].zfill(2)
        val_2 = hex(int(rgb_match.group(2), 10))[2:].zfill(2)
        val_3 = hex(int(rgb_match.group(3), 10))[2:].zfill(2)

        # Return the proformatted string with the new values.
        return '#%s%s%s' % (val_1, val_2, val_3)

    # Main function.
    def run(self, edit):
        """Default function that runs when colorconvert is called.

        Attributes:
            self: The Regionset object.
            edit: The Edit objtec.

        """

        sels = self.view.sel()

        for sel in sels:

            # Get the selection and its length.
            str = self.view.substr(sel)
            str_len = len(str)

            # Define the regular expressions to test hex/rgb(a).
            reg_hex = '^[\#]?([\dabcdefABCDEF]){3,6}'
            reg_rgb = '^rgb[a]?\((\s*\d+\s*),(\s*\d+\s*),(\s*\d+\s*),?(\s*(0?.?\d)+\s*)?\)$'

            hex_match = re.match(reg_hex, str)
            rgb_match = re.match(reg_rgb, str)

            # If a hexadecimal number is found, convert it to an rgb value.
            if hex_match is not None:

                # Expand the selection if we're dealing with hex, but the
                # hashtag is not part of the selection.
                if str_len == 3 or str_len == 6:
                    start = sel.begin() - 1
                    end = sel.end()

                    # Update the selection.
                    self.view.sel().add(sublime.Region(start, end))
                    sel = sublime.Region(start, end)

                else:
                    str = str[1:]

                # Replace the current selection with the rgb value.
                self.view.replace(edit, sel, self.hexToRgb(str, str_len))

            # If an rgb value is found, convert it to a hexadecimal number.
            elif rgb_match is not None:

                # Replace the current selection with the hex value.
                self.view.replace(edit, sel, \
                                  self.rgbToHex(rgb_match))
