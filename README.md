This is a collection of scripts used to convert data from GGcat and EqLocl to CSS3.0.

### Convert GGcat to CSS3.0

```
python GGcat_to_css3.py
```

This script is configured to use `sample_data/GGcat_big_2000.csv` as GGcat file (modify the `GGCAT_FILE` constant) and
creates corresponding `out.event`, `out.netmag`, `out.origerr`, `out.origin`, `out.remark` CSS3.0 files.

### Convert EqLocl to CSS3.0

This script converts EqLocl files to CSS3.0, and associates them with existing CSS3.0 tables.

```
python eqlocl_to_css3.py -d sample_data/ -p '/**/[GA|agso|ASC|MUN]*.txt' -o sample_data/sample_css.origin -e 
sample_data/sample_css.origerr -n sample_data/sample_css.netmag -r sample_data/sample_css.remark
```

Default configuration runs over `sample_data/` (modify the `EQLOCL_ROOT` constant, or pass as `-d` argument), and will
search through all its subdirectories for files in the form of `'/**/[GA|agso|ASC|MUN]*.txt'` to avoid non-eqlocl
files (modify `FILE_NAME_PATTERN` argument, pass as `-p` argument).

It will take eqlocl files and associate their values with 'close' origins from the existing CSS3.0 files (i.e.,
`sample_css.origin`, etc. by default -- modify `GAED_ORIGIN_FILE` constant, or pass as `-o` argument), and appends new
rows, or replacing empty values.

See all arguments by running: `python eqlocl_to_css3.py --help`.

Results are added to new CSS3.0 files (`eqlocl.netmag`, `eqlocl.origerr`, etc.). Actions taken are logged to `log.txt`.


### Installation

To install dependencies, run:

```
pip install -r requirements.txt
```

and then test by running:

```
nosetests
```

### TODO

- `assoc`, `arrival` and `event` tables are still to be associated in `eqlocl_to_css3.py`
