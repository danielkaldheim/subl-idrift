import sublime, sublime_plugin, header

class insert_functionsphpCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.set_name('functions.php')
		# self.view.set_syntax_file('../PHP/PHP.tmLanguage')

		try:
			with open('functionsphp.txt', 'r') as fp:
				self.view.run_command('insert_header', {'contents' : fp.read() })
		except IOError:
			print 'bugger'
		pass
