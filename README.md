# genovation-keypads
Description of Genovation Keypad binaries and configuration process
The Genovation Controlpad CPxx series is programmed by scancodes following, for the most part the AT Keyboard Scan Codes (Set 2). See https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html

# Sticking Points
The are a few notable additions/changes worth mentioning. After the `.ckd` file is compiled to a `.bin`, a few codes change:
 * `F0` ("release" code) -> changes to `E3`. The standard defines `F0 12` as "release left shift". In the `.bin` format, this will change to `E3 12` with no other indication.
 * `E2 01 {pp}` = "Delay `pp` × 4 milliseconds" e.g. `E2 01 0A` => Delay 40 milliseconds (`0A` = dec. 10)
 * * Maximum Value is `7d` (500 milliseconds). Longer delays are created by chaining these together.
 * The "Description" is completely dropped

# Control Characters
There are 5 control characters in the binary:
* `E0` -> Control character used for "special keys" (explained in https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html)
* `E2` -> Control character for something the keypad does. Action defined by next byte
** `E2 01` -> Delay, as described above
** `E2 (04|05|06)` -> Controls LED on keypad
* `E3` -> Control character used to indicate "release" of following keycode, described above
* `E4` -> Separator character in binary
** `E4 01` marks the header
** `E4 02` delineates the next Key (indexing starts with KEY0 `00`)
* `E5` -> Terminator character. When this is sent to the keypad, it closes the usb connection and restarts itself with the new configuration.

# Format of Binary
## Header
Contains information concerning Global Parameters. Notably does not contain information on number of keys or model.
15 bytes in total. First give  bytes always `E4 01 0C E0 70`

Next four bytes (`5`-`8`) mark out macro toggling keys. First two toggle, second two Shift. "None" is indicated by `80`.

Next three bytes control, in order, number of keys allowed to be pressed at once, (???), and milliseconds between strokes (halved).

Next three are LED Functions. Explained later. ()

## Keycodes
From the sixteenth byte onwards, everything contains key data for a single Key. The Maximum byte length for a single key is 229 bytes(`0xE5`)

First two bytes `E4 02` indicate a new Key

Third byte is the key number `00`, `01`,... `0A`, etc. (Indexing starts with `00`)

Fourth/Fifth byte (???) (something to do with macro modes)

Sixth byte is the key number repeated. `00`

Beyond this point is the data for Level 1 and Level 2 macros. Each is prepended by the length of the data, including the null terminator at the end. The maximum length for key data is 220 strokes for a single macro (`DD` including null terminator) or 111 for two levels of macro. (`70` each, including the null terminator). To indicate no keystrokes, a null terminator is used for the entire data, then the next data in concatenated.
Example:
`04 1B 1B 1B 00 03 1C 1C 00`

`04` indicates that the next `04` bytes are the keystrokes for the Level 1 Macro. The data is `1B 1B 1B 00` (`s s s 00`).
The Level 2 Macro immediately follows. `03` indicates the length of the data, `1C 1C 00` (`a a 00`).

The next keycode then begins immediately, with the `E4 02 xx` separator. After everything is defined, a final `E5` terminates the file.
