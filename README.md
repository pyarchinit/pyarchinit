# ![](icon.png) PyArchInit3 - QGIS plugin
[![GitHub release](https://img.shields.io/github/release/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![HitCount](http://hits.dwyl.io/pyarchinit/pyarchinit.svg)](http://hits.dwyl.io/pyarchinit/pyarchinit)
[![Donate to QGIS](https://img.shields.io/badge/donate%20to-QGIS-green.svg?style=flat-square)](http://qgis.org/en/site/getinvolved/donations.html)

## Installing from zip

### Linux/Windows/MacOS
1. Download the zip archive from github
2. Install the python packages requirements (see [Dependencies](#dependencies) paragraph)
3. Open QGIS and then from Plugin manager use Install from ZIP to install the plugin

**Note:** _While installing a message box could be prompted to warn you about missing python packages required from the plugin._

**Note2:** _Under Windows is necessary to start QGIS as Administrator when you install the plugin for the first time in order to install all the dependencies properly._

**Note3:** _If you use PostgreSQL, we raccomend to install PostgreSQL >=9.6_

**Note4:** _If you have already an pyarchinit db, use "update posgres" or "update sqlite" tool in pyarchinit configuration  form to update  your db to the new release._

**Note5:** _If you have already installed pyarchinit before of the 01/02/2019, to install the new version, delete the file config.cfg in pyarchinit_DB_folder and restart as admin._

#### Dependencies
* SQLAlchemy
* reportlab
* PypeR (for R)
* [R Software](https://www.r-project.org/)
* [Graphviz Visualization Software](https://www.graphviz.org/)
* [graphviz python module](https://github.com/xflr6/graphviz)
* matplotlib
* networkx
* pysftp

The dependencies can be installed using the [modules_installer.py](/scripts/modules_installer.py) by running it from within a python shell:

```python modules_installer.py```

### Contribute
1. Fork ad clone the repository: ```git clone https://github.com/<user>/pyarchinit.git```
2. Make your changes
3. Commit to your repository: ```git commit -am 'your_message'```
4. Create a pull request: ```git push -u origin <your_branch>```

![PR](https://services.github.com/on-demand/images/gifs/github-cli/push-and-pull.gif)
