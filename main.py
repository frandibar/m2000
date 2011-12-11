#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('main')

def start_application():
    from camelot.view.main import main
    from m2000.application_admin import MyApplicationAdmin
    main(MyApplicationAdmin())

if __name__ == '__main__':
    start_application()
