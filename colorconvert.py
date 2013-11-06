# colorconvert (1.1)
# coding: utf-8
#
# Converts CSS colors from hex to rgb(a), from rgb(a) to hsl(a), and from hsl(a)
# to hex, while preserving alpha channels.
#
# More information about color conversions (specifically rgb to hsl and back)
# can be found here: http://en.wikipedia.org/wiki/HSL_and_HSV#From_HSL

import sublime
import sublime_plugin
import re


class colorconvertCommand(sublime_plugin.TextCommand):
    """Converts a CSS color from hex to rgba to hsla to hex (etc).

    Attributes:
        sublime_plugin.TextCommand: Sublime Text 2 class basis.

    """

    # Initlialization.
    def __init__(self, view):
        """Initialization of the class.

        Attributes:
            self: The colorconvertCommand object.
            view: The current view.

        """

        # Store the view and color channels. The channels are used for
        # calculating with non-rounded floats.
        self.view = view

        self.r = 0
        self.g = 0
        self.b = 0

        self.h = 0.0
        self.s = 0.0
        self.l = 0.0

        self.alpha = 1.0


    def hexToRgb(self, r, g, b):
        """Converts a hex value to an rgb value.

        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (00 - ff)
            g:    The value of the green channel (00 - ff)
            b:    The value of the blue channel  (00 - ff)

        """

        r = (int(r, 16))
        g = (int(g, 16))
        b = (int(b, 16))

        return [r, g, b, self.alpha]


    def rgbToHex(self, r, g, b, a):
        """Converts an rgb(a) value to a hex value.

        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (0 - 255)
            g:    The value of the green channel (0 - 255)
            b:    The value of the blue channel  (0 - 255)
            a:    The value of the alpha channel (0.0 - 1.0)

        """

        r = hex(r)[2:].zfill(2)
        g = hex(g)[2:].zfill(2)
        b = hex(b)[2:].zfill(2)

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            self.alpha = a

        # If a short notation is possible, splice the values.
        if (r[0:1] == r[1:2]) and (g[0:1] == g[1:2]) and (b[0:1] == b[1:2]):
            r = r[1:]
            g = g[1:]
            b = b[1:]

        return [r, g, b]


    def rgbToHsl(self, r, g, b, a):
        """Converts an rgb(a) value to an hsl(a) value.

        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (0 - 255)
            g:    The value of the green channel (0 - 255)
            b:    The value of the blue channel  (0 - 255)
            a:    The value of the alpha channel (0.0 - 1.0)

        """

        r = float(r) / 255.0
        g = float(g) / 255.0
        b = float(b) / 255.0

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            self.alpha = a

        # Calculate the hsl values.
        cmax = max(r, g, b)
        cmin = min(r, g, b)

        delta = cmax - cmin

        # Hue
        if (cmax == r) and (delta > 0):
            h = 60 * (((g - b) / delta) % 6.0)

        elif (cmax == g) and (delta > 0):
            h = 60 * (((b - r) / delta) + 2.0)

        elif (cmax == b) and (delta > 0):
            h = 60 * (((r - g) / delta) + 4.0)

        elif (delta == 0):
            h = 0

        # Lightness
        l = (cmax + cmin) / 2.0

        # Saturation
        if (delta == 0):
            s = 0

        else:
            s = (delta / (1 - abs((2 * l) - 1)))

        s = s * 100.0
        l = l * 100.0

        # Store the hsl values globally, so we can use the unrounded versions
        # to convert them back.
        self.h = h
        self.s = s
        self.l = l

        return [h, s, l, self.alpha]


    def hslToRgb(self, h, s, l, a):
        """Converts an hsl(a) value to an rgb(a) value.

        Attributes:
            self: The Regionset object.
            h:    The value of the hue channel        (0.0 - 360.0)
            s:    The value of the saturation channel (0.0 - 100.0)
            l:    The value of the lightness channel  (0.0 - 100.0)
            a:    The value of the alpha channel      (0.0 - 1.0)

        """

        h = float(h)
        s = float(s) / 100
        l = float(l) / 100

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            self.alpha = a

        # Calculate the rgb values.
        c = (1 - abs((2 * l) - 1)) * s
        x = c * (1 - abs(((h / 60.0) % 2) - 1))
        m = l - (c / 2)

        if (h >= 0) and (h < 60):
            r = c
            g = x
            b = 0

        elif (h >= 60) and (h < 120):
            r = x
            g = c
            b = 0

        elif (h >= 120) and (h < 180):
            r = 0
            g = c
            b = x

        elif (h >= 180) and (h < 240):
            r = 0
            g = x
            b = c

        elif (h >= 240) and (h < 300):
            r = x
            g = 0
            b = c

        elif (h >= 300) and (h < 360):
            r = c
            g = 0
            b = x

        r = int((r + m) * 255.0)
        g = int((g + m) * 255.0)
        b = int((b + m) * 255.0)

        return [r, g, b, self.alpha]


    # Main function.
    def run(self, edit):
        """Default function that runs when colorconvert is called.

        Attributes:
            self: The Regionset object.
            edit: The Edit object.

        """

        sels = self.view.sel()

        for sel in sels:

            # Get the selection and its length.
            str = self.view.substr(sel)
            str_len = len(str)

            # Define the regular expressions to test hex/rgb(a).
            reg_hex = '^[\#]?([\dabcdefABCDEF]{3}){1,2}$'
            reg_rgb = ('^rgb[a]?\((\s*\d+\s*),(\s*\d+\s*),(\s*\d+\s*),'
                       '?(\s*(0?.?\d)+\s*)?\)$')
            reg_hsl = ('^hsl[a]?\((\s*\d+.?\d+\s*),(\s*\d+.?\d+\%\s*),(\s*\d+.?\d+\%\s*),'
                       '?(\s*(0?.?\d)+\s*)?\)$')

            hex_match = re.match(reg_hex, str)
            rgb_match = re.match(reg_rgb, str)
            hsl_match = re.match(reg_hsl, str)


            # If a hexadecimal number is found, convert it to an rgb value.
            if hex_match is not None:

                # Expand the selection if we're dealing with hex, but the
                # hashtag is not yet part of the selection.
                if (str_len == 3) or (str_len == 6):
                    start = sel.begin() - 1
                    end = sel.end()

                    # Update the selection.
                    self.view.sel().add(sublime.Region(start, end))
                    sel = sublime.Region(start, end)

                # If the hashtag is already part of the selection, make sure it
                # gets stripped.
                else:
                    str = str[1:]

                if (len(str) == 3):
                    r = str[0:1] * 2
                    g = str[1:2] * 2
                    b = str[2:3] * 2

                else:
                    r = str[0:2]
                    g = str[2:4]
                    b = str[4:6]

                # Get the rgb(a) values and output them to the current
                # selection.
                rgba_vals = self.hexToRgb(r, g, b)
                output = 'rgba(%d, %d, %d, %s)' % (rgba_vals[0], rgba_vals[1],
                                                   rgba_vals[2], rgba_vals[3])
                self.view.replace(edit, sel, output)


            # If an rgb(a) value is found, convert it to an hsla value.
            elif rgb_match is not None:

                # Get all the color channels.
                r = int(rgb_match.group(1), 10)
                g = int(rgb_match.group(2), 10)
                b = int(rgb_match.group(3), 10)

                # If applicable, also get the alpha channel.
                if (rgb_match.group(4) is not None):
                    a = float(rgb_match.group(4))

                else:
                    a = self.alpha

                # Get the hsl(a) values and output them to the current
                # selection.
                hsla_vals = self.rgbToHsl(r, g, b, a)
                output = 'hsla(%.1f, %.1f%%, %.1f%%, %s)' % (hsla_vals[0],
                                                             hsla_vals[1],
                                                             hsla_vals[2],
                                                             hsla_vals[3])
                self.view.replace(edit, sel, output)


            # If an hsl(a) value is found, convert it to a hex value.
            elif hsl_match is not None:

                # Get all the color channels.
                h = float(hsl_match.group(1))
                s = float(hsl_match.group(2).strip('%'))
                l = float(hsl_match.group(3).strip('%'))

                # If applicable, also get the alpha channel.
                if (hsl_match.group(4) is not None):
                    a = float(hsl_match.group(4))

                else:
                    a = self.alpha

                # Get the rgb(a) values, then the hex values and output them to
                # the current selection.
                rgba_vals = self.hslToRgb(h, s, l, a)
                hex_vals = self.rgbToHex(rgba_vals[0], rgba_vals[1],
                                         rgba_vals[2], rgba_vals[3])
                output = '#%s%s%s' % (hex_vals[0], hex_vals[1], hex_vals[2])
                self.view.replace(edit, sel, output)
