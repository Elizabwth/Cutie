class Chat(object):
	def __init__(self):
		self.accumulated_chat = ''

	def _reduce_chat(self):
		lines = self.accumulated_chat.split("\n")
		num_of_lines = len(lines)
		max_lines = num_of_lines-100
		if len(lines) > max_lines:
			self.accumulated_chat = ""
			for line in lines[max_lines:len(lines)]:
				self.accumulated_chat += line+"\n"