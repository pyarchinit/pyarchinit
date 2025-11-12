# tabs/networkaccessmanager.py

## Overview

This file contains 69 documented elements.

## Classes

### RequestsException

**Inherits from**: Exception

### RequestsExceptionTimeout

**Inherits from**: RequestsException

### RequestsExceptionConnectionError

**Inherits from**: RequestsException

### RequestsExceptionUserAbort

**Inherits from**: RequestsException

### Map

Example:
m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])

**Inherits from**: dict

#### Methods

##### __init__(self)

##### __getattr__(self, attr)

##### __setattr__(self, key, value)

##### __setitem__(self, key, value)

##### __delattr__(self, item)

##### __delitem__(self, key)

### Response

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

##### msg_log(self, msg)

##### httpResult(self)

##### request(self, url, method, body, headers, redirections, connection_type, blocking)

Make a network request by calling QgsNetworkAccessManager.
redirections argument is ignored and is here only for httplib2 compatibility.

##### downloadProgress(self, bytesReceived, bytesTotal)

Keep track of the download progress

##### requestTimedOut(self, QNetworkReply)

Trap the timeout. In Async mode requestTimedOut is called after replyFinished

##### replyFinished(self)

##### sslErrors(self, ssl_errors)

Handle SSL errors, logging them if debug is on and ignoring them
if disable_ssl_certificate_validation is set.

##### abort(self)

Handle request to cancel HTTP call

### RequestsException

**Inherits from**: Exception

### RequestsExceptionTimeout

**Inherits from**: RequestsException

### RequestsExceptionConnectionError

**Inherits from**: RequestsException

### RequestsExceptionUserAbort

**Inherits from**: RequestsException

### Map

Example:
m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])

**Inherits from**: dict

#### Methods

##### __init__(self)

##### __getattr__(self, attr)

##### __setattr__(self, key, value)

##### __setitem__(self, key, value)

##### __delattr__(self, item)

##### __delitem__(self, key)

### Response

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

##### msg_log(self, msg)

##### httpResult(self)

##### request(self, url, method, body, headers, redirections, connection_type, blocking)

Make a network request by calling QgsNetworkAccessManager.
redirections argument is ignored and is here only for httplib2 compatibility.

##### downloadProgress(self, bytesReceived, bytesTotal)

Keep track of the download progress

##### requestTimedOut(self, QNetworkReply)

Trap the timeout. In Async mode requestTimedOut is called after replyFinished

##### replyFinished(self)

##### sslErrors(self, ssl_errors)

Handle SSL errors, logging them if debug is on and ignoring them
if disable_ssl_certificate_validation is set.

##### abort(self)

Handle request to cancel HTTP call

### RequestsException

**Inherits from**: Exception

### RequestsExceptionTimeout

**Inherits from**: RequestsException

### RequestsExceptionConnectionError

**Inherits from**: RequestsException

### RequestsExceptionUserAbort

**Inherits from**: RequestsException

### Map

Example:
m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])

**Inherits from**: dict

#### Methods

##### __init__(self)

##### __getattr__(self, attr)

##### __setattr__(self, key, value)

##### __setitem__(self, key, value)

##### __delattr__(self, item)

##### __delitem__(self, key)

### Response

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

##### msg_log(self, msg)

##### httpResult(self)

##### request(self, url, method, body, headers, redirections, connection_type, blocking)

Make a network request by calling QgsNetworkAccessManager.
redirections argument is ignored and is here only for httplib2 compatibility.

##### downloadProgress(self, bytesReceived, bytesTotal)

Keep track of the download progress

##### requestTimedOut(self, QNetworkReply)

Trap the timeout. In Async mode requestTimedOut is called after replyFinished

##### replyFinished(self)

##### sslErrors(self, ssl_errors)

Handle SSL errors, logging them if debug is on and ignoring them
if disable_ssl_certificate_validation is set.

##### abort(self)

Handle request to cancel HTTP call

