Performance evaluation tools
============================

code_jube_template.xml
----------------------

A temaplate *JUBE* file as a skeleton for new codes to integrate the extraction process.


eocoe_jube.xml
--------------

The eocoe_jube.xml contains all general parameter and configurations to run an *JUBE* triggered metric extraction process (as described in EoCoE technical report).
The file can be used directly by using the *JUBE* include techniques or as a best practise data source.

create_tex.py
-------------

Allows the conversion of the final JSON metric files to a TEX table.

```bash
./create_tex.py -o output_filename.tex JSON_file1.json JSON_file2.json ...
```

Usage of extract_metrics.py
---------------------------

The extraction script is used to extract EoCoE related metrics out of different sources.

```bash
./extract_metrics.py [-t TAG] [-o OUTPUTFILE] subparser filename [optargs]
```

Time Extraction:

```bash
./extract_metrics.py time a_file #extract time in "time"-format
./extract_metrics.py time a_file -f libmem #extract time in "lib"-format
./extract_metrics.py time a_file -f usr #extract time in "/usr/bin/time"-format
```

Memory Extraction:

```bash
./extract_metrics.py mem a_file #extract memory in "libmem"-format
./extract_metrics.py mem a_file -f usr #extract mem in "/usr/bin/time"-format
./extract_metrics.py mem a_file -f slurm #extract mem by extracting the job_id out of the given file and using the sacct information
```

Scalasca Extraction:

```bash
./extract_metrics.py scaslasca a_file
```

Darshan Extraction:

```bash
./extract_metrics.py darshan a_file #will need numpy and darshan-parser available for execution, also the additional file darshanparser.py must be stored next to the extract_metrics.py script
```

PAPI Extraction:

```bash
./extract_metrics.py papi a_file #scalasca profile run file
```

Combination:

```bash
./extract_metrics.py combine a_file o_file #combine all metrics within one result file and create combined derived metrics (fma_eff, vec_eff, mem_vs_cmp)
```

