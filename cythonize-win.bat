call "c:\Program Files (x86)\Common Files\Microsoft\Visual C++ for Python\9.0\VC\bin\vcvars32.bat"
python setup-win.py build_ext --inplace
python setup-win.py clean --all
