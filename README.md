# genovation-keypads
Description of Genovation Keypad binaries and configuration process
The Genovation Controlpad CPxx series is programmed by scancodes following, for the most part the AT Keyboard Scan Codes (Set 2). See https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html

# Sticking Points
The are a few notable additions/changes worth mentioning. After the `.ckd` file is compiled to a `.bin`, a few codes change:
 * `0xF0` ("release" code) -> changes to `0xE3`. The standard defines `0xF0 0x12` as "release left shift". In the `.bin` format, this will change to `0xE3 0x12` with no other indication.
 * `0xE2 0x01 0x{pp}` = "Delay `pp` * 4 milliseconds" e.g. `0xE2 0x01 0x0A` => Delay 40 milliseconds (`0x0A` = dec. 10)
 * * Maximum Value is `0x7d` (500 milliseconds). Longer delays are created by chaining these together.
 * The "Description" is completely dropped

# Control Characters
There are 5 control characters in the binary:
* `0xE0` -> Control character used for "special keys" (explained in https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html)
* `0xE2` -> Control character for something the keypad does. Action defined by next byte
** `0xE2 0x01` -> Delay, as described above
** `0xE2 0x04/0x05/0x06` -> Controls LED on keypad
* `0xE3` -> Control character used to indicate "release" of following keycode, described above
* `0xE4` -> Separator character in binary
** `0xE4 0x01` marks the header
** `0xE4 0x02` marks a keypad input
* `0xE5` -> Terminator character. When this is sent to the keypad, it closes the usb connection and restarts.

# Format of Binary
## Header
more later...
## Keycodes
more in a bit...
