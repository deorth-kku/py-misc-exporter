#!/bin/python3
import os
import pkgutil

pkgpath = os.path.dirname(__file__)
pkgname = os.path.basename(pkgpath)

for _, file, _ in pkgutil.iter_modules([pkgpath]):
    __import__(pkgname+'.'+file)
if __name__ == "__main__":
    pass
