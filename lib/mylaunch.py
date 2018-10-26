#!/usr/bin/python3
import os, os.path, subprocess, sys

def pkill(name):  subprocess.run(['pkill', name])

def spawn(cmd, rundir= None, env= None):
  print('spawn', str(cmd))
  if rundir:  print('spawn rundir=', rundir)
  # https://stackoverflow.com/questions/31015591/spawn-and-detach-process-in-python
  # https://stackoverflow.com/questions/2613104/why-fork-before-setsid
  spawnenv= dict(os.environ); p= None
  if env:
    for k in env.keys():  spawnenv[k]= env[k]
  try: p= subprocess.Popen(cmd, env= spawnenv, cwd= rundir, start_new_session= True)
  except Exception as e:   print('spawn EXCEPTION:', str(cmd), str(e));  return -1
  print('spawn pid', str(p.pid))
  return int(str(p.pid))
  # return value is spawned pid

def xterm_spawn(cmd, rundir= None):  return spawn(['xterm', '-e', cmd], rundir)

def spawn_edit(spec):  spawn(['pluma', spec])

def spawn_viewdir(spec):  spawn(['pcmanfm', spec])


