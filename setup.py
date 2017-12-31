"""Setup Module für pyexe
"""
import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}
build_exe_options = {"packages" : ["svgwrite", "numpy"],
                     "includes" : ["tclwinbase",
                                   "tkiplotterprinter",
                                   "svgplotterprinter",
                                   "transformationmatrix",
                                   "plotterprinter"],
                     "include_files" : ["C:/Users/tiger/AppData/Local/Programs/Python/Python36-32/DLLs/tcl86t.dll",
                                        "C:/Users/tiger/AppData/Local/Programs/Python/Python36-32/DLLs/tk86t.dll",
                                        "Wimpelh150.jpg"],
                     "path": sys.path + ["src"]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = 'C:/Users/tiger/AppData/Local/Programs/Python/Python36-32/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'C:/Users/tiger/AppData/Local/Programs/Python/Python36-32/tcl/tk8.6'

setup(name="pygpsplotter",
      version="0.1",
      description="Produziert GPS Plotter für Seekarten",
      options={"build_exe": build_exe_options},
      executables=[Executable("src/pygpsplotmain.py", base=base)])

