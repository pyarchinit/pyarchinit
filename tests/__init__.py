"""Rende `tests` un pacchetto vero, e non una porzione di namespace.

Serve perché i moduli PostgreSQL fanno `from tests.sync.conftest_pg import
pg_engine`: senza questo file `tests/` è solo una porzione di namespace, e
la regola di Python è che la scansione di `sys.path` non si fermi su una
porzione ma continui — così un pacchetto `tests` VERO trovato più avanti
vince su di noi anche se noi veniamo prima. Su questa macchina quel
pacchetto esiste: `ultralytics` installa la propria suite come `tests`
di primo livello in `~/.local/lib/python3.9/site-packages/tests/`, e
`import tests.sync.conftest_pg` finiva lì dentro con
`ModuleNotFoundError: No module named 'tests.sync'`.

Con l'`__init__.py` la nostra `tests/` è un pacchetto regolare trovato
nella directory di lavoro (sys.path[0] sotto `python -m pytest`) e vince.
"""
