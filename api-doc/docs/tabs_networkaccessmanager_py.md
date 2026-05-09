# tabs/networkaccessmanager.py

## Overview

This file contains 23 documented elements.

## Classes

### RequestsException

*No description available.*
Base exception class for the requests module, inheriting from Python's built-in `Exception`. Serves as the parent class for more specific request-related exceptions, including `RequestsExceptionTimeout` and `RequestsExceptionConnectionError`. Custom exception handling can target this class to catch any requests-related error in a single handler.

**Inherits from**: Exception

### RequestsExceptionTimeout

*No description available.*
An exception class representing a timeout error that occurs during a request operation. It inherits from `RequestsException`, which itself extends the built-in `Exception` class. This class introduces no additional attributes or methods beyond those provided by its parent classes.

**Inherits from**: RequestsException

### RequestsExceptionConnectionError

*No description available.*
A subclass of `RequestsException` that represents a connection error occurring during a request. It inherits all behavior from `RequestsException` without adding additional methods or attributes. This exception can be raised and caught distinctly from other request-related exceptions such as `RequestsExceptionTimeout` and `RequestsExceptionUserAbort`.

**Inherits from**: RequestsException

### RequestsExceptionUserAbort

*No description available.*
A specialized exception class that extends `RequestsException` to represent a user-initiated abort of a request. It inherits all behavior from its parent class `RequestsException` without adding additional attributes or methods. This exception can be raised to signal that a request was deliberately cancelled or aborted by the user.

**Inherits from**: RequestsException

### Map

Example:
m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])

**Inherits from**: dict

#### Methods

##### __init__(self)

Initializes a `Map` instance by accepting any combination of positional dictionary arguments and keyword arguments. Each key-value pair from any `dict` passed as a positional argument is stored directly on the instance, as are all keyword arguments. This allows the object to be constructed with a syntax such as `Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])`.

##### __getattr__(self, attr)

*No description available.*
Intercepts attribute access on the object and delegates it to the dictionary's `get` method using the requested attribute name as the key. This allows dictionary entries to be retrieved using dot notation (e.g., `obj.key`) in addition to standard bracket notation. Returns `None` if the key does not exist, consistent with the default behavior of `dict.get`.

##### __setattr__(self, key, value)

*No description available.*
Intercepts attribute assignment on the object and delegates to `__setitem__` rather than the default attribute-setting mechanism. This ensures that setting an attribute via dot notation (e.g., `obj.key = value`) is equivalent to setting it as a dictionary item. As a result, both the dictionary contents and the instance's `__dict__` are kept in sync through the underlying `__setitem__` implementation.

##### __setitem__(self, key, value)

Sets a key-value pair in both the underlying dictionary and the instance's `__dict__`, ensuring that the entry is accessible via both dictionary-style (`obj[key]`) and attribute-style (`obj.key`) access. Delegates to the parent class `Map`'s `__setitem__` via `super()` before synchronising the instance dictionary with the new key-value pair.

##### __delattr__(self, item)

*No description available.*
Delegates attribute deletion to the `__delitem__` method, ensuring that removing an attribute via `del obj.attr` syntax is handled consistently with item deletion. This maintains synchronization between the object's dictionary (`__dict__`) and the underlying map by routing both attribute-style and item-style deletion through a single code path.

##### __delitem__(self, key)

*No description available.*
Deletes an item from the `Map` by removing it from both the underlying mapping (via the parent class `__delitem__`) and from the instance's `__dict__`. This ensures that attribute-style access and item-style access remain synchronized after deletion. It is also invoked internally by `__delattr__` when an attribute is deleted using the `del` statement.

### Response

*No description available.*
A subclass of `Map` with no additional methods or attributes defined. It inherits all behavior from `Map`, including attribute-style and dictionary-style access to its items. See the `Map` implementation for full details on inherited functionality.

**Inherits from**: Map

### NetworkAccessManager

This class mimicks httplib2 by using QgsNetworkAccessManager for all
network calls.
The return value is a tuple of (response, content), the first being and
instance of the Response class, the second being a string that contains
the response entity body.
Parameters
----------
debug : bool
    verbose logging if True
exception_class : Exception
    Custom exception class
Usage 1 (blocking mode)
-----
::
    nam = NetworkAccessManager(authcgf)
    try:
        (response, content) = nam.request('http://www.example.com')
    except RequestsException as e:
        # Handle exception
        pass
Usage 2 (Non blocking mode)
-------------------------
::
    NOTE! if blocking mode returns immediatly
          it's up to the caller to manage listeners in case
          of non blocking mode
    nam = NetworkAccessManager(authcgf)
    try:
        nam.request('http://www.example.com', blocking=False)
        nam.reply.finished.connect(a_signal_listener)
    except RequestsException as e:
        # Handle exception
        pass
    Get response using method:
    nam.httpResult() that return a dictionary with keys:
        'status' - http code result come from reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        'status_code' - http code result come from reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        'status_message' - reply message string from reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)
        'content' - bytearray returned from reply
        'ok' - request success [True, False]
        'headers' - Dicionary containing the reply header
        'reason' - fomatted message string with reply.errorString()
        'exception' - the exception returne dduring execution

**Inherits from**: object

#### Methods

##### __init__(self, authid, disable_ssl_certificate_validation, exception_class, debug)

Initializes a new instance of the class with the provided configuration parameters, setting up the internal state for an HTTP network request. Assigns `authid`, `disable_ssl_certificate_validation`, `debug`, and `exception_class` to their corresponding instance attributes, and initializes `reply`, `on_abort`, and `blocking_mode` to their default values. Creates a default `http_call_result` as a `Response` object with zeroed status fields, empty content and headers, and `ok` set to `False`.

##### msg_log(self, msg)

Logs a message to the QGIS message log under the `"NetworkAccessManager"` tag using `QgsMessageLog.logMessage`. The message is only logged if the instance's `debug` attribute evaluates to `True`; otherwise, the method performs no action.

##### httpResult(self)

*No description available.*
Returns the result of the most recent HTTP network call by providing access to the internal `http_call_result` attribute. This method serves as a getter, exposing the stored response from the last request made via the network access manager.

##### request(self, url, method, body, headers, redirections, connection_type, blocking)

Make a network request by calling QgsNetworkAccessManager.
redirections argument is ignored and is here only for httplib2 compatibility.

##### downloadProgress(self, bytesReceived, bytesTotal)

Keep track of the download progress

##### requestTimedOut(self, QNetworkReply)

Trap the timeout. In Async mode requestTimedOut is called after replyFinished

##### replyFinished(self)

*No description available.*
Slot invoked when the network reply completes, responsible for processing the full HTTP response and populating `http_call_result` with the status code, status message, headers, and response body. If a network error is present, it constructs an appropriate error message and assigns a corresponding exception (`RequestsExceptionTimeout`, `RequestsExceptionConnectionError`, `RequestsExceptionUserAbort`, or `RequestsException`) to `http_call_result.exception`, with any configured `exception_class` taking precedence. If the response indicates a redirection, the method follows it by issuing a new request; otherwise, it reads the response body, logs the full response details, and cleans up the reply object by disconnecting all signals and scheduling it for deletion.

##### sslErrors(self, ssl_errors)

Handle SSL errors, logging them if debug is on and ignoring them
if disable_ssl_certificate_validation is set.

##### abort(self)

Handle request to cancel HTTP call

