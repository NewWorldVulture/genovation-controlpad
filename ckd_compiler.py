class GlobalOptions:
	def __init__(self, raw_info):
		self.header_info = [0xE4, 0x01, 0x0C, 0xE0, 0x70]
		# The macro shift and toggle keys are not stored in the GLOBAL_PARAMETERS, ...
		# So we modify these as we iterate through the key macros
		self.macro_toggle_keys = [0x80, 0x80]
		self.macro_shift_keys =  [0x80, 0x80]

		# This number isn't used in the actual header information or anywhere explicitly
		# We'll only need
		self.number_of_keys = int(raw_info[2].split('=')[1])

		# default [0x02]
		self.key_rollover = [int(raw_info[3].split('=')[1], 16)]
		self.null_spacer = [0x00] # 
		# default [0x01]
		self.char_pacing = [int(raw_info[7].split('=')[1], 16)]
		# default [0x01, 0x02, 0x04]
		self.led_functions = [int(raw_info[x].split('=')[-1], 16) for x in (4,5,6)]

		self.fields = [self.header_info,
									self.macro_toggle_keys,
									self.macro_shift_keys,
									self.key_rollover,
									self.null_spacer,
									self.char_pacing,
									self.led_functions,]

	# Expects key_num as aa hex number to be passed in
	# from string -> int(hex_str, 16)
	def add_macro_toggle_key(self, key_num):
		# There are only two slots available for Toggle and Shift keys
		try:
			ind = self.macro_toggle_keys.index(0x80)
			self.macro_toggle_keys[ind] = key_num
		except Exception:
			pass

	# Expects key_num as aa hex number to be passed in
	# from string -> int(hex_str, 16)
	def add_macro_shift_key(self, key_num):
		try:
			ind = self.macro_shift_keys.index(0x80)
			self.macro_shift_keys[ind] = key_num
		except Exception:
			pass

	def add_compiled_info(self, file):
		for field in self.fields:
			for val in field:
				file.write(bytes((val,)))


class KeyMacro:
	# Initial Parsing of Data
	def __init__(self, raw_info, global_options):
		self.opening = [0xE4, 0x02]
		# Parse out digits from line
		self.keynum = [int(''.join([x for x in raw_info[0] if x.isdigit()]))]
		# These are all altered by various options. We'll get to it, Together™
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
			# If it's an empty string, we leave this blank `[]`
			# Otherwise, each macro  is pre-pended with the length of its data
			self.l1_data_length = [len(self.l1_macro_data)]
			print(str(self.keynum[0]) +" l1: "+ str(len(self.l1_macro_data)))
			# The last bit of macro_options is whether any data is written for this macro
			self.l1_macro_options[0] += 0b0001

		# Returns macro in nice list format
		self.l2_macro_data = self._macro_parser(raw_info[7])
		if len(self.l2_macro_data) > 1:
		# If it's an empty string, we leave this blank `[]`
			# Otherwise, each macro  is pre-pended with the length of its data
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
		line = raw_line.split('=')[1]
		# Split string into groups of two characters
		line = [int(line[x:x+2], 16) for x in range(0, len(line), 2)]
		# In the compiled files, 0xF0 is replaced with 0xE3. This is undocumented.
		for c, val in enumerate(line): #!TODO: Fix this!!! it didn't work!!! >:0
			if val == 0xF0:
				line[c] = 0xE3
		# All macros have a null terminator on the end. If the macro is blank, just return a null.
		line = line + [0x00]
		return line

	def add_compiled_info(self, file):
		for field in self.fields:
			for val in field:
				file.write(bytes((val,)))


def main(filename):
	global_options = None
	key_params = []

	with open(filename, "r") as file:
		# Buffer holding each line in the .ckd file until we parse it out
		text_buffer = []

		for line in file.readlines():
			# Parse out text_buffer one at a time
			if (line.strip().startswith("[") or line.strip() == '') and (len(text_buffer)):
				if text_buffer[0] == "[GLOBAL_PARAMETERS]":
					global_options = GlobalOptions(text_buffer)
				else:
					key_params.append(KeyMacro(text_buffer, global_options))
				# Clear the buffer 
				text_buffer = []
			text_buffer.append(line.strip())
		if text_buffer:
			key_params.append(KeyMacro(text_buffer, global_options))

	# Begin Compilation of ckd
	new_file = filename.split('.')[0] + "_compiled_bin.bin"
	with open(new_file, "wb") as new_filename:
		global_options.add_compiled_info(new_filename)
		for key_number in range(global_options.number_of_keys):
			key_params[key_number].add_compiled_info(new_filename)
		new_filename.write(bytes((0xE5,))) # Terminator


main("sample_ckd.ckd")
