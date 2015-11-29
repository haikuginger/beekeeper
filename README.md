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

Note the `api_key` keyword argument used here. This is not natively coded in beekeeper; rather, it's defined in the hypothetical hive file we're constructing from as a required argument for the API as a whole; a variable that should have a consistent value across all requests constructed using that API object.

Once constructed using either the `.from_hive` or `.from_hive_file` methods, an API object can be addressed quickly and simply. For example, if we wanted to retrieve the information for a particular Widget object from our original `my_api` API, we'd just do the following:

```python
this_widget = my_api.Widget.get(widget_id=123456)
```

Again, the keyword argument `widget_id` is not part of the beekeeper codebase, but is defined in the hive file as being a variable needed for the endpoint related to the "get" action on the Widget APIObject. An action can be anything, as long as it's related to a particular Endpoint, and a particular HTTP method on that endpoint. In this case, the "Widget.get" action is likely related to a given Widget endpoint, and to the HTTP `GET` method on that endpoint.

To compare, an `update` action would likely related to the same Endpoint (taking the `widget_id` keyword argument), but might use the `PUT` HTTP method. A `create` action would probably attach to a different endpoint, since there wouldn't yet be a `widget_id` variable to pass, and would likely use the HTTP `POST` method. And a `list` action that retrieves all Widget objects would probably access yet another different endpoint, but use the same HTTP `GET` method as the original `get` action.

This abstraction allows developers to think more clearly about the actual object they're working with on the server, and more directly relate to what they're doing with that object. In comparison, while a well-designed REST API communicates clearly what's being done, a fully-built request still contains a substantial amount of detail that isn't meaningful. beekeeper, by minimizing the construction effort, provides the developer direct insight into the object structure of the server.

## Hive structure

Coming soon; for now, take a look at `hive_sample.json`.

## Notes

beekeeper does not currently do SSL certificate verification.