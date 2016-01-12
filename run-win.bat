::python -m cProfile -o output Main.py -i test.desc -d 24 -p
::snakeviz output
python Main.py
pause
