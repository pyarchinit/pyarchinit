# modules/db/entities/DETSESSO.py

## Overview

This file contains 4 documented elements.

## Classes

### DETSESSO

*No description available.*
A data model class representing the sex determination record of a skeletal individual within an archaeological or bioarchaeological context. It stores 54 attributes covering the site identifier (`sito`), individual number (`num_individuo`), cranial morphological trait importance grades and values (glabella, mastoid process, nuchal crest, zygomatic process, supraorbital arch, tubercle, occipital protuberance, frontal inclination, zygomatic bone, and supraorbital margin), mandibular trait importance grades and values (palate, mandibular morphology, chin, mandibular angle, inferior margin, ascending ramus, and mandibular condyle), as well as pelvic sex indicators (`sup_p_I`–`sup_p_sex`, `in_isch_I`–`in_isch_sex`, `arco_c_sex`, `ramo_ip_I`–`ramo_ip_sex`, `prop_ip_sex`, `ind_bac_sex`) and overall cranial sex indices (`sex_cr_tot`, `ind_cr_sex`). The `__repr__` method returns a formatted string representation of all 54 fields.

**Inherits from**: object

#### Methods

##### __init__(self, id_det_sesso, sito, num_individuo, glab_grado_imp, pmast_grado_imp, pnuc_grado_imp, pzig_grado_imp, arcsop_grado_imp, tub_grado_imp, pocc_grado_imp, inclfr_grado_imp, zig_grado_imp, msorb_grado_imp, glab_valori, pmast_valori, pnuc_valori, pzig_valori, arcsop_valori, tub_valori, pocc_valori, inclfr_valori, zig_valori, msorb_valori, palato_grado_imp, mfmand_grado_imp, mento_grado_imp, anmand_grado_imp, minf_grado_imp, brmont_grado_imp, condm_grado_imp, palato_valori, mfmand_valori, mento_valori, anmand_valori, minf_valori, brmont_valori, condm_valori, sex_cr_tot, ind_cr_sex, sup_p_I, sup_p_II, sup_p_III, sup_p_sex, in_isch_I, in_isch_II, in_isch_III, in_isch_sex, arco_c_sex, ramo_ip_I, ramo_ip_II, ramo_ip_III, ramo_ip_sex, prop_ip_sex, ind_bac_sex)

Initializes a `DETSESSO` instance with 54 parameters representing a complete sex determination record for a skeletal individual. The parameters cover the record identifier (`id_det_sesso`), site (`sito`), and individual number (`num_individuo`), followed by cranial morphological trait importance grades and values (glabella, mastoid process, nuchal crest, zygomatic process, supraorbital arch, tubercle, occipital protuberance, frontal inclination, zygomatic bone, and supraorbital margin), mandibular trait importance grades and values (palate, mandibular morphology, chin, mandibular angle, inferior margin, ascending ramus, and mandibular condyle), and pelvic sex determination scores (`sex_cr_tot`, `ind_cr_sex`, `sup_p_I`–`sup_p_sex`, `in_isch_I`–`in_isch_sex`, `arco_c_sex`, `ramo_ip_I`–`ramo_ip_sex`, `prop_ip_sex`, `ind_bac_sex`). Each argument is assigned directly to the corresponding instance attribute.

##### __repr__(self)

Returns a string representation of a `DETSESSO` instance, formatting all 54 fields into a structured, human-readable string enclosed in angle brackets. The output includes integer and string representations of cranial and pelvic morphological grading values, importance scores, and sex determination indices, formatted using `%d`, `%r`, and `%s` conversion specifiers. This method is automatically invoked by `repr()` and provides a complete snapshot of the object's state for debugging or logging purposes.

