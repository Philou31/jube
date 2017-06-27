#!/bin/bash

jube -vvv run result_creation.xml
jube analyse bench_run/ --id $1
jube result bench_run/ --id $1
