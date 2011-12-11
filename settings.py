import logging
import os

import sqlalchemy
import elixir

import m2000.config

logger = logging.getLogger('settings')

CAMELOT_ATTACHMENTS = ''
# media root needs to be an absolute path for the file open functions
# to function correctly
CAMELOT_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# backup root is the directory where the default backups are stored
CAMELOT_BACKUP_ROOT = os.path.join(os.path.dirname(__file__), 'backup')

# default extension for backup files
CAMELOT_BACKUP_EXTENSION = 'db'

# template used to create and find default backups
CAMELOT_BACKUP_FILENAME_TEMPLATE = 'default-backup-%(text)s.' + CAMELOT_BACKUP_EXTENSION


def ENGINE():
    """This function should return a connection to the database"""
    return sqlalchemy.create_engine('mysql://root:root@localhost:5432/m2000',
                                    encoding='latin1',
                                    convert_unicode=True,
                                    echo=False)

def setup_model():
    """This function will be called at application startup, it is used to setup
    the model"""
    # TODO: when there is no need for views in the db, remove
    # the setup_db call, and use elixir.setup_all(create_tables=True)
    conf = m2000.config.Config()
    if conf.get('create_db') == 'yes':
        import db_setup
        db_setup.setup_db()
        conf.set('create_db', 'no')
    
    # tables only get created in mysql if the db exists
    # 'create database m2000' sufices
    elixir.setup_all(create_tables=False)

    # camelot.model.authentication.updateLastLogin()
