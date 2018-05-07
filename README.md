# ![](icon.png) PyArchInit3 - QGIS plugin
[![GitHub version](https://badge.fury.io/gh/pyarchinit%2Fpyarchinit.svg)](https://badge.fury.io/gh/pyarchinit%2Fpyarchinit)

## Installing from zip

### Linux/Windows/MacOS
1. Download the zip archive from github
2. Install the python packages requirements (see [Dependencies](#dependencies) paragraph)
3. Open QGIS and then from Plugin manager use Install from ZIP to install the plugin

**Note:** _While installing a message box could be prompted to warn you about missing python packages required from the plugin_

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
1. Fork ad clone the repository: ```git clone https://github.com/<user>/pyarchinit.git```
2. Make your changes
3. Commit to your repository: ```git commit -am 'your_message'```
4. Create a pull request: ```git push -u origin <your_branch>```

![PR](https://services.github.com/on-demand/images/gifs/github-cli/push-and-pull.gif)
