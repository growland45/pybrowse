import os, os.path, signal, sys
from tkinter import *
from lib import gframe, gw

root= mw= None;  screen_width= 640;  screen_height= 480

def dbg(text):  print (text, file= sys.stderr)

def domain(mainframeclass, palette= None, fullscreen= False,
           geometry= None, packfirst= False, **sfkwargs):
  global root, mw, screen_height
  if not palette:  palette= mainframeclass.palette
  root= domain_makeroot(palette, fullscreen, geometry)
  #print('mainframeclass:', str(mainframeclass));  print('sfkwargs:', str(sfkwargs))
  mw= mainframeclass(root, **sfkwargs)
  domain_window(root, mw, packfirst= packfirst)
  domain_killroot()

def domodal(frameclass, modalparent= None, fullscreen= False,
            geometry= None, title= None, **sfkwargs):
  global root
  if not modalparent:  modalparent= root
  mroot= domain_maketoplevel(modalparent.root.palette, fullscreen, geometry)
  #print('g.domodal, sfkwargs: ', str(sfkwargs))
  mow= frameclass(mroot, **sfkwargs);  mow.modalparent= modalparent
  if title:  mow.title(title)
  mow.grab_set();  domain_window(mroot, mow, loop= False)
  # if loop is true, no return until main app is closed.
  # otherwise immediate return with modal still running
  # both pretty damn useless

def domain_makeroot(palette= None, fullscreen= False, geometry= None):
  global root, screen_width, screen_height
  root = Tk();  root_config(root, palette, fullscreen, geometry)
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  gframe.compute_default_fonts(screen_width)
  return root

def domain_killroot(force= False):
  global root; r2= root
  if root:
    root= None;  r2.quit()
    if force:  r2.destroy()

def root_config(root, palette= None, fullscreen= False, geometry= None):
  root.palette= palette;  root.bgcolor= gframe.choosecolor(palette, 'bggrid', '#555555')
  if   fullscreen:  root.wm_attributes('-zoomed', 1)
  elif geometry:    root.geometry(geometry)
  else:             root.geometry('+0+0')
  root.root= root   # for g.packframe

def domain_maketoplevel(palette= None, fullscreen= False, geometry= None):
  root = Toplevel();  root_config(root, palette, fullscreen, geometry)
  return root

from lib import myio

def domain_window(root, mw, loop= True, packfirst= False):
  try:
    if packfirst:  mw.pack(fill=BOTH, expand=True);  mw.populate()
    else:          mw.populate();  mw.pack(fill=BOTH, expand=True)
  except Exception as e:  myio.log_exception(e)
  if loop:  domain_loop(root, mw)

def domain_loop(root, mw):
  root.mainloop()  # doesn't seem to make a difference for modals

#----------------------------------------------------------------------------
def zoom_main():  global root;  root.wm_attributes('-zoomed', 1)
def minimize_main():  global root;  root.wm_state('iconic')

def update_main(idleonly= True):
  global root;
  if not root:  return  
  if idleonly:  root.update_idletasks()
  else:         root.update()

timerjob= None
def aftersec_main(delay_sec, callback, *args):
  global root, timerjob;
  if timerjob:  
    try:  root.after_cancel(timerjob)
    except Exception:  pass
  timerjob= root.after(int(delay_sec*1000), callback, *args)

def refresh_main():  global mw;  mw.refresh()

def quit():  global root;  root.destroy()

def killmain():
  global root
  try:     root.destroy()
  except:  pass
  root= None

def fontsize_from_gridwid(wid, chinese= True):
  maxfontsizew= screen_width*  0.62
  maxfontsizeh= screen_height* 0.4
  fontsize= maxfontsizew/wid
  if fontsize> maxfontsizeh:  fontsize= maxfontsizeh
  if not chinese:  fontsize= fontsize* 1.4
  return int(fontsize)

#-----------------------------------------------------------------------

def clipget():
  global root
  if root== None:
    temproot= Tk();
    try:               text= temproot.clipboard_get()
    except Exception:  text= ''
    temproot.destroy()
    return text
  try:               text= root.clipboard_get()
  except Exception:  text= ''
  return text

def clipput(text):
  global root;  tr= root
  if tr== None:  tr= Tk()
  try:  tr.clipboard_clear();  tr.clipboard_append(text);  tr.update()
  except Exception as e:  print('CLIP FAILED', str(e))
  if root== None:  tr.destroy()

def stringvar():  return StringVar()

def TODO(sfile):  gframe.TODOlaunch(sfile)

#--------------------------------------------------------------------------------
def justone(appname):
  pidfile= "/dev/shm/."+ appname+ ".pid"
  if os.path.isfile(pidfile):
    try:
      fi= open(pidfile, 'r');  opid= int(fi.read());  fi.close()
      print(appname, "was running as", str(opid))
      os.kill(opid, signal.SIGKILL)
    except Exception:  pass
  fo = open(pidfile, "w");  fo.write(str(os.getpid()));  fo.close()

#=====================================================================================
class packframe(gframe.myframe):
  def packw(self, tkw, **pkwargs):
    fill= BOTH;  expand= True
    if 'expand' in pkwargs:  expand= pkwargs['expand']
    if 'fill' in pkwargs:    fill= pkwargs['fill']
    tkw.pack(fill= fill, side=TOP, expand= expand, anchor='nw', pady= 2)

  def colf(self, **sfkwargs):          return self.subframe(packframe, **sfkwargs)
  def ctlrow(self, **sfkwargs):        return self.subframetight(rowframe, **sfkwargs)
  def rowf(self, **sfkwargs):          return self.subframe(rowframe, **sfkwargs)
  def gridf(self, wid= 1, **sfkwargs):
    return self.subframetight(gridframe, wid= wid, **sfkwargs)

  def clip_button(self, cliptext):
    self.control_button(text='Clip',
                        command= lambda t=cliptext: clipput(t))

  def domodaldlg(self, frameclass, **kwargs):
    domodal(frameclass, modalparent= self, **kwargs)

  def kill(self):        killmain();  sys.exit(0)    

#--------------------------------------------------------------------
class rowframe(packframe):
  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.row= 0;  self.col= 0;  self.wid= 0
    self.choosebg('bgrowframe')
 
  def packw(self, tkw, **kwargs):
    fill= X;  expand= True
    if 'expand' in kwargs:  expand= kwargs['expand']
    if 'fill' in kwargs:    fill=   kwargs['fill']
    tkw.pack(fill= fill, side= LEFT, expand= expand, anchor= 'nw', padx= 2)
    # yes, LEFT to end up on right. see:
    # https://www.tutorialspoint.com/python/tk_pack.htm

class rowframe_loose(rowframe):
  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
 
  def packw(self, tkw, **kwargs):
    kwargs['expand']= True
    rowframe.packw(self, tkw, **kwargs)

#--------------------------------------------------------------------
class gridframe(packframe):
  def __init__(self, parent, wid= 0, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.row= 0;  self.col= 0;  self.wid= wid
    self.choosebg('bggrid')
 
  def packw(self, tkw, **kwargs):
    colspan= 1;  sticky= 'w'
    if 'colspan' in kwargs:  colspan= kwargs['colspan']
    if 'sticky' in kwargs:   sticky= kwargs['sticky']
    tkw.grid(column=self.col, row= self.row, sticky=sticky, columnspan=colspan)
    tkw.grid_configure(padx= 2, pady= 2)
    self.col= self.col+ colspan
    if self.wid and self.col>= self.wid:  self.newrow();

  def newrow(self):
    if self.col== 0:  return
    self.row= self.row+1;  self.col= 0

#---------------------------------------------------------------------------------
# really wanted this in gw.py, but Python would not cooperate...
class Ftextpane(rowframe):
  def __init__(self, parent, height= None, width=None, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.height= height;  self.width= width

  def populate(self):   gw.pop_textpane(self, height= self.height, width= self.width)
  def get(self):        return gw.get_textpane(self)
  def set(self, text):  gw.set_textpane(self, text)

#---------------------------------------------------------------------------------
class Fmessagesection(rowframe):
  def __init__(self, parent, title= '', text= '', *args, **kwargs):
    self.title= title;  self.text= text
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    gw.pop_messagesection(self, title= self.title, text= self.text, clipput= clipput)


#=======================================================================================
class tabmain(packframe):
  def __init__(self, parent, *args, **kwargs):
    self.titleprefix= '';  self.curtab= self.launchtab= None;  self.buttons= {}
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    #print('tabmain', self)
    self.tabrow=   self.subframetight(rowframe)
    self.scroller= self.vscrollsubframe()
    self.buttons= {};  self.pop_tabs();  self.pop_curtab()

  def pop_tab(self, name, viewclass, launch= False, **sfkwargs):
    tab= {'name': name, 'viewclass': viewclass, 'sfkwargs': sfkwargs}
    command= lambda tab= tab: self.switchto(tab)
    b= self.tabrow.button(name, background= 'lightgray', command= command)
    self.buttons[name]= b
    if launch and not self.curtab:  self.curtab= self.launchtab= tab

  def switchto(self, tab):
    #print('switchto:', str(tab['viewclass']))
    prevtab= self.curtab
    if prevtab:
      prevbutton= self.buttons[prevtab['name']]
      prevbutton.config(background= 'lightgray')
    self.curtab= tab;  self.pop_curtab()

  def switchtolaunch(self):  self.switchto(self.launchtab)

  def pop_curtab(self):
    tab= self.curtab
    if not tab:  return
    title= self.titleprefix+ tab['name'];  self.title(title)
    self.buttons[tab['name']].config(background= 'white')
    viewclass= tab['viewclass'];  scroller= self.scroller;   sfkwargs= tab['sfkwargs']
    scroller.pop_addinterior(viewclass, **sfkwargs)
    scroller.interior.tabmain= self

#=============================================================================
def inprogress_popup(text, command):
  domain(Finprogress, packfirst= True, text= text, command= command)

class Finprogress(packframe):
  def __init__(self, parent, text, command, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.text= text;  self.command= command
  def populate(self):
    command= self.command;  text= self.text;   self.title(text);
    self.label('In progress:');  self.label(text, font=('TxTextFont', 17))
    update_main(idleonly= False);  print('executing command...')
    command()
    print('...executed command');  self.root.destroy()

