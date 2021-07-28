#!/usr/bin/python3
# Created by Ada


class GlobalOptions:
	""" Holds Global Settings such as LED Settings and Macro Toggling Keys """
	def __init__(self, raw_info):
		self.file_header = [0xE4, 0x01, 0x0C, 0xE0, 0x70]
		# The macro shift and toggle keys are not stored in the GLOBAL_PARAMETERS, ...
		# ... so we set them to defaults then modify them as we find them in the key macros
		self.macro_toggle_keys = [0x80, 0x80]
		self.macro_shift_keys =  [0x80, 0x80]

		# This number isn't used anywhere explicitly
		# We only need it to know the number of key macros to compile
		self.number_of_keys = int(raw_info[2].split('=')[1])

		self.n_key_rollover = [int(raw_info[3].split('=')[1], 16)]
		self.null_spacer = [0x00]	# Unknown Function
		self.char_pacing = [int(raw_info[7].split('=')[1], 16)]
		self.led_functions = [int(raw_info[x].split('=')[-1], 16) for x in (4,5,6)]

		self.fields = [self.file_header,
			self.macro_toggle_keys,
			self.macro_shift_keys,
			self.n_key_rollover,
			self.null_spacer,
			self.char_pacing,
			self.led_functions,
		]

	def add_macro_toggle_key(self, key_num):
		# There are only two slots available for Toggle and Shift keys
		try:
			# Find the first instance of `0x80`. If not found, skip it
			slot = self.macro_toggle_keys.index(0x80)
			self.macro_toggle_keys[slot] = key_num
		except Exception:
			pass

	def add_macro_shift_key(self, key_num):
		# There are only two slots available for Toggle and Shift keys
		try:
			# Find the first instance of`0x80`. If not found, skip it
			slot = self.macro_shift_keys.index(0x80)
			self.macro_shift_keys[slot] = key_num
		except Exception:
			pass

	def add_compiled_info(self, file):
		# Write values to
		for field in self.fields:
			for val in field:
				file.write(bytes((val,)))


class KeyMacro:
	""" Holds information for the Macro Data for a Key """
	# Initial Parsing of Data
	def __init__(self, raw_info, global_options):
		self.opening = [0xE4, 0x02]
		# Parse out digits from line
		self.keynum = [int(''.join([x for x in raw_info[0] if x.isdigit()]))]
		# These are all altered by various options. We'll get to it, Together
		self.l1_data_length = []
		self.l1_macro_options = [0x00]
		self.l2_data_length = []
		self.l2_macro_options = [0x00]

		# KeyType 1 signifies "Macro Shift" key
		if raw_info[1].endswith('1'):
			if self.keynum[0] < global_options.number_of_keys:
				global_options.add_macro_shift_key(self.keynum[0])
		# KeyType 2 signifies "Macro Toggle" key
		elif raw_info[1].endswith('2'):
			if self.keynum[0] < global_options.number_of_keys:
				global_options.add_macro_toggle_key(self.keynum[0])
		else:
			pass

		# Returns macro in nice list format
		# Level 1 Macro Data
		self.l1_macro_data = self._macro_parser(raw_info[6])
		if len(self.l1_macro_data) > 1:
			# If it's an empty string, we leave this blank
			# Otherwise, each macro is pre-pended with the length of its data
			self.l1_data_length = [len(self.l1_macro_data)]
			print(str(self.keynum[0]) +" l1: "+ str(len(self.l1_macro_data)))
			# The final bit of macro_options is whether any data is written for this macro
			self.l1_macro_options[0] += 0b0001

		self.l2_macro_data = self._macro_parser(raw_info[7])
		if len(self.l2_macro_data) > 1:
			# Each macro is pre-pended with the length of its data
			# ... unless it has a length of 0
			self.l2_data_length = [len(self.l2_macro_data)]
			print(str(self.keynum[0]) +" l2: "+ str(len(self.l2_macro_data)))
			# The last bit of macro_options is whether any data is written for this macro
			self.l2_macro_options[0] += 0b0001

		# Second to last bit flipped by Auto-Repeat
		if raw_info[2].endswith('1'):
			self.l1_macro_options[0] += 0b0010
		if raw_info[3].endswith('1'):
			self.l2_macro_options[0] += 0b0010

		# The bits flipped here are according to the MacroMode of the macro
		# These control the first two bits. Mode '0' and Mode '2' are Identical
		macro_mode_lookup_table = {
			'0': 0b0000,	# "Default Mode" (changes)
			'1': 0b1000,	# Separate Up Codes
			'2': 0b0000,	# Macro Mode
			'3': 0b0100}	# Literal Mode
		self.l1_macro_options[0] += macro_mode_lookup_table[raw_info[4].split('=')[1]]
		self.l2_macro_options[0] += macro_mode_lookup_table[raw_info[5].split('=')[1]]

		self.fields = [self.opening,
			self.keynum,
			self.l2_macro_options,
			self.l1_macro_options,
			self.keynum,
			self.l1_data_length,
			self.l1_macro_data,
			self.l2_data_length,
			self.l2_macro_data,
		]
	
	def _macro_parser(self, raw_line):
		""" Parses out the macro into individual bytes and puts it in the format GENOVATION wants """
		line = raw_line.split('=')[1]
		# Split string into groups of two characters
		line = [int(line[x:x+2], 16) for x in range(0, len(line), 2)]
		# In the compiled files, 0xF0 is replaced with 0xE3. This is undocumented.
		for c, val in enumerate(line):
			if val == 0xF0:
				line[c] = 0xE3
		# All macros are null terminated. If the macro is blank, just returns a null.
		line = line + [0x00]
		return line

	def add_compiled_info(self, file):
		""" Called to write data to passed-in file """
		for field in self.fields:
			for val in field:
				file.write(bytes((val,)))


def compile_ckd(i_file=None, o_file=None):
	global_options = None
	key_params = []

	with open(i_file, "r") as file:
		# Buffer holding each line in the .ckd file until we parse it out
		text_buffer = []

		for line in file.readlines():
			# If we reach a new section, parse out the previous section, ...
			# ...then write the line to the text buffer
			if (line.strip().startswith("[") or line.strip() == '') and (len(text_buffer)):
				if text_buffer[0] == "[GLOBAL_PARAMETERS]":
					global_options = GlobalOptions(text_buffer)
				else:
					key_params.append(KeyMacro(text_buffer, global_options))
				# Clear the previous section's buffer 
				text_buffer = []
			# Append the line to the buffer
			text_buffer.append(line.strip())
		
		if text_buffer:
			key_params.append(KeyMacro(text_buffer, global_options))

	# Begin Writing of .bin
	with open(o_file, "wb") as output_file:
		# Write Header to File
		global_options.add_compiled_info(output_file)

		# Write Key Macros to File
		for key_number in range(global_options.number_of_keys):
			key_params[key_number].add_compiled_info(output_file)
		# Write Terminator to File
		output_file.write(bytes((0xE5,))) # Terminator
