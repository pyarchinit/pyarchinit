# modules/db/entities/DETETA.py

## Overview

This file contains 4 documented elements.

## Classes

### DETETA

*No description available.*
A data model class representing an age estimation record (`determinazione dell'età`) for a skeletal individual within an archaeological context. It stores a comprehensive set of osteological age indicators, including symphysis pubis scores (`sinf`, `SSPIA`–`SSPID`), auricular surface ranges (`sup_aur`), dental wear (`usura`), endocranial suture closure scores for ribs I–X (`Id_endo` through `Xs_endo`), cranial vault and lateral suture scores (`volta_1`–`volta_7`, `lat_6`–`lat_10`), and ectocranial suture ranges (`ecto_min`, `ecto_max`), each expressed as minimum/maximum age range values where applicable. The `__repr__` method returns a formatted string representation of all 56 fields, identified by `id_det_eta`, site (`sito`), and individual number (`nr_individuo`).

**Inherits from**: object

#### Methods

##### __init__(self, id_det_eta, sito, nr_individuo, sinf_min, sinf_max, sinf_min_2, sinf_max_2, SSPIA, SSPIB, SSPIC, SSPID, sup_aur_min, sup_aur_max, sup_aur_min_2, sup_aur_max_2, ms_sup_min, ms_sup_max, ms_inf_min, ms_inf_max, usura_min, usura_max, Id_endo, Is_endo, IId_endo, IIs_endo, IIId_endo, IIIs_endo, IV_endo, V_endo, VI_endo, VII_endo, VIIId_endo, VIIIs_endo, IXd_endo, IXs_endo, Xd_endo, Xs_endo, endo_min, endo_max, volta_1, volta_2, volta_3, volta_4, volta_5, volta_6, volta_7, lat_6, lat_7, lat_8, lat_9, lat_10, volta_min, volta_max, ant_lat_min, ant_lat_max, ecto_min, ecto_max)

Initializes a `DETETA` instance with 56 parameters representing skeletal age estimation data for an individual archaeological find. The parameters cover identification fields (`id_det_eta`, `sito`, `nr_individuo`), age range pairs for multiple osteological indicators including symphysis pubis (`sinf_min`/`sinf_max`), auricular surface (`sup_aur_min`/`sup_aur_max`), dental wear (`usura_min`/`usura_max`), endocranial suture closures (`Id_endo` through `Xs_endo`, `endo_min`/`endo_max`), vault and lateral cranial sutures (`volta_1`–`volta_7`, `lat_6`–`lat_10`, `volta_min`/`volta_max`, `ant_lat_min`/`ant_lat_max`), and ectocranial sutures (`ecto_min`/`ecto_max`). Note that `sinf_min_2` and `sup_aur_min_2` are assigned the values of `sinf_min` and `sup_aur_min` respectively, and `sinf_max_2` and `sup_aur_max_2` are assigned the values of `sinf_max` and `sup_aur_max`, regardless of the corresponding arguments passed.

##### __repr__(self)

Returns a formatted string representation of a `DETETA` instance, displaying all 56 fields as a sequence of integer values enclosed in `<DETETA(...)>` angle brackets. The output includes identifiers, site and individual references, and the full set of age estimation parameters spanning symphysis pubis indicators, auricular surface measurements, dental wear, endocranial suture closures, vault and lateral cranial metrics, and ecto-cranial range values. This method is intended for unambiguous object identification and debugging purposes.

