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

class promt_headerCommand(sublime_plugin.TextCommand):

	settings = sublime.load_settings("iDriftWeb.sublime-settings")
	gitconfig = {'name' : '', 'email' : '', 'company' : 'iDrift Web AS', 'copy' : '2012'}

	def run(self, edit):
		if get_gitconfig():
		 	self.gitconfig = get_gitconfig()
		 	self.gitconfig['company'] = 'iDrift Web AS'
		 	self.gitconfig['copy'] = '2012'

		self.view.window().show_input_panel("Name", self.settings.get('name', self.gitconfig['name']), self.get_mail, None, None)
		pass

	def get_mail(self, text):
		self.settings.set('name', text)
		self.view.window().show_input_panel("Email", self.settings.get('email', self.gitconfig['email']), self.get_company, None, None)
		pass

	def get_company(self, text):
		self.settings.set('email', text)
		self.view.window().show_input_panel("Company", self.settings.get('company', self.gitconfig['company']), self.get_copy, None, None)
		pass

	def get_copy(self, text):
		self.settings.set('company', text)
		self.view.window().show_input_panel("Copyright", self.settings.get('copy', self.gitconfig['copy']), self.on_done, None, None)
		pass

	def on_done(self, text):
		self.settings.set('copy', text)
		pass

class insert_headerCommand(sublime_plugin.TextCommand):
	settings = sublime.load_settings("iDriftWeb.sublime-settings")
	gitconfig = {'name' : '', 'email' : '', 'company' : 'iDrift Web AS', 'copy' : '2012'}
	contents = ''

	def run(self, edit, contents = '${13}\n'):
		self.contents = contents
		if self.settings.has('name'):
			self.insert()
			pass
		else:
			self.view.run_command('promt_header')
		pass


	def insert(self):
		now = datetime.datetime.now()

		pt = self.view.text_point(0, 0)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(pt))
		self.view.show(pt)

		content_syntax_open     = "<?php\n"
		content_meta_open       = "/**\n"
		content_comment         = " *	${1}\n"
		content_file            = " *	${2:$TM_FILENAME}\n"
		content_date            = " *	Created on ${3:${4:%d}.${5:%d}.${6:%d}}.\n *\n" % (now.day, now.month, now.year)
		content_author          = " *	@author ${7:%s} <${8:%s}>\n" % (self.settings.get('name'), self.settings.get('email'))
		if self.settings.get('copy'):
			content_copy        = " *	@copyright ${9:%s} - ${10:%d} ${11:%s}\n" % (self.settings.get('copy'), now.year, self.settings.get('company') if self.settings.get('company') else self.settings.get('name') )
		else:
			content_copy        = ""
		content_version         = " *	@version ${12:1.0.0}\n"
		content_meta_end        = " *\n */\n\n"

		content_content         = "%s\n" % self.contents

		content_end_of_file     = "/* End of file $2 */\n"
		if self.view.file_name():
			content_location    = "/* Location: ${TM_FILEPATH} */\n"
		else:
			content_location    = ""
		content_end             = "\n?>\n"

		snippet_content         = "%s%s%s%s%s%s%s%s%s%s%s%s%s" % (content_syntax_open, content_meta_open, content_comment, content_file, content_date, content_author, content_copy, content_version, content_meta_end, content_content, content_end_of_file, content_location, content_end)
		self.view.run_command("insert_snippet", { "contents": snippet_content })
