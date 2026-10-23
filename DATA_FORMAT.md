# Data formats

## Experiment dict (one per .paf)

Produced by `utils_shared/paf_reader.load_experiment_from_paf`, then extended by
the processing steps.

| key | type | meaning |
| --- | --- | --- |
| `experiment_name` | str | file stem |
| `metadata` | dict | `OD`, `volume`, `dilution_factor`, `events` |
| `metadata['events']` | list of dict | `datapoint`, `text`, `label`, `concentration_uM`, `time` (min) |
| `CcO2`, `CsO2`, `VoO2` | DataFrame | measured O2, set O2, OCR against time |
| `VoO2_OD` | DataFrame | OCR divided by dilution x OD x volume |
| `haem_conc`, `haem_abs`, `haem_delta_abs` (+ `_OD`) | DataFrame | decomposed haems |
| `raw_spectra` | dict | `{dataset: {wavelengths, time, transmission, attenuation}}`; dropped after the special figures are prepared |
| `averages` | dict | event-window averages (see below) |

### `averages`
`settings` (`vo2_source`, `haem_source`, window lengths), then one entry per
window (`average0` = baseline window, then one per event) holding the window
times and the mean of each OCR / haem series.

## Special figures (added by `utils_custom`)

### Per experiment, time response
- `group`: str, e.g. `knockdown`
- `spectral_averages`: `{window name: {'time_range', 'wavelengths', 'attenuation'}}`
- `difference_spectrum`: `{'wavelengths', 'values', 'minuend', 'subtrahend'}`
- `difference_decomposition`: `{'fitted', 'residual', 'haem_spectra': {haem: array}, 'haem_percentages': {haem: float}}`

### Triplicates (haem and OCR response)
`triplicate_averager` returns `{condition: {...}}` where condition is
`<strain>_<order>`: per window, the mean, SEM and per-run values of OCR and each
haem, the list of runs, and `settings` copied from the runs' `averages`.

## File names

- Haem and OCR response: `<control|knockdown>_<bd_then_kcn|kcn_then_bd>_run<N>`
- Time response: `<group>_<N>hours`

## Results folder

```
<results>/<experiment>/<experiment>.xlsx   one workbook per experiment
<results>/<experiment>/                    figure files
<results>/publication_figure/              special figures and their tables
```
