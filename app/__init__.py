import logging
from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
from app.index import MyIndexView
from .momentjs import momentjs





"""
 Logging configuration
"""

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
 
app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs

db = SQLA(app)
appbuilder = AppBuilder(app, db.session, indexview=MyIndexView, base_template='mybase.html')

#migration_dir = str(app.static_folder) + '/alembic'
#migrate = Migrate(app, db)
'''
with app.app_context():
    # Only run DB downgrade for local dev environment
    # otherwise all data is lost  
    #     print 'Downgrading back to base revision'
    #     downgrade(directory=migration_dir, revision='base')
    print('Upgrading up to head revision')
    
    if os.path.exists(os.getcwd() + '/app/static/alembic'):
        print('alembic migration folder found')
    else:
        print('alembic migration folder not found:', os.getcwd()+ '/app/static/alembic')
        init()
    
    #Migrate(directory=migration_dir)
    config = Config("migrations/alembic.ini")
    config.set_main_option("script_location", "migrations")
    #command.upgrade(config, "head")
    command.upgrade(config, revision='head')
    #upgrade(directory=migration_dir, revision='head')

'''
"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    

from app import views




