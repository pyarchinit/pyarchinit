# ![](icon.png) PyArchInit3 - QGIS plugin

## Installing from zip

### Linux/Windows/MacOS
1. Download the zip archive from github
2. Install the python packages requirements (see [Dependencies](#dependencies) paragraph)
3. Open QGIS and then from Plugin manager use Install from ZIP to install the plugin

```Note: While installing a message box could be prompted which warn you on missing python packages required from the plugin```

#### Dependencies
* SQLAlchemy
* reportlab
* PypeR (for R)
* [Graphviz Visualization Software](https://www.graphviz.org/)
* [graphviz python module](https://github.com/xflr6/graphviz)
* matplotlib
* networkx

The dependencies can be installed using the [modules_installer.py](/scripts/modules_installer.py) by running it from within a python shell:

```python modules_installer.py```

### Contribute
1. Fork the repository
2. Make your changes
3. Commit to your repository
4. Create a pull request

