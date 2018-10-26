#!/usr/bin/python3
import glob, os, stat, subprocess, sys

def spiderdirs(basedir, callback, dirsonly= False):
  print('spiderdirs', basedir)
  if not os.path.isdir(basedir):  return
  proc = subprocess.Popen(['find', basedir], stdout=subprocess.PIPE)
  for line in proc.stdout:
    try:
      line= line.decode('utf-8').rstrip()  #;  print(line)
      if dirsonly and not os.path.isdir(line):  continue
      callback(line)
    except Exception: pass


