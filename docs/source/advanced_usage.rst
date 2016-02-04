Advanced Usage
==============

beekeeper is designed to be easy-to-use, but its structure also makes it
incredibly adaptable and powerful for advanced users. Right now, there are
three key advanced feature that you may want to take advantage of.

Methods as Variables
--------------------

When initializing a hive, you can pass callable objects like methods and
functions into beekeeper to use as values for variables, as long as there
aren't any variables that need to be used to call them. To avoid this, you
can do a few different things. First, and most easily, they can be object
instance methods. beekeeper will keep those methods linked to their original
contexts, and so their results will be based on the state of their parent
object. You can also use alternate forms of callables, like Python's built-in
"partial" object, which lets you fill in variable values ahead of time.

Either way you do it, you let your beekeeper-generated API move from a simple
static platform to a more robust and dynamic system. Perhaps the most common
use of this feature would be to tie into an OAuth authentication scheme, or some
other system that requires credentials to change automatically over time.

To set this up, just pass in an uncalled method or function as a variable when you
initialize the API. Every time you make an API call, your method will be executed,
and the returned value will be used as the value for that variable.

Custom Data Handlers
--------------------

beekeeper has built-in support for a number of different data types, and
automatically chooses between them based on the defined MIME type of data
being sent, or the Content-Type header of the data being received. Right now,
we can read JSON, plaintext, binary streams, and XML.

But, you might decide that you need something different. For example, you might
want to automatically parse a "text/csv" response into a set of lists, or you might
want to do that the other way around to post "text/csv" data to a server.

First, you'll need to define a data handler class. It should have at least one of
two possible static methods; "dump" and "load". "dump" takes a Python object and
encodes it to a bytes object in the appropriate format; "load" does exactly the
opposite.

Once you've defined your class, you'll need to add it to beekeeper by calling
"beekeeper.add_data_handler" with the data's MIME type as the first argument,
and the data handler class you defined as the second argument.

All told, it should look something like this:

.. code:: python

    class CSVHandler(object):

    @staticmethod
    def dump(python_object, encoding):
        """
        Logic goes here - take the Python object the method receives, and parse it
        into a bytes() object. For elements using text, be sure to use the text encoding
        passed to the "encoding" argument.
        """

    @staticmethod
    def load(response, encoding):
        """
        Again, logic goes here. beekeeper will pass you a bytes() object, as well as the
        encoding the bytes were sent in, and will expect to receive in response a Python
        object that's relevant to the data received.
        """

    beekeeper.add_data_handler('text/csv', CSVHandler)

Because you've informed beekeeper about the specific MIME type that the data handler
should be associated with, beekeeper now knows exactly when to use it; when you define
a data variable that has the defined MIME type of "text/csv", or when a response is
received from the server with "text/csv" in the "Content-Type" header. If a MIME type
doesn't have a data handler associated with it, beekeeper will just return the raw bytes received.

Custom Variable Types
---------------------

Sometimes, you have a variable that's a little particular in its needs, and which you
might want to make a bit easier to use. To do that, you can define a custom variable type
and handler to make things a bit simpler.

For example, when updating contact properties using the Hubspot API, a JSON object in the
following format is required:

.. code:: json

    {
        "properties": [
            {
                "property": "firstname",
                "value": "John"
            },
            {
                "property": "lastname",
                "value": "Smith"
            }
        ]
    }

It's a little bit verbose. And the whole goal of beekeeper is to make your life easier, so
you can put in a little work to make it easier still, just by defining a custom variable
handler and sticking it into beekeeper.

A variable handler takes keyword arguments of the defined type, processes them, and yields
"final variables" of one of the types beekeeper handles natively. Those four types are
as follows:

-   "url_param"
-   "header"
-   "url_replacement"
-   "data"

A final variable looks like this:

.. code:: python

    {'name': 'Content-Type', 'type': 'header', 'value': 'application/json'}

For an example of what a variable handler looks like, take the handler for "data"-type variables.
Now, I know what you're thinking: "Didn't he JUST say that data variables were handled natively?"
And they are. But there's a difference between the "data" variable as it exists on the hive, and the
"data" final variable as it's sent to the request handler.

The key is that a data variable within the hive actually contains multiple piece of information;
it contains the data being sent, sure, but it also contains MIME type information, which needs to
be written to the "Content-Type" header.

As a result, the handler for "data" variables returns an iterable containing two final variables;
a "data"-type final variable, and a "header"-type final variable. The built-in variable handlers
do this by yielding those individual items; acting as generators. This is the recommended behavior
for any custom handlers you build as well.

When you're building your custom data handler, you have a resource that'll make it much easier;
the "beekeeper.render_variables" method. This method will takes a single positional argument "var_type"
as well as any number of keyword arguments. It'll then return an iterable containing all the final
variables produced by the rendering process.

For example:

.. code:: python
    >>> my_data = {'value': 'This is my data!', 'mimetype': 'text/plain'}
    >>> for each in beekeeper.render_variables('data', my_data=my_data):
    ...     print(each)
    ...
    {'name': 'Content-Type', 'type': 'header', 'value': 'text/plain'}
    {type': 'data', 'value': b'This is my data!'}

Note that the "data" final object doesn't have a name; this is because body data doesn't have any
sort of variable name to go with it. It's just there.

Now that we've got some principles down, let's look at our original case. We want a simpler way to write
Hubspot contacts, so let's implement a custom variable type to handle getting them into the right format:

.. code:: python

    def hubspot_contact_handler(**values):
        #Typically, because this is a data-type object, we only receive one variable.
        for _, contact in values.items():
            x = {
                    'properties': [
                        {'property':prop, 'value': val} for prop, val in contact.items()
                    ]
                }
            return beekeeper.render_variables('data', data={'value': x, 'mimetype': 'application/json'})

This simple function will perform the transformation we're looking for (we can simply pass in a
dictionary containing the new variable values), and then pass it into the data-rendering pipeline, which
will yield both the body data we need, and the appropriate "Content-Type" header. Note that in this case,
we're simply returning the data-rendering generator, which is an iterable in itself. If you're manually
crafting your final variables, or using multiple variable handlers, then you'll need to built the
iterable yourself.

The final step is to bind your function to a new variable type so that when variables of that type are defined in your hive, your parsing scheme happens automatically. Just like with a custom data handler, it takes one step:

.. code:: python

    beekeeper.add_variable_handler('hs_contact', hubspot_contact_handler)
