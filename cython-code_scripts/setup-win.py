import os
from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

ext_modules=[
    Extension("RunSimulation", ["RunSimulation.py"]),
    Extension("batchlocations.BatchClean", ["batchlocations/BatchClean.py"]),
    Extension("batchlocations.BatchContainer", ["batchlocations/BatchContainer.py"]),
    Extension("batchlocations.BatchProcess", ["batchlocations/BatchProcess.py"]),
    Extension("batchlocations.BatchTex", ["batchlocations/BatchTex.py"]),
    Extension("batchlocations.BatchTransport", ["batchlocations/BatchTransport.py"]),
    Extension("batchlocations.Buffer", ["batchlocations/Buffer.py"]),
    Extension("batchlocations.IonImplanter", ["batchlocations/IonImplanter.py"]),
    Extension("batchlocations.Operator", ["batchlocations/Operator.py"]),
    Extension("batchlocations.PrintLine", ["batchlocations/PrintLine.py"]),
    Extension("batchlocations.SingleSideEtch", ["batchlocations/SingleSideEtch.py"]),
    Extension("batchlocations.TubeFurnace", ["batchlocations/TubeFurnace.py"]),
    Extension("batchlocations.TubePECVD", ["batchlocations/TubePECVD.py"]),
    Extension("batchlocations.WaferBin", ["batchlocations/WaferBin.py"]),
    Extension("batchlocations.WaferSource", ["batchlocations/WaferSource.py"]),
    Extension("batchlocations.WaferUnstacker", ["batchlocations/WaferUnstacker.py"])
]

setup(
	cmdclass = {'build_ext': build_ext},
	ext_modules = ext_modules
)
