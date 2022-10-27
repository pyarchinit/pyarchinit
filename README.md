# ![](icon.png) PyArchInit4 by Luca Mandolesi & Enzo Cocca - QGIS plugin for archaeology - #MICH
[![GitHub release](https://img.shields.io/github/release/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![HitCount](http://hits.dwyl.io/pyarchinit/pyarchinit.svg)](http://hits.dwyl.io/pyarchinit/pyarchinit)
[![Donate to QGIS](https://img.shields.io/badge/donate%20to-QGIS-green.svg?style=flat-square)](http://qgis.org/en/site/getinvolved/donations.html)

## PyArchInit4 works with QGIS >=3.22

## Installing adding pyarchinit repository into QGIS

# Video per installazione plugin -> [Video](https://www.adarteinfo.it/archivio/pyarchinit-download/install.gif)

In QGIS add this link for the master version:

_http://pyarchinit.org/pyarchinit.xml_



## Installing from zip

### Linux/Windows/MacOS
1. Download the zip archive from github
2. Install the python packages requirements (see [Dependencies](#dependencies) paragraph)
3. Open QGIS and then from Plugin manager use Install from ZIP to install the plugin


**Note1:** _If you use PostgreSQL, we raccomend to install PostgreSQL >=9.6_


#### Dependencies
* SQLAlchemy
* reportlab
* PypeR (for R)
* [R Software](https://www.r-project.org/)
* [Graphviz Visualization Software](https://www.graphviz.org/)*(see note)
* [graphviz python module](https://github.com/xflr6/graphviz)
* matplotlib
* pdf2docx
* pysftp

**Note2:** _Note for Mac_

you need install Cambria font. If you don't have already installed, automatically the folder with cambria font  will open 

you need just double click on all file with cambria name.
* cambria.ttc
* Cambria.ttf
* cambriab.ttf
* cambriai.ttf
* cambriaz.ttf

**Note3:** _Indtruction to install Graphviz on windows and OSx (first installation)_

Windows
- Download zip file of the [last release of Graphviz (2.50)](https://www.graphviz.org/download/)
- install .exe.

Mac
- Install homwbrew via console (copy and past this): 

  **/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"**
- install graphviz (copy and past this):

  **brew install graphviz**


The dependencies can be installed also using the [modules_installer.py](/scripts/modules_installer.py) by running it from within a python shell:

```python modules_installer.py```

### Contribute
1. Fork ad clone the repository: ```git clone https://github.com/<user>/pyarchinit.git```
2. Make your changes
3. Commit to your repository: ```git commit -am 'your_message'```
4. Create a pull request: ```git push -u origin <your_branch>```


## pyArchInit is used by:

* Dottorato di ricerca in corso (2021) presso Ludwig Maximilian Universität
* Progetti con X-Cavate
* Tesi di laurea, Manuela Battaglia, Necropoli di Malignano, Sovicille (SI)
* Tesi di Laurea, Simona Gugnali, La Necropoli di Via Arnaldo da Brescia (Rimini)
* Parco Archeologico Paestum - Ministero della Cultura
* Dipartimento di archeologia di Università di Salerno
* Scavi archeologici adArte Srl circa 150 contesti
* Scavo del quartiere tardoanitico di Portus
* Scavo di Vicolo del Bologna a Roma centro
* Scavo del comprensorio di S. Giovanni Bosco sull’Appia nuova
* Scavi della Regione Lazio in Via delle Antenne, Roma
* Ricognizioni archeologiche adArte Srl 
* Viarch adArte Srl
* Carta Archeologica Comune di Rimini
* Carta Archeologica Comune di Santarcangelo di Romagna
* Scavi proprietà dell’Ente Nazionale Assistenza Biologi (ENPAB) Roma
* Scavi di Piana S. Marco Castel del Monte (AQ)
* Scavi del monastero di S. Scolastica, Baullo, Gagliano Aterno AQ
* Scavi di Amiternum (AQ)
* Scavi della villa di Poggio Gramignano, Lugnano in Teverina TR
* Scavi della necropoli etrusca di Trocchi, Bomarzo, VT
* Maasser el-Shouf Archaeological Project (Libano), Dott.ssa Silvia Festuccia - Dott. ssa Myriam Ziadé (UniSOB-DGA)
* Università di Pisa - Villa dei Vetti o anche dell'Oratorio a Capraia e Limite, professor Federico Cantini
* Università di Chieti - Castelseprio Casa Piccoli (Varese) - Prof. Vasco La Salvia, Dott. Marco Moderato
