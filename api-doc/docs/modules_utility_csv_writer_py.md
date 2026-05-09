# modules/utility/csv_writer.py

## Overview

This file contains 12 documented elements.

## Classes

### UTF8Recoder

Iterator that reads an encoded stream and reencodes the input to UTF-8

#### Methods

##### __init__(self, f, encoding)

*No description available.*
Initializes the iterator with an encoded input stream and the specified encoding. Wraps the provided file-like object `f` using `codecs.getreader(encoding)`, storing the resulting reader as `self.reader` for use during iteration.

##### __iter__(self)

*No description available.*
Returns the iterator object itself (`self`), making instances of this class usable as iterators. This method satisfies the iterator protocol, enabling the object to be used in iteration contexts such as `for` loops. The actual iteration logic is delegated to `__next__`.

##### __next__(self)

*No description available.*
Returns the next row from the underlying reader, encoded as a UTF-8 byte string. This method delegates to `self.reader.next()` to retrieve the next value and applies `.encode("utf-8")` before returning it. It enables the object to function as a Python iterator, working in conjunction with `__iter__`.

### UnicodeReader

A CSV reader which will iterate over lines in the CSV file "f",
which is encoded in the given encoding.

#### Methods

##### __init__(self, f, dialect, encoding)

*No description available.*
Initializes a Unicode-aware CSV reader for the file object `f`. The file is first wrapped in a `UTF8Recoder` instance to transcode it from the specified `encoding` into UTF-8, and the resulting stream is passed to `csv.reader` using the given `dialect` and any additional keyword arguments `**kwds`. The constructed `csv.reader` is stored as `self.reader` for use during iteration.

##### __next__(self)

*No description available.*
Advances the underlying CSV reader to the next row and returns it as a list of Unicode strings. Each element in the row is decoded from its UTF-8 byte representation to a `str` object. This method enables the class to function as a Python iterator, supporting use in `for` loops and other iteration contexts.

##### __iter__(self)

*No description available.*
Returns the iterator object itself. This method makes the class an iterator by satisfying the iterator protocol, allowing instances to be used directly in iteration contexts such as `for` loops. It works in conjunction with `__next__` to enable sequential row-by-row traversal.

### UnicodeWriter

A CSV writer which will write rows to CSV file "f",
which is encoded in the given encoding.

#### Methods

##### __init__(self, f, dialect, encoding)

*No description available.*
Initializes a Unicode-aware CSV writer that writes rows to the file object `f` using the specified `dialect` (defaulting to `csv.excel`) and `encoding` (defaulting to `"utf-8"`). An internal `io.StringIO` queue is created to buffer output, a standard `csv.writer` is attached to that queue, and an incremental encoder is instantiated for the given encoding. Any additional keyword arguments are forwarded directly to the underlying `csv.writer`.

##### writerow(self, row)

*No description available.*
Encodes each element of `row` to UTF-8 and writes it using the underlying `csv.writer` to an internal queue buffer. The buffered data is then re-encoded into the target encoding via the incremental encoder and written to the output stream. Finally, the internal queue is truncated to prepare it for the next write operation.

##### writerows(self, rows)

*No description available.*
Iterates over the provided `rows` collection and writes each row individually by calling `self.writerow(row)` for every element. This method serves as a convenience wrapper for batch-writing multiple rows in a single call.

**Parameters:**
- `rows` — An iterable of rows, where each row is passed directly to `writerow`.

