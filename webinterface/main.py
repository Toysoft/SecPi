import os

# web framework
import cherrypy

# db connection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Integer

# web <--> db
from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin

# templating engine
from mako.template import Template
from mako.lookup import TemplateLookup

# our stuff
from tools.db import objects
from tools import config

# sub pages
from sites.sensors import SensorsPage
from sites.zones import ZonesPage
from sites.setups import SetupsPage
from sites.alarms import AlarmsPage
from sites.workers import WorkersPage
from sites.actions import ActionsPage
from sites.actionparams import ActionParamsPage
from sites.logs import LogEntriesPage


lookup = TemplateLookup(directories=['templates'], strict_undefined=True)
config.load("webinterface")

class Root(object):

	def __init__(self):
		self.sensors = SensorsPage()
		self.zones = ZonesPage()
		self.setups = SetupsPage()
		self.alarms = AlarmsPage()
		self.workers = WorkersPage()
		self.actions = ActionsPage()
		self.actionparams = ActionParamsPage()
		self.logs = LogEntriesPage()
	
	@property
	def db(self):
		return cherrypy.request.db


	@cherrypy.expose
	def index(self):
		tmpl = lookup.get_template("index.mako")
		return tmpl.render(page_title="Welcome")
	
	@cherrypy.expose
	def mytest(self, param_1=None, param_2=None, *args, **kw):
		return repr(dict(param_1=param_1,
						 param_2=param_2,
						 args=args,
						 kw=kw))


def run():
	cherrypy.tools.db = SQLAlchemyTool()
	
	
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0',
		'server.socket_port': 8080,
	})
	'''
		'log.error_file': "./logs/error.log",
		'log.access_file': "./logs/access.log",
		'log.screen': False,
	'''
	
	app_config = {
		'/': {
			'tools.db.on': True,
			'tools.staticdir.root': os.path.join(config.get("project_path"), "webinterface")
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'static'
		}
	}
	cherrypy.tree.mount(Root(), '/', app_config)
	dbfile = "%s/data.db"%config.get("project_path")

	if not os.path.exists(dbfile):
		open(dbfile, 'w+').close()

	sqlalchemy_plugin = SQLAlchemyPlugin(
		cherrypy.engine, objects.Base, 'sqlite:///%s' % (dbfile),
		echo=True
	)
	sqlalchemy_plugin.subscribe()
	sqlalchemy_plugin.create()
	cherrypy.engine.start()
	cherrypy.engine.block()


if __name__ == '__main__':
	run()