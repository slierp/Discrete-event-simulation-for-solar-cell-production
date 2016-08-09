rmdir build /s /q
rmdir dist /s /q
rmdir desc_pro.egg-info /s /q
cd desc-pro
del *.c
del *.pyc
del *.pyd
cd batchlocations
del *.c
del *.pyc
del *.pyd
cd ../dialogs
del *.c
del *.pyc
del *.pyd
cd ..
pause
