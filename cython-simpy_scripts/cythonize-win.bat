call "c:\Program Files (x86)\Common Files\Microsoft\Visual C++ for Python\9.0\VC\bin\vcvars32.bat"
copy setup-win.py c:\Python27\Lib\site-packages\simpy\
cd c:\Python27\Lib\site-packages\simpy\
python setup-win.py build_ext --inplace
python setup-win.py clean --all
del setup-win.py
pause
