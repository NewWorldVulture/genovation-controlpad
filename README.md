# Genovation ControlPads Details
Description of Genovation Keypad binaries and configuration process
The Genovation Controlpad CPxx series is programmed by scancodes following, for the most part the AT Keyboard Scan Codes (Set 2). See https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html

# Control Characters
There are 5 control characters in the binary:
* `E0` -> Control character used for "special keys" (explained in https://webdocs.cs.ualberta.ca/~amaral/courses/329/labs/scancodes.html)
* `E2` -> Control character for something the keypad does. Action defined by next byte
* * `E2 01` -> Delay, as described above
* * `E2 (04|05|06)` -> Controls LED on keypad
* `E3` -> Control character used to indicate "release" of following keycode, described above
* `E4` -> Separator character in binary
* * `E4 01` marks the header
* * `E4 02` delineates the next Key (indexing starts with KEY0 `00`)
* `E5` -> Terminator character. When this is sent to the keypad, it closes the usb connection and restarts itself with the new configuration.

# Format of Binary
## Header
![image](https://user-images.githubusercontent.com/49806198/121860320-97049300-ccad-11eb-8af4-c5dbdf97658e.png)

Contains information concerning Global Parameters. Notably does not contain information on number of keys or model.
15 bytes in total. First five bytes are always `E4 01 0C E0 70`. `E0 70` is the code for "Insert", but no other write mode seems to work in these bytes.


Bytes `0x5` and `0x6` dictate which keys are used as **Macro Toggle** keys. After these are pressed, all further keys pressed input their Level 2 Macro, similar to the way a Caps Lock key works. The keys are counted indexed at `0x00`, left-to-right, top-to-bottom. A value of `80` indicates an unused slot.

Bytes `0x7`, `0x8` dictate the **Macro Shift** keys. All the same rules for Macro Toggle Keys Applies here

`0x9` controls **Key-Rollover**. This dictates how many keys can be pressed at once. This must be at least `02` for the Macro Shift keys to work as intended.

`0xA` has no known function, and is always `00`.

`0xB` dictates Character Pacing. This number is in milliseconds, and is doubled on the keypad. e.g. a value of `04` would mean a eight millisecond gap between characters being typed.

`0xC`, `0xD`, `0xE` control the LED Functions. These control which LEDs are powered and under what circumstances. The CP24 only has one LED, and therefore only reads the first value. There are seven  possible values:
1. `00` for no function
2. `01` to indicate Caps Lock
3. `02` to indicate Num Lock
4. `03` to indicate Level Indicator (LED on when L2 macros are active)
5. `04` to indicate Host/Macro Control
6. `05` to indicate power
7. `06` to indicate Scroll Lock

`0xF` onwards indicates the start of a new key definition

## Keycodes
![image](https://user-images.githubusercontent.com/49806198/121881780-8b709680-ccc4-11eb-9b6c-33c117ea7a61.png)

First two bytes `E4 02` indicate the next **Key Definition**.

`0x02` and `0x05` are both the **Key Number** `00`, `01`,... `0A`, etc. (Indexing starts with `00`)

`0x03` holds the options for the Level 2 Macro for this key. The first four bits are never used. The fifth marks the Separate Up Codes mode (only used when it only types one character). Sixth marks "Literal Mode". This is explained in full detail in the CP24 `MacroMasterCPxx.pdf` that comes with Genovation MacroMasterCPxx. Seventh bit marks "Auto-Repeat" (If the key is held down, the macro repeats over and over). Eighth marks whether the macro is active. If the macro has no data, this is `0`.

`0x04` holds the options for the LEvel 1 Macro for this key.

Beyond this point is the data for Level 1 and Level 2 macros. Each is prepended by the length of the data, including the null terminator at the end. The maximum length for key data is 220 strokes for a single macro, or 111 strokes for two levels of macro. To indicate no keystrokes, a null terminator is used for the entire data, then the next data is concatenated.
Example:
`04 1B 1B 1B 00 03 1C 1C 00`

`04` indicates that the next `04` bytes are the keystrokes for the Level 1 Macro. The data is `1B 1B 1B 00` (`s s s 00`).
The Level 2 Macro immediately follows. `03` indicates the length of the data, `1C 1C 00` (`a a 00`).

The next keycode then begins immediately, with the same `E4 02` separator. After everything is defined, a final `E5` terminates the file.

# Sticking Points
The are a few notable additions/changes worth mentioning. After the `.ckd` file is compiled to a `.bin`, a few codes change:
 * `F0` ("release" code) -> changes to `E3`. The standard defines `F0 12` as "release left shift". In the `.bin` format, this will change to `E3 12` with no indication that it has done so.
 * `E2 01 {pp}` = "Delay `pp` × 4 milliseconds" e.g. `E2 01 0A` => Delay 40 milliseconds (`0A` = dec. 10)
 * * Maximum Value is `7d` (500 milliseconds). Longer delays are created by chaining these together.
 * The "Description" is completely dropped
