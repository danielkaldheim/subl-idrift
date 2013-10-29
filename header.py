import sublime, sublime_plugin, datetime, getpass, re, json
from os.path import expanduser

def get_gitconfig():
	home = expanduser("~")
	fname = "%s/.gitconfig" % home
	try:
		fo = open(fname, "r")
		resultat = {}
		for line in fo:
			res = re.search("\t([^=]+) = ([^\n]+)", line, re.S)
			if res:
				resultat[res.group(1)] = res.group(2)
		return resultat
	except IOError:
		return 0

class promt_headerCommand(sublime_plugin.WindowCommand):

	settings = {'name' : '', 'email' : '', 'company' : 'iDrift Web AS', 'copy' : '2012'}

	def run(self):
		try:
			with open('data.json', 'rb') as fp:
				self.settings = json.load(fp)
			print self.settings
		except IOError:
			self.settings = get_gitconfig()
			self.settings['company'] = 'iDrift Web AS'
			self.settings['copy'] = '2012'

		self.window.show_input_panel("Name", self.settings['name'], self.get_mail, None, None)
		pass

	def get_mail(self, text):
		self.settings['name'] = text
		self.window.show_input_panel("Email", self.settings['email'], self.get_company, None, None)
		pass
	def get_company(self, text):
		self.settings['email'] = text
		self.window.show_input_panel("Company", self.settings['company'], self.get_copy, None, None)
		pass
	def get_copy(self, text):
		self.settings['company'] = text
		self.window.show_input_panel("Copyright", self.settings['copy'], self.on_done, None, None)
		pass
	def on_done(self, text):
		self.settings['copy'] = text
		with open('data.json', 'wb') as fp:
			json.dump(self.settings, fp)

class insert_headerCommand(sublime_plugin.TextCommand):
	settings = {'name' : '', 'email' : '', 'company' : 'iDrift Web AS', 'copy' : '2012'}

	def run(self, edit):
		try:
			with open('data.json', 'rb') as fp:
				self.settings = json.load(fp)
				self.insert()
		except IOError:
			try:
				with open('data.json', 'rb') as fp:
					self.settings = json.load(fp)
				print self.settings
			except IOError:
				self.settings = get_gitconfig()
				self.settings['company'] = 'iDrift Web AS'
				self.settings['copy'] = '2012'
				self.view.window().show_input_panel("Name", self.settings['name'], self.get_mail, None, None)
				pass
		pass

	def get_mail(self, text):
		self.settings['name'] = text
		self.view.window().show_input_panel("Email", self.settings['email'], self.get_company, None, None)
		pass
	def get_company(self, text):
		self.settings['email'] = text
		self.view.window().show_input_panel("Company", self.settings['company'], self.get_copy, None, None)
		pass
	def get_copy(self, text):
		self.settings['company'] = text
		self.view.window().show_input_panel("Copyright", self.settings['copy'], self.on_done, None, None)
		pass
	def on_done(self, text):
		self.settings['copy'] = text
		with open('data.json', 'wb') as fp:
			json.dump(self.settings, fp)
		self.insert()

	def insert(self):
		now = datetime.datetime.now()

		content_open        = "<?php\n/**\n *  ${1}\n *	${2:$TM_FILENAME}\n"
		content_date        = " *	Created on ${3:${4:%d}.${5:%d}.${6:%d}}.\n *\n" % (now.day, now.month, now.year)
		content_author      = " *	@author ${7:%s} <${8:%s}>\n" % (self.settings['name'], self.settings['email'])
		if self.settings['copy']:
			content_copy        = " *	@copyright ${9:%s} - ${10:%d} ${11:%s}\n" % (self.settings['copy'], now.year, self.settings['company'] if self.settings['company'] else self.settings['name'] )
		else:
			content_copy = ""
		content_version     = " *	@version ${12:1.0.0}\n"
		content_content     = " *\n */\n\n${13}\n\n"
		content_end_of_file = "/* End of file ${TM_FILENAME:${2/(.+)/\l$1.php/}} */\n"
		content_location    = "/* Location: ${TM_FILEPATH} */\n\n?>\n"

		content = "%s%s%s%s%s%s%s%s" % (content_open, content_date, content_author, content_copy, content_version, content_content, content_end_of_file, content_location)
		self.view.run_command("insert_snippet", { "contents": content })
