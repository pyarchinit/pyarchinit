# modules/db/pyarchinit_utility.py

## Overview

This file contains 22 documented elements.

## Classes

### Utility

*No description available.*
A general-purpose helper class providing a collection of data transformation and manipulation methods for Python lists, tuples, and dictionaries. Its methods cover operations such as converting tuples to lists, locating and replacing `'None'` string values, removing duplicates, extracting and comparing list elements, stripping Unicode-style quote wrappers from string items, and aggregating numeric values within lists of tuples. Additional utilities include dictionary manipulation (adding items, removing empty entries, extracting list-typed values), numeric formatting via `conversione_numeri`, and loading named queries from a text file via `getQuery`.

#### Methods

##### pos_none_in_list(self, l)

take a list of values and return the position number of the values
equal to 'None' 

##### tup_2_list(self, t, s, i)

take a tuple of strings, and return a list of lists of the values.
if s is set, add the value to the strings. If i is set return only the
value in the i position

##### tup_2_list_II(self, l)

take a list of tuples ad return a list of lists

##### tup_2_list_III(self, l)

take a list of tuples ad return a list of values

##### list_tup_2_list(self, l)

take a list of tuples ad return a list of lists

##### select_in_list(self, l, p)

take a list of lists or value and return the in a list of lists
the value taken by the value of p. 

##### count_list_eq_v(self, l, v)

take a list and a value. If the number of occurens of a
items inside the list is equal to v value, put the singol value
into list_res as a list. Return a list of lists

##### find_list_in_dict(self, d)

recives a dict and if contains a list of lists and
delete the item from the dict.
Return a tuple containin the new dict and a list of
tuples wich contain the keys and the values

##### add_item_to_dict(self, d, i)

receive a dict and a list containt tuple with key,value
and add them to dict

##### list_col_index_value(self, v1, v2)

return two lists into one tupla,
takin' two list with same lenght and lookin for the occurrences.
for every occurrences between v_1 and v_2 the v_2 value it's charged
into mod_value and its position in list it's put into list_index.

##### deunicode_list(self, l)

*No description available.*
Processes a list in-place by stripping enclosing quotation mark delimiters from string elements. For each string item, it removes triple double-quote (`"""`) wrappers or single double-quote (`"`) wrappers from the start and end of the value; non-string types (`int`, `float`, `date`, `datetime`, `NoneType`, `bool`, `list`, `dict`) and falsy values are left unchanged. Returns the modified list.

##### zip_lists(self, l1, l2)

*No description available.*
Combines two lists element-wise using `zip` and returns a list of elements that are equal at the same position in both lists. Iterates over each paired tuple and appends the element to the result only when both values in the pair are identical. Returns the resulting list if it contains at least one matching element, or `None` implicitly if no matches are found.

##### join_list_if(self, l1, l2, v1, v2)

*No description available.*
Performs a conditional join between two lists (`l1` and `l2`) using specified positional indices (`v1`, `v2`) as the join keys. For each element in `l1`, it searches `l2` for matching values at the respective positions, accounting for both exact matches and stripped string comparisons when the value is not an integer; matching elements from `l2` (from position `v2 + 1` onward) are appended to the corresponding `l1` element. Returns the resulting list of merged sublists if any matches are found, otherwise returns `None` implicitly.

##### extract_from_list(self, l, p)

*No description available.*
Iterates over the provided list `l` and extracts the element at position `p` from each item, storing each extracted element as a single-item list. The results are collected and returned as a new list of single-element lists. The method also assigns `l` and `p` to the instance attributes `self.list` and `self.pos` respectively before processing.

##### remove_empty_items_fr_dict(self, d)

*No description available.*
Iterates over all key-value pairs in the provided dictionary `d` and removes any entry whose value is an empty string (`""`), the literal string `"''"` or `'""'`, or `None`. Modification is performed in-place by calling `d.pop(k)` on matching keys, and the cleaned dictionary is returned.

##### findFieldFrDict(self, d, fn)

*No description available.*
Searches a dictionary `d` for a key whose value matches the specified field name `fn`. Iterates over all entries in the dictionary, returning the key associated with the matching value. If no match is found among the final entry evaluated, returns `None`.

##### remove_dup_from_list(self, ls)

*No description available.*
Accepts a list `ls`, assigns it to the instance attribute `self.list`, and sorts it in place. If the list contains more than one element, the method iterates through the sorted list and builds a new list `nl` containing only unique values by comparing each element to the previously recorded value, then returns `nl`. If the list contains one or fewer elements, the original sorted list is returned as-is.

##### sum_list_of_tuples_for_value(self, l)

*No description available.*
Accepts a list of two-element tuples, sorts it, and aggregates the numeric second values of tuples that share the same first value (string key). Tuples with matching keys are collapsed into a single tuple containing the key and the sum of their associated numeric values. Returns a new list of tuples with deduplicated keys and their corresponding summed values.

##### conversione_numeri(self, Numero)

*No description available.*
Converts a numeric value into a formatted Italian-style string representation, where thousands groups are separated by periods and the decimal part is appended after a final period. The method accepts either a numeric type or a string, coerces it to a string if necessary, splits the integer part into groups of three digits from the right, and extracts up to three decimal digits. The resulting string follows the pattern `groups.joined.by.dots.DD`, where the last segment represents the decimal portion.

##### getQuery(name)

*No description available.*
Opens the file `queries.txt` and searches line by line for the first line containing the specified `name` string. Upon finding a match, it splits that line on the `"="` character and stores the result, then breaks out of the loop. Returns the split result as a list if a match is found, or an empty string if no match exists or if the file cannot be opened; any exception encountered during file access is caught and its message printed to standard output.

