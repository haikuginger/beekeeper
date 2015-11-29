# beekeeper

## Description
beekeeper is a Python library designed around dynamically generating a RESTful client interface based on a minimal JSON hive.

The hive specification is designed to provide beekeeper (or other applications consuming hive files) with programmatically-designed insight into the structure of both the REST endpoints that are available and the objects and methods that those endpoints represent.

While the classes available in beekeeper can be used manually to create Pythonic representations of REST endpoints, it is strongly preferred that the library be used as a whole with a constructed hive file. As APIs become larger in scale (in terms of the number of endpoints and represented objects), the time benefit of beekeeper becomes more pronounced, as adding additional objects and endpoints is a trivial process.

## Requirements
beekeeper requires Python 3 or higher and its built-in modules, including json, base64, functools, and urllib.

## Usage
beekeeper does not handle application logic for your client program. Rather, it only constructs an API object which can be used to abstract your server's REST interface. Currently, construction is supported in one of two fashions; either from a Python dictionary representing the hive, or from a JSON hive file.

In the future, beekeeper will be expanded to support constructing an API object from hive files located at arbitrary URLs, and will support a specification for server developers to automatically declare hive files for their websites, meaning that, where implemented, only a domain name will need to be passed to beekeeper.

At present, if a properly-constructed hive file is available, constructing an API object takes one line in Python (after importing the beekeeper module):

```python
my_api = beekeeper.API.from_hive_file('hive.json', api_key="XXXXXXXXXX")
```