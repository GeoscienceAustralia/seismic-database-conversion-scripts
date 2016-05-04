This is a collection of scripts used to convert data from GGcat and EqLocl to CSS3.0.

### Convert GGcat to CSS3.0

```
python GGcat_to_css3.py
```

This script is configured to use `sample_data/GGcat_big_2000.csv` as GGcat file (modify the `GGCAT_FILE` constant) and
creates corresponding `out.event`, `out.netmag`, `out.origerr`, `out.origin`, `out.remark` CSS3.0 files.

### Convert EqLocl to CSS3.0

Assuming you have either run the above command to create CSS3.0 files (`out.event`, `out.netmag`, etc.), or they
already exit.

```
python eqlocl_to_css3.py
```

This script is configured to use a directory root `sample_data/` (modify the `EQLOCL_ROOT` constant), and will
search through all its subdirectories for files in the form of `'/**/[GA|agso|ASC|MUN]*.txt'` (to avoid non-eqlocl
files).

It will take eqlocl files and associate their values with 'close' origins from the existing CSS3.0 files (i.e.,
`out.event`, etc.) -- appending new rows, or replacing empty values.

Results are added to new CSS3.0 files (`eqlocl.netmag`, `eqlocl.origerr`, etc.). Actions taken are logged to `log.txt`.


### TODO

- finish associating `assoc` and `arrival` tables in `eqlocl_to_css3.py`
