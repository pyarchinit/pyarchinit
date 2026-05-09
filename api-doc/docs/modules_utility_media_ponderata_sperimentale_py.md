# modules/utility/media_ponderata_sperimentale.py

## Overview

This file contains 9 documented elements.

## Classes

### Cronology_convertion

*No description available.*
A utility class for converting and processing archaeological chronological data expressed as textual period labels (e.g., `"I sec. a.C."`, `"II meta' III sec. a.C."`) into numeric date intervals. It provides methods to parse period strings against a predefined dictionary of BC date ranges, calculate percentage distributions across chronological spans, and aggregate fractional values grouped by chronological unit. Additional helper methods support interval length computation, weighted average calculations over sorted chronological lists, and validation of whether a partial interval overlaps a reference interval.

#### Methods

##### sum_list_of_tuples_for_value(self, l)

*No description available.*
Accepts a list of two-element tuples, sorts it, and aggregates the numeric values (second element) of all tuples that share the same key (first element). The method iterates through the sorted list, accumulating values for consecutive matching keys and appending a consolidated tuple to the result list each time the key changes or the end of the list is reached. Returns a new list of tuples where each unique key appears exactly once, paired with the sum of all its associated values.

##### convert_data(self, datazione_reperto)

*No description available.*
Converts a textual Italian archaeological dating string (e.g., `"I sec. a.C."`, `"Meta' IV"`) into a numeric temporal interval by matching it against a predefined dictionary of period labels mapped to BCE year-range tuples.

If the input string contains a single recognizable period label, the method returns a two-element list with the corresponding start and end year values. If the string encodes a range spanning two consecutive period labels (separated by a fixed-width delimiter), the method combines the start year of the first match with the end year of the second, returning the broader interval; if no match is found, an empty list is returned.

##### found_intervallo_per_forma(self, data)

*No description available.*
Accepts a `data` parameter and is intended to determine or retrieve a time interval associated with a given form. The method body is not yet implemented, as indicated by the `pass` statement, and currently returns `None` implicitly. No logic, return value, or exception handling is defined in the source.

##### calc_percent(self, val_parz, val_totale)

*No description available.*
Calculates the percentage that a partial value represents relative to a total value. It applies the proportion formula `val_parz * 100 / val_totale` and returns the resulting percentage. Both `val_parz` (partial value) and `val_totale` (total value) are expected to be numeric, and `val_totale` must be non-zero.

##### media_ponderata_perc_intervallo(self, lista_dati, valore)

*No description available.*
Searches a sorted list of data entries (`lista_dati`) for the contiguous interval of records matching the specified `valore`, returning the start and end chronological boundaries of that interval.

The method sorts a duplicate reference of `lista_dati`, then iterates through it to identify the first occurrence of `valore` and tracks the trailing end timestamp (`cron_fin_temp`) until a record with a different value is encountered. Returns a tuple `(cron_iniz, cron_fin)` representing the opening and closing boundaries of the matched interval.

##### totale_forme_min(self, data)

*No description available.*
Iterates over the provided `data` sequence and accumulates the values found at index `1` of each element into a running counter. Returns the total sum of those values as an integer. Each element in `data` is expected to be an indexable structure where the second item (`[1]`) holds a numeric value.

##### intervallo_numerico(self, lista_intervalli_cron_i_f)

*No description available.*
Computes the numeric interval (duration) for each entry in the provided list of chronological intervals. For every element in `lista_intervalli_cron_i_f`, it calculates the difference between the end value (`i[1][1]`) and the start value (`i[1][0]`), pairing the result with the corresponding identifier (`i[0]`). Returns a list of two-element lists, each containing the identifier and its computed numeric interval.

##### check_value_parz_in_rif_value(self, val_parz, val_rif)

*No description available.*
Checks whether a partial value interval (`val_parz`) overlaps with a reference value interval (`val_rif`), where each interval is represented as a two-element sequence defining a numeric range.

Returns `0` if `val_parz` lies entirely outside `val_rif` — either when the start of `val_parz` exceeds the upper bound of `val_rif`, or when both bounds of `val_parz` fall below the lower bound of `val_rif`. Returns `1` in all other cases, indicating that the partial value falls at least partially within the reference range.

