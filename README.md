# beekeeper

## Description
beekeeper is a Python library designed around dynamically generating a RESTful client interface based on a minimal JSON hive.

The hive specification is designed to provide beekeeper (or other applications consuming hive files) with programmatically-designed insight into the structure of both the REST endpoints that are available and the objects and methods that those endpoints represent.

While the classes available in beekeeper can be used manually to create Pythonic representations of REST endpoints, it is strongly preferred that the library be used as a whole with a constructed hive file. As APIs become larger in scale (in terms of the number of endpoints and represented objects), the time benefit of beekeeper becomes more pronounced, as adding additional objects and endpoints is a trivial process.

## Requirements
beekeeper requires Python 3.4.3 or higher and its built-in modules.

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

Hives have several mandatory and optional nodes and subobjects that define the interaction with the remote API. Here's a basic rundown of what those look like; for a (completely non-functional) example, take a look at `hive_sample.json`. There are functional examples in the `hives` folder, but not all of them take advantage of all current features, and they may be out of date with the current hive specification.

###name

`name` is a plain string defining the name of the API. This is not currently used in beekeeper, but the potential applications include a hive file containing definitions for multiple APIs where namespaces for all APIs can be generated automatically.

###root

`root` is a plain string containing the base stub for the HTTP API. This is the fully-qualified domain name and subpath under which all resources for the entire API can be found. As an example, for Hubspot, this path is `https://api.hubapi.com`.

###mimetype

`mimetype` is a plain string containing the MIME type that most interactions with the API take place in. This is used to parse responses from servers when we're not able to automatically extract a Content-Type header.

###versioning

`versioning` is an optional object that enables you to define different versions of the API. In general, this shouldn't be necessary to use, as the whole point of beekeeper is to abstract away the specific implementation details of how a REST API works. However, if a feature is added or removed, it may be desirable to target a specific version of an API. To do this, you can pass the version you want to use as the `version` keyword argument to the `.from_hive_file()` or `.from_remote_hive()` constructor methods.

The `versioning` object has two keys; a `version` key that has a plain string or integer that can be easily compared against the value passed to the aforementioned constructors, and an optional "previousVersions" array that contains an arbitrary number of `version` objects.

Each `version` object contains two required keys (a `version` key similar to the one in the main `versioning` object, and a `location` key that provides a full URL that can be used to download the relevant hive file). It may also contain an optional `expires` key in ISO 8601 format, which declares if the API corresponding to that hive has a planned deprecation date from which it will no longer be available.

###variables

`variables` is an optional object containing any number of individual `variable` objects, keyed by name. Each `variable` object has a mandatory `type` key, corresponding to one of the valid variable types, and an optional `value` key, if the value for that variable should be kept static across all instantiations of this particular API. Variables that are defined at the API level must be filled in during initialization of the API by passing variables as arguments (if only one value is needed) or keyword arguments with the argument name corresponding to the variable name. Each `variable` may also have an `optional` key with a Boolean value. If a variable has `optional: true` set, then it will be ignored at execution time if a value is missing. Otherwise, an exception will be raised that a required variable is missing a value.

Variables at the API level will be applied to all requests made by the API, but can be overridden by being redefined at a lower level, or by passing a keyword argument with the relevant name during the execution of a call.

####Variable types

There are several variable types with different considerations.

*   `header`

    `header` variables are sent as HTTP headers.

*   `url_param`

    `url_param` variables are appended to the end of the URL that's being requested; for example, `https://company.tld/path?var1=value&var2=othervalue`

*   `url_replacement`

    `url_replacement` variables fill "holes" in incomplete URLs. For example, the path for an endpoint might be `/contacts/{contact_id}`. In that case, setting a `url_replacement` variable with name `contact_id` to a value of `123` would result in a path to be appended to the root of `/contacts/123`.

*   `http_form`

    `http_form` variables are similar to `url_param` variables, however, they're sent to the server as part of the body of the request, rather than within the URL. This is the method by which HTTP forms are typically sent. Due to the way `http_form` variables are sent, they cannot be sent simultaneously with other data.

*   `data`

    `data` variables can be any Python object which can be encoded by the encoder associated with the MIME type for that variable, set by the `mimetype` key in the object for that variable in the hive.

*   `http_basic_auth`
    
    `http_basic_auth` variables are translated into standard Authorization headers. Two variables of this type are generally needed; a `username` variable and a `password` variable. If one of these variables is not present, it will be treated as empty when  building the Authorization header.

#####MIME type support

Currently, support for different data formats is relatively minimal, but can be expanded by adding additional classes to `parsers.py`.

Supported types:

* `application/json`

* `text/plain`

* `text/html`

* `application/x-www-form-urlencoded` (typically, not used directly; use the `http-form` variable type instead)

###endpoints

`endpoints` is a required object that describes the different HTTP(s) URLs that are used as part of the API, and the variables and methods that can be used at that URL. Each `Endpoint` contains an optional `variables` key that will add to and override any values found at the API level. It also contains a required `path` key that completes the URL started by the API `root` key. Optionally, it contains a `methods` key that contains an array of the acceptable HTTP methods that can be used at that endpoint (defaulting to `GET`-only) and a `mimetype` key for use if that particular endpoint handles a different kind of data than the API as a whole.

###objects

`objects` is a required object that describes the different resources available via the API, and how the different actions that can be taken on them map onto different endpoints and methods. For example, a `Contact` object might have `create`, `update`, `get`, and `delete` actions. The `update`, `get`, and `delete` actions might map onto one endpoint with the `PUT`, `GET`, and `DELETE` HTTP methods, while the `create` action might map onto another endpoint with the `POST` HTTP method. `objects` helps abstract this to help you keep track more easily without worrying about implementation details.

`objects` contains any number of `APIObject` objects, keyed by name. Each of those `APIObject`s contains a `description` key, which isn't currently functional, but is useful for documentation purposes. Each may also contain an optional `id_variable` key, the value of which should be equal to the name of the variable which, if present, is the unique key of each record. This allows us to do subscription of objects by ID - for example, `Hubspot.Contacts[39410]`, rather than `Hubspot.Contacts.get(contact_id=39410)`.

####actions

`actions` is the key element of each `APIObject`. `actions` is an object that contains an arbitrary number of `action` objects related to that `APIObject`, keyed by name. Each `action` contains an `endpoint` key, the value of which must relate to one of the previously-defined `Endpoint` objects, and a `method` key that contains one of the HTTP methods available on that `Endpoint`. If `method` isn't present, the method is assumed to be `GET`.

Each `action` may also optionally contain a `mimetype` object and a `variables` object. The `variables` object behaves similarly to those places at the `Endpoint` and `API` levels; it will add to and override any values defined at a higher level, and will be filled by arguments and keyword arguments presented during execution.

The optional `mimetype` object may contain any or none of three keys; `takes`, `returns`, and `both`. This is a higher-detail version of the `mimetype` key present on the `API` and `Endpoint`. `takes` defines the type of data the API expects to receive from this action, `returns` defines the type of data that the API will return from this action, and `both` defines the expected data in both directions. This key is wholly optional and only necessary if the datatype in at least one direction differs from how it's defined at the `Endpoint` or `API` level.

## Notes

beekeeper does not currently do SSL certificate verification when used on Python versions earlier than 3.4.3. If ported to use urllib2 for python2 compatibility in future, SSL certificate verification will require 2.7.9 or later.
