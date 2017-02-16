rmdir build /s /q
rmdir dist /s /q
rmdir desc_pro.egg-info /s /q
cd desc-pro
del *.c
del *.pyc
del *.pyd
rmdir __pycache__ /s /q
cd batchlocations
del *.c
del *.pyc
del *.pyd
rmdir __pycache__ /s /q
cd ../dialogs
del *.c
del *.pyc
del *.pyd
rmdir __pycache__ /s /q
cd ..
pause
