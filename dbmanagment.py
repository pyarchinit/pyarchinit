#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

from PyQt4 import QtGui
from modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from modules.gui.dbmanagment_ui import Ui_DBmanagment


try:
    from qgis.core import *
    from qgis.gui import *
except:
    pass

# --import pyArchInit modules--#

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

        self.backup.setEnabled(n)

    def enable_button_search(self, n):

        self.backup.setEnabled(n)

    def on_backupsqlite_pressed(self):
        import shutil

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        conn_import = '%s%s%s' % (home, os.sep,
                                  'pyarchinit_DB_folder/pyarchinit_db.sqlite'
                                  )
        conn_export = '%s%s%s' % (home, os.sep,
                                  'pyarchinit_db_backup/pyarchinit_db_'
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

    def on_backup_pressed(self):
        from pyarchinit_OS_utility import *
        from time import gmtime, strftime
        import subprocess
        import os
        import glob

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_backup/')

        # filename = ('%s%s%s') % (PDF_path, os.sep, 'semivariogramma.png')

        dump_dir = PDF_path
        db_username = 'postgres'

                # db_password = ''

        db_names = ['pyarchinit']

        for db_name in db_names:
            try:

                barra = QtGui.QProgressBar(self)
                barra.show()
                barra.setMinimum(0)
                barra.setMaximum(9)
                for a in range(10):
                    time.sleep(1)
                    barra.setValue(a)

                file_path = ''
                dumper = ' -U %s -Z 9 -f %s -F c %s  '


                bkp_file = '%s_%s.sql' % (db_name,
                        time.strftime('%Y%m%d_%H_%M_%S'))

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

    def on_backup_total_pressed(self):

        from pyarchinit_OS_utility import *

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_backup/')
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

            barra = QtGui.QProgressBar(self)
            barra.show()
            barra.setMinimum(0)
            barra.setMaximum(9)
            for a in range(10):
                time.sleep(1)
                barra.setValue(a)

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
    sys.exit(app.exec_())