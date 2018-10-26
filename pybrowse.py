#!/usr/bin/python3
import glob, os, pathlib, subprocess, sys
from lib import g, gw, myfs, mylaunch

home= os.environ['HOME']
mybasedir= os.getcwd()
titlefont= ('TkTextFont', 15)

#==============================================================================
class Fmain(g.packframe):
  def populate(self):
    paths= [mybasedir]
    for path in sys.path:
      if path!= mybasedir and os.path.isdir(path):  paths.append(path)
    cr= self.ctlrow()
    self.wpath= cr.addwidget(gw.Woptionmenu, optionlist= paths, default= mybasedir)
    cr.control_button(text='Select', command= self.select_path)

    self.title('My scripts')
    cr= self.ctlrow()
    cr.control_button(text='Command line', command= lxterm)
    cr.control_button(text='Screenshot', command= screenshot)

    self.root.bind("<Return>", self.on_enter)
    cr= self.ctlrow()
    cr.control_button(text='Search', command= self.search)
    cr.control_button(text='Exec',   command= self.execute)
    self.wsearchpattern= cr.entry(50)

    self.pdirscroller= self.vscrollsubframe(Fscroll, basedir= mybasedir)

  def select_path(self):
    path= self.wpath.get()
    self.pdirscroller= self.scrollframe.pop_addinterior(Fscroll, basedir= path)

  def on_enter(self, whatever):
    pattern= self.wsearchpattern.get()
    if pattern== '':  return
    if pattern.startswith('./')  or '.py'  in pattern:  self.execute();  return 
    self.search()

  def search(self):
    pattern= self.wsearchpattern.get()
    if pattern== '':  return
    outspec= '/dev/shm/grep.lst'
    self.sfiles= []
    myfs.spiderdirs(mybasedir, self.search_addfile)
    command= ['grep', pattern]
    command.extend(self.sfiles)
    with open(outspec, "w") as outfile:  subprocess.call(command, stdout= outfile)
    mylaunch.spawn_edit(outspec)

  def search_addfile(self, spec):
    if '__pycache__' in spec:  return
    if not spec.endswith('.py'):  return
    self.sfiles.append(spec)

  def execute(self):
    cmdline= self.wsearchpattern.get()
    if cmdline== '':  return
    mylaunch.xterm_spawn(cmdline)

#==============================================================================
class Fscroll(g.packframe):
  def __init__(self, parent, basedir, *args, **kwargs):
    self.basedir= basedir;  super().__init__(parent, *args, **kwargs)

  def populate(self):
    self.pdir= None;  self.dirs= []
    myfs.spiderdirs(self.basedir, self.handle_dir)
    self.cr= self.g= None
    for sdir in sorted(self.dirs):   self.pop_dirbutton(sdir)

  def handle_dir(self, spec):
    if '__pycache__' in spec:  return
    if not os.path.isdir(spec):  return
    self.dirs.append(spec)

  def pop_dirbutton(self, spec):
    if not self.cr:  self.cr= self.ctlrow()
    if not self.g:   self.g=  self.cr.gridf(6)
    lpath= spec;  lpath= lpath.replace(self.basedir+ '/', '')
    self.g.button(text= lpath, command= lambda spec= spec: self.launchdir(spec))

  def launchdir(self, spec):
    #mylaunch.spawn(['pcmanfm', spec]);
    if self.pdir:  self.pdir.destroy()
    self.pdir= self.subframe(Fpdir, spec= spec, basedir= self.basedir)

def lxterm():      mylaunch.spawn(['lxterminal'], rundir= mybasedir)

def screenshot():
  g.minimize_main()
  os.system('gnome-screenshot -d 3 -f ~/screenshot.jpg')
  g.zoom_main()

#==============================================================================
class Fpdir(g.packframe):
  def __init__(self, parent, spec, basedir, *args, **kwargs):
    self.spec= spec;  self.basedir= basedir
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    spec= self.spec
    cr= self.ctlrow();  cr.wlabel(spec, font= titlefont);
    cr.control_button(text= 'Browse', command= lambda spec= spec: self.launchdir(spec))
    self.lfiles= glob.glob(spec+ '/*.py')
    g= self.gridf(4);  self.ffile= None
    for fspec in sorted(self.lfiles):
      mod= fspec
      mod= mod.replace(self.basedir+ '/', '')
      mod= mod.replace('.py', '')
      mod= mod.replace('/', '.')
      g.button(text= mod, command= lambda fspec= fspec, mod= mod: self.showfile(fspec, mod))

  def showfile(self, fspec, modname):
    if self.ffile:  self.ffile.destroy()
    self.ffile= self.subframe(Ffile, spec= fspec, modname= modname);

  def launchdir(self, spec):  mylaunch.spawn(['pcmanfm', spec]);

#==============================================================================
class Ffile(g.packframe):
  def __init__(self, parent, spec, modname, *args, **kwargs):
    self.spec= spec;  self.modname= modname
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    g= self.g= self.gridf(1);  spec= self.spec
    command= lambda spec= spec:  mylaunch.spawn_edit(spec)
    cr= g.ctlrow()
    cr.wlabel(spec, font= titlefont);  cr.control_button(text= 'Edit', command= command)
    self.inclass= False
    with open(spec, 'r') as f:
      linenumber= 0
      while True:
        line= f.readline()
        if not line:  break
        linenumber= linenumber+1
        line= line.rstrip()
        if len(line)== 0:  continue
        l0= line[0]
        if l0== '#':  continue
        if l0== ' ' or l0== "\t": 
          self.pop_interior_line(line, linenumber)
        else: 
          self.pop_check_class_closeout()
          self.pop_toplevel_line(line, linenumber)
      self.pop_check_class_closeout()

  def pop_toplevel_line(self, line, linenumber):
    if line.startswith('class '):
      self.classline= line
      self.classcr= cr= self.g.ctlrow();  self.classdefs= []
      cr.label(linenumber);  cr.wlabel(line);  self.inclass= True
      ptext= line[6:];  i=ptext.find('(')
      if i<0:  i=ptext.find(':')
      if i>0:  ptext= ptext[:i]
      cr.clip_button(self.modname+ '.'+ ptext)
      return
    if line.startswith('def '):
      cr= self.g.ctlrow()
      cr.label(linenumber);  cr.wlabel(line)
      ptext= line[4:];  i=ptext.find('(')
      if i>0:  ptext= ptext[:i]
      cr.clip_button(self.modname+ '.'+ ptext+ '()')

  def pop_check_class_closeout(self):
    if self.inclass:
      cd= self.classdefs;  print(str(cd))
      command= lambda cl= self.classline, cd= cd:  self.browse_class(cl, cd) 
      self.classcr.control_button(text='List', command= command)
      self.classcr= None
    self.inclass= False

  def pop_interior_line(self, line, linenumber):
    if not self.inclass:  return
    line= line.lstrip()
    if line.startswith('def '):  self.classdefs.append((line, linenumber))

  def browse_class(self, classline, classdefs):
    self.domodaldlg(Dclass, classline=classline, classdefs=classdefs)

#==============================================================================
class Dclass(g.packframe):
  def __init__(self, parent, classline, classdefs, *args, **kwargs):
    self.classline= classline;  self.classdefs= classdefs
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    self.title(self.classline)
    self.wlabel(self.classline, font= titlefont)
    scroller= self.vscrollsubframe(g.gridframe, wid=1)
    for (line, linenumber) in self.classdefs:
      cr= scroller.ctlrow()
      cr.label(linenumber);  cr.wlabel(line)
      ptext= line[4:];  i=ptext.find('(')
      if i>0:  ptext= ptext[:i]
      cr.clip_button('.'+ ptext+ '()'+ '   # '+ line)


#==============================================================================
g.justone('pybrowse') 
palette= { 'bggrid': '#444488', 'bgcolframe': '#333377', 'bgrowframe': '#222266',
           'control_button': '#7777cc' }
g.domain(Fmain, palette, fullscreen= True)


