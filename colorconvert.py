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
import math


# Global color channel values.
_hr = None
_hg = None
_hb = None

_r = None
_g = None
_b = None

_h = None
_s = None
_l = None

_alpha = 1.0
_alpha_enabled = True


class colorconvertCommand(sublime_plugin.TextCommand):
    """Converts a CSS color from hex to rgba to hsla to hex (etc).

    Attributes:
        sublime_plugin.TextCommand: Sublime Text class basis.

    """

    # Initlialization.
    def __init__(self, view):
        """Initialization of the class.

        Attributes:
            self: The colorconvertCommand object.
            view: The current view.

        """

        # Store the view.
        self.view = view

        # Load settings
        settings = sublime.load_settings("colorconvert.sublime-settings")
        settings.add_on_change("enable_alpha", loadSettings)

        loadSettings()


    def hueToRgb(self, v1, v2, vH):
        """Assists with converting hsl to rgb values.

        Attributes:
            self: The Regionset object.
            v1:   The first part of the hsl collection
            v2:   The second part of the hsl collection
            vH:   The thrid part of the hsl collection

        """

        if vH < 0:
            vH += 1

        if vH > 1:
            vH -= 1

        if ((6 * vH) < 1):
            return (v1 + (v2 - v1) * 6 * vH)

        if ((2 * vH) < 1):
            return v2

        if ((3 * vH) < 2):
            return (v1 + (v2 - v1) * ((2 / 3) - vH) * 6)

        return v1


    def hexToRgb(self, hr, hg, hb):
        """Converts a hex value to an rgb value.

        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (00 - ff)
            g:    The value of the green channel (00 - ff)
            b:    The value of the blue channel  (00 - ff)

        """

        global _r
        global _g
        global _b

        global _alpha

        r = (int(hr, 16))
        g = (int(hg, 16))
        b = (int(hb, 16))

        if _r is None:

            _r = r
            _g = g
            _b = b

        return [r, g, b, _alpha]


    def rgbToHex(self, r, g, b, a):
        """Converts an rgb(a) value to a hex value.

        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (0 - 255)
            g:    The value of the green channel (0 - 255)
            b:    The value of the blue channel  (0 - 255)
            a:    The value of the alpha channel (0.0 - 1.0)

        """

        global _alpha

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            _alpha = a

        # Convert the channels' values to hex values.
        r = hex(r)[2:].zfill(2)
        g = hex(g)[2:].zfill(2)
        b = hex(b)[2:].zfill(2)

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

        global _h
        global _s
        global _l

        global _alpha

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            _alpha = a

        r = float(r) / 255.0
        g = float(g) / 255.0
        b = float(b) / 255.0

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

        # Store the hsl values globally.
        if _h is None:

            _h = h
            _s = s
            _l = l

        return [h, s, l, _alpha]


    def hslToRgb(self, h, s, l, a):
        """Converts an hsl(a) value to an rgb(a) value.

        Attributes:
            self: The Regionset object.
            h:    The value of the hue channel        (0.0 - 360.0)
            s:    The value of the saturation channel (0.0 - 100.0)
            l:    The value of the lightness channel  (0.0 - 100.0)
            a:    The value of the alpha channel      (0.0 - 1.0)

        """

        global _alpha

        h = float(h)
        s = float(s) / 100
        l = float(l) / 100

        # Get the alpha channel and store it globally (if present).
        if a is not None:
            _alpha = a

        # Unsaturated colors have equal rgb channels.
        if s is 0:
            r = l * 255
            g = l * 255
            b = l * 255

        # Magic :)
        else:

            if l < 0.5:
                var_2 = l * (1 + s)

            else:
                var_2 = (l + s) - (s * l)

            var_1 = 2 * l - var_2

            r = 255 * self.hueToRgb(var_1, var_2, (h + (1 / 3)))
            g = 255 * self.hueToRgb(var_1, var_2, h)
            b = 255 * self.hueToRgb(var_1, var_2, (h - (1 / 3)))

        r = int(math.ceil(r))
        g = int(math.ceil(g))
        b = int(math.ceil(b))

        return [r, g, b, _alpha]


    # Main function.
    def run(self, edit):
        """Default function that runs when colorconvert is called.

        Attributes:
            self: The Regionset object.
            edit: The Edit object.

        """

        sels = self.view.sel()

        # Global values for the hex parts of rgb.
        global _hr
        global _hg
        global _hb

        # Global values for rgb channels.
        global _r
        global _g
        global _b

        # Global values for the hsl channels.
        global _h
        global _s
        global _l

        # Global values for the alpha channel.
        global _alpha
        global _alpha_enabled

        for sel in sels:

            # Get the selection and its length.
            str = self.view.substr(sel)
            str_len = len(str)

            # Define the regular expressions to test hex/rgb(a).
            reg_hex = '^[\#]?([\dabcdefABCDEF]{3}){1,2}$'
            reg_rgb = ('^rgb[a]?\((\s*\d+\s*),(\s*\d+\s*),(\s*\d+\s*),'
                       '?(\s*(0?.?\d)+\s*)?\)$')
            reg_hsl = ('^hsl[a]?\((\s*\d+.?\d?\s*),(\s*\d+.?\d?\%\s*),(\s*\d+.?\d?\%\s*),'
                       '?(\s*\d+.?\d?\s*)?\)$')

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

                # Store the hex channel values globally.
                if _hr is None:
                    _hr = r
                    _hg = g
                    _hb = b

                # If global rgb values are present, use those for speed and
                # accuracy. Otherwise convert the values.
                if _r is not None:

                    rgba_vals = [_r, _g, _b, _alpha]

                else:

                    rgba_vals = self.hexToRgb(_hr, _hg, _hb)

                # Write the output to the selection.
                if _alpha_enabled is True:

                    output = 'rgba(%d, %d, %d, %s)' % (rgba_vals[0],
                                                       rgba_vals[1],
                                                       rgba_vals[2],
                                                       rgba_vals[3])
                else:

                    output = 'rgba(%d, %d, %d)' % (rgba_vals[0], rgba_vals[1],
                                                   rgba_vals[2])

                self.view.replace(edit, sel, output)


            # If an rgb(a) value is found, convert it to an hsla value.
            elif rgb_match is not None:

                # Get all the color channels.
                r = int(rgb_match.group(1), 10)
                g = int(rgb_match.group(2), 10)
                b = int(rgb_match.group(3), 10)

                # Store the rgb channel values globally.
                if _r is None:
                    _r = r
                    _g = g
                    _b = b

                # If applicable, also get the alpha channel.
                if (rgb_match.group(4) is not None):
                    a = float(rgb_match.group(4))

                else:
                    a = _alpha

                # If global hsl values are present, use those for speed and
                # accuracy. Otherwise convert the values.
                if _h is not None:

                    hsla_vals = [_h, _s, _l, _alpha]

                else:

                    hsla_vals = self.rgbToHsl(r, g, b, a)

                # Write the output to the selection.
                if _alpha_enabled is True:

                    output = 'hsla(%.1f, %.1f%%, %.1f%%, %s)' % (hsla_vals[0],
                                                                 hsla_vals[1],
                                                                 hsla_vals[2],
                                                                 hsla_vals[3])

                else:

                    output = 'hsla(%.1f, %.1f%%, %.1f%%)' % (hsla_vals[0],
                                                             hsla_vals[1],
                                                             hsla_vals[2])

                self.view.replace(edit, sel, output)


            # If an hsl(a) value is found, convert it to a hex value.
            elif hsl_match is not None:

                # Get all the color channels.
                h = float(hsl_match.group(1).strip('%'))
                s = float(hsl_match.group(2).strip('%'))
                l = float(hsl_match.group(3).strip('%'))

                # Store the hsl channel values globally.
                if _h is None:
                    _h = h
                    _s = s
                    _l = l

                # If applicable, also get the alpha channel.
                if (hsl_match.group(4) is not None):
                    a = float(hsl_match.group(4))

                else:
                    a = _alpha

                # If global hex or rgb values are present, use those for speed
                # and accuracy. Otherwise convert the values.
                if _hr is not None:

                    hex_vals = [_hr, _hg, _hb, _alpha]

                else:

                    if _r is not None:

                        rgba_vals = [_r, _g, _b, _alpha]

                    else:

                        rgba_vals = self.hslToRgb(h, s, l, a)


                    hex_vals = self.rgbToHex(rgba_vals[0], rgba_vals[1],
                                             rgba_vals[2], rgba_vals[3])
                
                # Write the output to the selection.
                output = '#%s%s%s' % (hex_vals[0], hex_vals[1], hex_vals[2])
                self.view.replace(edit, sel, output)


class colorconvertEvents(sublime_plugin.EventListener):
    """Event listener for the ColorConvert plugin.

    Attributes:
        sublime_plugin.EventListener: Sublime Text class basis.

    """

    def on_selection_modified(self, view):
        """Listener for selection change.

        Attributes:
            self: The colorconvertCommand object.
            view: The current view.

        """

        sels = view.sel()

        global _hr
        global _hg
        global _hb

        global _r
        global _g
        global _b

        global _h
        global _s
        global _l

        global _alpha

        # If the selection changed to a 'cursor' (e.g. no selection at all)
        # then we reset the global values.
        if len(sels) is 1 and sels[0].empty():

            _hr = None
            _hg = None
            _hb = None

            _r = None
            _g = None
            _b = None

            _h = None
            _s = None
            _l = None

            alpha = 1.0


def loadSettings():
    """Loads settings from the .sublime-settings file

    Attributes:
        sublime_plugin.EventListener: Sublime Text class basis.

    """
    
    global _alpha_enabled

    settings = sublime.load_settings("colorconvert.sublime-settings")

    _alpha_enabled = settings.get("enable_alpha")