# modules/utility/pyarchinit_error_check.py

## Overview

This file contains 7 documented elements.

## Classes

### Error_check

*No description available.*
A utility class that provides a collection of basic data validation methods. It includes checks for empty data, integer and float convertibility, string length constraints, and duplicate detection within a list. Each validation method returns `0` or `1` (or a boolean for `checkIfDuplicates_3`) to indicate failure or success of the respective check.

#### Methods

##### data_is_empty(self, d)

*No description available.*
Checks whether the provided data `d` is empty or evaluates to a falsy value. Returns `0` if the data is empty (i.e., `bool(d)` evaluates to `False`), or `1` if the data is non-empty. This method is part of the `Error_check` class and is intended for basic data validation.

##### data_is_int(self, d)

*No description available.*
Attempts to cast the provided value `d` to an integer using Python's built-in `int()` function. Returns `1` if the conversion succeeds, or `0` if any exception is raised during the attempt. This method serves as a simple integer validation check for the given input.

##### data_lenght(self, d, l)

*No description available.*
Validates that the length of the given data `d` does not exceed the specified limit `l`. Returns `0` if the length of `d` is greater than `l`, indicating a validation failure, or `1` if the length is within the acceptable range, indicating success.

**Parameters:**
- `d` — The data whose length is to be checked.
- `l` — The maximum allowable length.

**Returns:** `0` if `len(d) > l`, otherwise `1`.

##### data_is_float(self, d)

*No description available.*
Attempts to convert the given value `d` to a `float`. Returns `1` if the conversion succeeds, or `0` if it raises an exception. This method effectively validates whether the provided input can be interpreted as a floating-point number.

##### checkIfDuplicates_3(listOfElems)

Check if given list contains any duplicates 

