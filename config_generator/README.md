# Sparnatural for the life sciences

This modification of [sparnatural](https://github.com/sparna-git/Sparnatural) includes:
* new javascript functions in the `index.html` to adapt results to Wikidata
* a set of SPARQL queries in `index.html` for the dropdown menus 
* a `build_config.py` file that pulls a Google Spreadsheet and builds the config file from it. 
* a `pull_tooltips.py` file that pulls property descriptions from Wikidata


The [Google spreadsheet](https://docs.google.com/spreadsheets/d/1y9_jtEnr2jRWnU5vI5cXmToslIi2nikGcS23m_c_kWY/edit?usp=sharing) containts 2 important sheets: `classes` and `properties`. They determine the fieldts that will be added to the config file. 
If you need write access to the spreadsheet, just ask it there and I'll provide it as soon as possible.


To build the config file, just go in the command line and run:

```python
pip install -r requirements.txt
python3 build_config.py
```















