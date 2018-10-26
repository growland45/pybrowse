from tkinter import *
from lib import gw, myio, mylaunch
import traceback

default_fonts= {
  'entryfont':         ('Courier New', 12),
  'tinyfont':          ('TkTextFont', 10),
  'controlbuttonfont': ('TkTextFont', 11),
  'regularfont':       ('TkTextFont', 12)
}

def compute_default_fonts(screen_width):
  global default_fonts, fontw
  w= (screen_width*1.0)/ 1024.0
  if w> 1.16:  w=1.16
  default_fonts= {
    'entryfont':         ('Courier New', int(w*12)),
    'tinyfont':          ('TkTextFont',  int(w*10)),
    'controlbuttonfont': ('TkTextFont',  int(w*11)),
    'regularfont':       ('TkTextFont',  int(w*12))
  }
  fontw= w

def choosecolor(palette, name, alt= None):
  if not palette:  return alt # may be color name
  if name in palette:  return palette[name]
  if not alt:  return None
  if alt in palette:  return palette[alt]
  return alt # may be color name

class myframe(Frame):
  palette= None

  def __init__(self, parent, palette= None, fonts= None, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent= parent;  self.root = root= parent.root
    #[doesn't work]self.report_callback_exception = self.report_callback_exception
        
    self.fonts= default_fonts
    if hasattr(parent, 'fonts'):  self.fonts= parent.fonts
    if fonts:  self.fonts= fonts

    if not self.palette:  self.palette= palette
    if not self.palette and hasattr(self.parent, 'palette'):
      self.palette= self.parent.palette
    if not self.palette:  self.palette= self.root.palette

    self.choosebg('bgcolframe')
    self.isfocusset= False;  self.scrollframe= None

  # rigmarole to get exceptions and stack trace on screen when needed:
  def on_exception(self):  myio.log_exception()

  def cmdwrapped(self, cmd):
    try:   cmd()
    except Exception as e:  self.on_exception()
  def wrapcmd(self, cmd):
    wrapped= lambda cmd= cmd: self.cmdwrapped(cmd);  return wrapped

  def pcolor(self, name, alt= None):
    return choosecolor(self.palette, name, alt)

  def choosebg(self, key):
    bgcolor= self.pcolor(key)
    if not bgcolor:  return
    self.bgcolor= bgcolor
    self.configure(bg= bgcolor)

  def tktarget(self):  return self   # the "parent" to feed tkinter when creating sub-widgets
  def populate(self):  return        # OVERRIDE
  def title(self, title):   self.root.title(title)

  def maybe_setfocus(self, tkw):
    if self.isfocusset:  return
    tkw.focus_set();  self.isfocusset= True

  def addwidget(self, widgetclass, pkwargs= {}, **wkwargs):
    if not 'font' in wkwargs or wkwargs['font']== None:
      wkwargs['font']= self.fonts['regularfont']
    return self.addwidget_noaddfont(widgetclass, pkwargs= pkwargs, **wkwargs)

  def addwidget_noaddfont(self, widgetclass, pkwargs= {}, **wkwargs):
    tkw= widgetclass(self, **wkwargs)
    if not 'expand' in pkwargs:  pkwargs['expand']= False
    if not 'fill'   in pkwargs:  pkwargs['fill']=   X
    self.tktarget().packw(tkw, **pkwargs)
    return tkw

  def label(self, text, white= False, font= None, var= None, **wkwargs):
    return self.addwidget(gw.Wlabel, text= text, textvariable= var,
                                     font= font, white= white, **wkwargs)
  def wlabel(self, text, font= None, **wkwargs):
    white= not 'foreground' in wkwargs
    return self.label(text, white= white, font=font, **wkwargs)
  def varlabel(self, var, font= None, **wkwargs):
    return self.label(None, False, var= var, font=font, **wkwargs)

  def message(self, text, width= 700,  **wkwargs): # width is pixels, despite documentation
    fg= self.pcolor('fgedit', 'white'); bg= self.pcolor('bgedit', 'black')
    return self.addwidget(Message, text= text, width= width, fg= fg, bg= bg, **wkwargs)

  def button(self, text, command, **wkwargs):
    return self.addwidget(Button, text= text, command= self.wrapcmd(command), **wkwargs)
  def compact_button(self, text, command, **wkwargs):
    return self.addwidget(gw.Wcompactbutton, text= text,
                          command= self.wrapcmd(command), **wkwargs)
  def control_button(self, text, command):
    return self.addwidget(gw.Wcontrolbutton, text= text, command= self.wrapcmd(command))
  def okbutton(self, text= 'OK', command= None):
    if command== None:  command=self.on_ok
    tkw= self.button(text, command)
    self.root.bind("<Return>", command)
    return tkw

  def checkbox(self, text, val= 0):
    return self.addwidget(gw.Wcheckbox, text= text, val= val)

  def entry(self, width=30, text=''):
    tkw= self.addwidget_noaddfont(gw.Wentry, width= width, root= self.root)
    tkw.set(text)
    self.maybe_setfocus(tkw)
    return tkw

  def packw(self, tkw, **pkwargs):  pass # override

  def subframe(self, sfclass, pkwargs= {}, **sfkwargs):
    try:
      sf= sfclass(self, **sfkwargs)
      self.packw(sf, **pkwargs);
      sf.populate();   
    except Exception as e:  self.on_exception();  return None
    return sf

  def subframetight(self, sfclass, pkwargs= {}, **sfkwargs):
    #print('subframetight CFG: ', str(cfg)); print('subframetight KWARGS: ', str(kwargs))
    try:
      sf= sfclass(self, **sfkwargs)
      sf.populate();   self.packw(sf, fill=NONE, expand=False, **pkwargs)
    except Exception as e:  self.on_exception();  return None
    return sf

  def update_modalparent(self):
     if not hasattr(self, 'modalparent'):  return
     modalparent= self.modalparent
     #print('update_modalparent', str(modalparent), modalparent.__class__.__name__)
     if not modalparent: return
     modalparent.refresh()

  def refresh(self):
    wlist= list(self.children.values())
    for w in wlist:  w.destroy()
    self.scrollframe= None
    self.populate()

  def vscrollsubframe(self, viewclass= None, **sfkwargs):
    # only one allowed...
    if self.scrollframe:  raise ValueError('Redundant vscrollsubframe()')

    scr= vscrollframe(self);  scr.viewclass= viewclass;  scr.sfkwargs= sfkwargs
    scr.populate();  self.packw(scr); # would rather populate before show.
    self.scrollframe= scr
    return scr.tktarget()

  def exit(self):
    if hasattr(self, 'root'):  self.root.destroy();  return
    self.destroy()

  def TODO(self, sfile):
    command= lambda sfile= sfile:  TODOlaunch(sfile)
    self.button(text='TODO '+ sfile, command= command, background='#f00')

def TODOlaunch(sfile):  mylaunch.spawn(['pluma', sfile])

#--------------------------------------------------------------------

class vscrollframe(myframe):
  def __init__(self, parent, *args, **kwargs):
    self.sfkwargs= kwargs
    super().__init__(parent, *args, **kwargs)

  def populate(self):
    self.interior= None
    # https://gist.github.com/EugeneBakin/76c8f9bcec5b390e45df
    # create a canvas object and a vertical scrollbar for scrolling it
    vscrollbar = Scrollbar(self, orient= VERTICAL)
    vscrollbar.pack(fill= Y, side= RIGHT, expand= FALSE)
    canvas = Canvas(self, bd=0, highlightthickness= 0, yscrollcommand= vscrollbar.set)
    canvas.root= self
    canvas.pack(side= LEFT, fill= BOTH, expand= TRUE)
    canvas.create_rectangle(0, 0, 3000, 30000, fill= self.pcolor('bgcolframe', '#555555'))
    vscrollbar.config(command= canvas.yview)

    # reset the view
    canvas.xview_moveto(0);   canvas.yview_moveto(0)
    self.canvas= canvas

    self.pop_addinterior(**self.sfkwargs)

  def pop_addinterior(self, viewclass= None, **sfkwargs):
    if not viewclass:  viewclass= self.viewclass
    else:              self.viewclass= viewclass
    if not viewclass:  return None

    # so can replace existing...
    if self.interior:  self.interior.destroy()

    # create a frame inside the canvas which will be scrolled with it
    canvas= self.canvas
    self.interior = interior = self.viewclass(canvas, **sfkwargs)
    interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(event):
      # update the scrollbars to match the size of the inner frame
      size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
      canvas.config(scrollregion="0 0 %s %s" % size)
      if interior.winfo_reqwidth() != canvas.winfo_width():
        # update the canvas's width to fit the inner frame
        canvas.config(width=interior.winfo_reqwidth())
    interior.bind('<Configure>', _configure_interior)

    def _configure_canvas(event):
      if interior.winfo_reqwidth() != canvas.winfo_width():
        # update the inner frame's width to fill the canvas
        canvas.itemconfigure(interior_id, width=canvas.winfo_width())
    canvas.bind('<Configure>', _configure_canvas)

    interior.scroller= self
    interior.populate();
    return interior

  def refresh(self):
    print('vscrollframe refresh')
    self.pop_addinterior()

  # the "parent" to feed tkinter when creating sub-widgets
  def tktarget(self):
    if self.interior:  return self.interior
    return self


