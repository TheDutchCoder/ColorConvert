ColorConvert
============

A Sublime Text 2 plugin that converts CSS colors from hex to rgb and back.

## Installation
I've submitted the plugin to Package Control by wbond, but until it's implemented, you can just clone this repo in your sublime text 2 packages directory (don't put it in the User sub dir).

## Instructions
Hit ctrl+shift+c by default (cmd+shift+c on Mac OS) to switch between values.

    color: #f20645
    
    /* Select the hex, either with, or without the hash.
       It will be converted to this: */
    
    color: rgb(242, 6, 69)
    
    /* Pressing ctrl+shift+c again will convert to rgba */
    
    color: rgba(242, 6, 69, 1)
    
    /* Another ctrl+shift+c and you're back at hex */
    
    color: #f20645

Please note that alpha channel values will not be stored and will automatically revert to "1".

## To-do
- Color code support (e.g. 'red')
