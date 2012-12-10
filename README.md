ColorConvert
============

A Sublime Text 2 plugin that converts CSS colors from hex to rgb and back.

## Installation
I've submitted the plugin to Package Control by wbond, but until it's implemented, you can just clone this repo in your sublime text 2 packages directory (don't put it in the User sub dir).

## Instructions
Hit ctrl+shift+c by default to switch between values.

    color: #f20645
    
    /* Select the hex, either with, or without the hash.
       It will be converted to this: */
    
    color: rgb(242, 6, 69)

This also works for rgba values, although the alpha channel won't be stored.