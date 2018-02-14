#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
try:
    from qgis.core import *
    from qgis.gui import *
except:
    pass

from pyarchinit_db_manager import *

from psycopg2 import *

# --import pyArchInit modules--#

from dbmanagment_ui import Ui_DBmanagment
from dbmanagment_ui import *
from pyarchinit_utility import *
from pyarchinit_error_check import *

from pyarchinit_pyqgis import Pyarchinit_pyqgis


class pyarchinit_dbmanagment(QDialog, Ui_DBmanagment):

    MSG_BOX_TITLE = \
        'PyArchInit - pyarchinit_version 0.4 - Scheda gestione DB'

    def __init__(self, iface):
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(self.iface)
        QDialog.__init__(self)
        self.setupUi(self)
        QMessageBox.warning(self, 'Alert',
                            'Sistema sperimentale solo per lo sviluppo'
                            , QMessageBox.Ok)

        # self.customize_GUI() #call for GUI customizations

        self.currentLayerId = None

    def enable_button(self, n):

        self.beckup.setEnabled(n)

    def enable_button_search(self, n):

        self.beckup.setEnabled(n)

    def on_backupsqlite_pressed(self):
        import time
        import shutil

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        conn_import = '%s%s%s' % (home, os.sep,
                                  'pyarchinit_DB_folder/pyarchinit_db.sqlite'
                                  )
        conn_export = '%s%s%s' % (home, os.sep,
                                  'pyarchinit_db_beckup/pyarchinit_db_'
                                  + time.strftime('%Y%m%d_%H_%M_%S_')
                                  + '.sqlite')
        backupdir = conn_export

        shutil.copy(conn_import, conn_export)

        barra = QtGui.QProgressBar(self)
        barra.show()
        barra.setMinimum(0)
        barra.setMaximum(9)
        for a in range(10):
            time.sleep(1)
            barra.setValue(a)

    def on_beckup_pressed(self):
        from pyarchinit_OS_utility import *
        from time import gmtime, strftime
        import subprocess
        import os
        import glob
        import time

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_beckup/')

        # filename = ('%s%s%s') % (PDF_path, os.sep, 'semivariogramma.png')

        dump_dir = PDF_path
        db_username = 'postgres'

                # db_password = ''

        db_names = ['pyarchinit']

        for db_name in db_names:
            try:

            # app = QtGui.QApplication(sys.argv)

                barra = QtGui.QProgressBar(self)
                barra.show()
                barra.setMinimum(0)
                barra.setMaximum(9)
                for a in range(10):
                    time.sleep(1)
                    barra.setValue(a)

                # app.exec_()........

                file_path = ''
                dumper = ' -U %s -Z 9 -f %s -F c %s  '

                #        os.putenv('PGPASSWORD', db_password)

                bkp_file = '%s_%s.sql' % (db_name,
                        time.strftime('%Y%m%d_%H_%M_%S'))

                #        glob_list = glob.glob(dump_dir + db_name + '*' + '.pgdump')

                file_path = os.path.join(dump_dir, bkp_file)
                command = 'pg_dump' + dumper % (db_username, file_path,
                        db_name)
                subprocess.call(command, shell=True)
                subprocess.call('gzip ' + file_path, shell=True)

                QMessageBox.warning(self, 'Messaggio',
                                    'Backup completato', QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self, 'Messaggio',
                                    'Backup fallito!!' + str(e),
                                    QMessageBox.Ok)

    def on_beckup_total_pressed(self):

        from pyarchinit_OS_utility import *
        import os
        import time

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_beckup/')
        filename = '%s%s%s' % (PDF_path, os.sep, 'semivariogramma.png')

        username = 'postgres'

        defaultdb = 'postgres'

        port = '5432'

        backupdir = PDF_path

        date = time.strftime('%Y-%m-%d-%H-%M-%S')

        # GET DB NAMES

        get_db_names = \
            "psql -U%s -d%s -p%s --tuples-only -c '\l' | awk -F\| '{ print $1 }' | grep -E -v '(template0|template1|^$)'" \
            % (username, defaultdb, port)

        # MAKE BACKUP OF SYSTEMGRANTS

        os.popen('pg_dumpall -p%s -g|gzip -9 -c > %s/system.%s.gz'
                 % (port, backupdir, date))

        # MAKING DB BACKUP

        for base in os.popen(get_db_names).readlines():
            try:

            # app = QtGui.QApplication(sys.argv)

                barra = QtGui.QProgressBar(self)
                barra.show()
                barra.setMinimum(0)
                barra.setMaximum(9)
                for a in range(10):
                    time.sleep(1)
                    barra.setValue(a)

                # app.exec_()....

                base = base.strip()
                fulldir = backupdir + base
                if not os.path.exists(fulldir):
                    os.mkdir(fulldir)
                filename = '%s/%s-%s.sql' % (fulldir, base, date)
                os.popen('nice -n 19 pg_dump -C -F c -U%s -p%s %s > %s'
                         % (username, port, base, filename))
                QMessageBox.warning(self, 'Messaggio',
                                    'Backup completato', QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self, 'Messaggio',
                                    'Backup fallito!!' + str(e),
                                    QMessageBox.Ok)

    def on_upload_pressed(self):
        self.percorso = QtGui.QFileDialog.getOpenFileName(self,
                'Open file', '/')

        # QMessageBox.warning(self, "Messaggio", str(self.FILE), QMessageBox.Ok)

    def on_restore_pressed(self):
        try:

        # app = QtGui.QApplication(sys.argv)

            barra = QtGui.QProgressBar(self)
            barra.show()
            barra.setMinimum(0)
            barra.setMaximum(9)
            for a in range(10):
                time.sleep(1)
                barra.setValue(a)

            # app.exec_()........

            path = self.percorso
            os.popen('dropdb -U postgres pyarchinit')
            os.popen('createdb -U postgres -p 5432 -h localhost -E UTF8  -T template_postgis_20 -e pyarchinit'
                     )
            os.popen('pg_restore --host localhost --port 5432 --username postgres --dbname pyarchinit --role postgres --no-password  --verbose %s'
                      % str(path))
            QMessageBox.warning(self, 'Messaggio',
                                'Ripristino completato', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, 'Messaggio',
                                'Ripristino fallito!!' + str(e),
                                QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = pyarchinit_dbmanagment()
    ui.show()
    barra.show()
    sys.exit(app.exec_())
