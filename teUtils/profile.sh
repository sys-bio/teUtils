#! /bin/bash
python -m cProfile tests/benchmarkModelFitter.py > profile.csv
echo " ncalls  tottime  percall  cumtime  percall filename:lineno(function)" > result.csv
grep namedTimeseries profile.csv >> result.csv
grep timeseriesPlotter profile.csv >> result.csv
grep modelFitter profile.csv >> result.csv
grep "_helper" profile.csv >> result.csv
