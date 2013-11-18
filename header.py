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

	gitconfig = {}

	def run(self, edit):
		settings = sublime.load_settings("iDriftWeb.sublime-settings")
		if get_gitconfig():
			self.gitconfig = get_gitconfig()
			self.gitconfig['company'] = 'iDrift Web AS'
			self.gitconfig['copy'] = '2012'
		else:
			self.gitconfig = {'name' : '', 'email' : '', 'company' : 'iDrift Web AS', 'copy' : '2012'}

		if settings.has('name'):
			name = settings.get('name')
		else:
			name = self.gitconfig['name']

		self.view.window().show_input_panel("Name", name, self.get_mail, None, None)
		pass

	def get_mail(self, text):
		settings = sublime.load_settings("iDriftWeb.sublime-settings")
		settings.set('name', text)
		sublime.save_settings("iDriftWeb.sublime-settings")

		if settings.has('email'):
			email = settings.get('email')
		else:
			email = self.gitconfig['email']

		self.view.window().show_input_panel("Email", email, self.get_company, None, None)
		pass

	def get_company(self, text):
		settings = sublime.load_settings("iDriftWeb.sublime-settings")
		settings.set('email', text)
		sublime.save_settings("iDriftWeb.sublime-settings")

		if settings.has('company'):
			company = settings.get('company')
		else:
			company = self.gitconfig['company']

		self.view.window().show_input_panel("Company", company, self.get_copy, None, None)
		pass

	def get_copy(self, text):
		settings = sublime.load_settings("iDriftWeb.sublime-settings")
		settings.set('company', text)
		sublime.save_settings("iDriftWeb.sublime-settings")

		if settings.has('copy'):
			copy = settings.get('copy')
		else:
			copy = self.gitconfig['copy']

		self.view.window().show_input_panel("Copyright", copy, self.on_done, None, None)
		pass

	def on_done(self, text):
		settings = sublime.load_settings("iDriftWeb.sublime-settings")
		settings.set('copy', text)
		sublime.save_settings("iDriftWeb.sublime-settings")
		pass

class insert_headerCommand(sublime_plugin.TextCommand):
	contents = ''

	def run(self, edit, contents = '${13}\n'):
		self.contents = contents
		settings = sublime.load_settings("iDriftWeb.sublime-settings")

		if settings.has('name'):
			self.insert()
			pass
		else:
			self.view.run_command('promt_header')
		pass


	def insert(self):

		settings = sublime.load_settings("iDriftWeb.sublime-settings")
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
		content_author          = " *	@author ${7:%s} <${8:%s}>\n" % (settings.get('name'), settings.get('email'))
		if settings.get('copy'):
			content_copy        = " *	@copyright ${9:%s} - ${10:%d} ${11:%s}\n" % (settings.get('copy'), now.year, settings.get('company') if settings.get('company') else settings.get('name') )
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

class insert_functionsphpCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.set_name('functions.php')
		content = """
		class ${14:Class_Name} {

			/**
			 * Holds class instance
			 *
			 * @access protected
			 * @var object
			 */

			protected static \$instance;


			/**
			 * Static Singleton Factory Method
			 *
			 * @return object
			 */

			public static function instance() {

				if ( ! isset( self::\$instance ) ) {

					\$className = __CLASS__;
					self::\$instance = new \$className;

				}

				return self::\$instance;

			}


			/**
			 * Initialize
			 */

			public function __construct() {

				// Setup theme
				add_action( 'after_setup_theme', array( &\$this, 'setup_theme' ) );

				// Enqueue frontend styles
				add_action( 'wp', array( &\$this, 'frontend_styles' ) );

				// Enqueue frontend scripts
				add_action( 'wp_enqueue_scripts', array( &\$this, 'frontend_scripts' ) );

			}


			/**
			 * Setup theme
			 */

			public function setup_theme() {

				// Code

			}


			/**
			 * Enqueue frontend stylesheets
			 */

			public function frontend_styles() {

				if( is_admin() )
					return;

				wp_enqueue_style( 'themename', THEME_URL . '/styles/style.less', array( 'normalize' ), NULL );

			}


			/**
			 * Enqueue frontend scripts
			 */

			public function frontend_scripts() {

				wp_enqueue_script( 'themename', THEME_URL . '/js/common.js', array('jquery'), NULL, true );

			}

		}

		\$${14:Class_Name} = ${14:Class_Name}::instance();
		"""
		self.view.run_command("insert_header", { "contents": content })
