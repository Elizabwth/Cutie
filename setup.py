import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                        "packages": ["os", "xml", "cgi", "hmac", "ctypes"], 
                        "excludes": ["tkinter"],
                        "include_files": ["res/"],
                        "zip_includes":[]
                    }

for fn in os.listdir("src/"):
    if fn[-3::] != ".py":
        if fn[-4::] != ".pyc":
            fn += "/"
        build_exe_options["zip_includes"].append(["src/"+fn,""])

print build_exe_options["zip_includes"]


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# uncomment for no console window
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(  name = "Cutie",
        version = "0.1",
        description = "Cutie Sync",
        options = {"build_exe": build_exe_options},
        executables = [
                        Executable("main.py", 
                        base=base,
                        targetName = "cutie.exe",
                        copyDependentFiles = True)])