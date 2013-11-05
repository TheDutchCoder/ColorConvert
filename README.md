ColorConvert
============

A Sublime Text plugin that converts CSS numerical color values.
You can convert any hex, rgb(a) or hsl(a) color in the following sequence: hex -> rgba -> hsla -> hex (etc).

## Installation
You can easily install the pluing through Will Bond's excellent Package Control (https://sublime.wbond.net/).
If you want to install this plugin manually for some reason, simply clone this repo into your packages directory (make sure not to put it in the user sub dir).

## Instructions
1. Select a color declaration (e.g. '#ff0022', 'rgb(120, 0, 12)', or 'hsla(320, 75%, 10%, 0.2)')
2. Hit ctrl+shift+c by default (cmd+shift+c on Mac OS) to convert to the next type (hex -> rgba -> hsla -> hex -> etc).

## Supported Features
- Convert hex values to rgba
- Convert rgb(a) values to hsla
- Convert hsl(a) values to hex
- Remembers the alpha value of a selection (e.g. when 'rgba(120, 0, 12, 0.2)' is converted to any other value, the '0.2' alpha value will be remembered, even if you convert the value to hex)

## Planned Features
- Convert all colors equal to the selected one in the document (milestone 1.2)

## Notes
1. CSS color names (e.g. 'red', 'transparent', etc) are currently not supported (not planning to unless there's a high demand).
2. Whenever possible, the plugin will output the shorthand hex value (e.g. '#000' instead of '#000000').
3. All 'rgb' and 'hsl' values will always be written as 'rgba' and 'hsla'. Every browser that supports rgb/hsl also supports rgba/hsla, so opaque colors simple get an alpha of 1.0.
4. The output for hsl and alpha channels is in floating point, to ensure a little more accuracy.

## Examples
```css
color: rgba(128, 0, 12, 0.5);
```

Will convert to:
```css
color: hsla(354.4, 100.0%, 25.1%, 0.5);
color: #80000b;
color: rgba(128, 0, 12, 0.5);
```
