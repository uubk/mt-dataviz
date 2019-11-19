bin/plot_endtoend.py --inputBaseline data/perf-isl-gmp.txt --titleBaseline GMP --input data/perf-libint-multicol-macro.txt data/perf-multi.txt data/perf-isl-imath.txt data/perf-libint-multicol-macro-tp.txt --title 'libint multicol int32_t' 'Matrix-granularity transprecision(manual)' 'Element-granularity transprecision' 'Matrix-granulariy transprecision(automatic)' --output plots/endtoend
bin/plot_endtoend.py --inputBaseline data/perf-red-isl-gmp.txt --titleBaseline GMP --input data/perf-red-libint.txt data/perf-red-libint-tp.txt data/perf-red-libint-multicol.txt data/perf-red-libint-multicol-tp.txt data/perf-red-libint-multicol-macro.txt data/perf-red-libint-multicol-macro-tp.txt --title 'libint int32_t' 'libint tp' 'libint multicol int32_t' 'libint multicol tp' 'libint multicol macro int32_t' 'libint multicol macro tp' --output plots/overhead-multicol
bin/plot_endtoend.py --inputBaseline data/perf-red-isl-gmp.txt --titleBaseline GMP --input data/perf-red-libint.txt data/perf-red-multi.txt data/perf-red-isl-imath.txt data/perf-red-libint-tp.txt --title 'libint int32_t' 'Matrix-granularity transprecision(manual)' 'Element-granularity transprecision' 'Matrix-granulariy transprecision(automatic)' --output plots/endtoend-small
