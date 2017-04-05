#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- file : DiaSvgWebIntegration.py -*- 

#  PyDia SVG Renderer
#  Copyright (c) 2003, 2004 Hans Breuer <hans@breuer.org>
#
#  Web-Adaptation to integrate all common attribute into style attribute.
#  (Maxiste Deams) 2017. maxistedeams@gmail.com 
#
#  - Creating a Buffer version of PyDia SVG Renderer to make possible to
#  add a base64 codec available for web development. Adding images like
#  <img src="data:image/svg;base64,... Base64 String-Codec..."></img>
#  by pasting file written in SvgBase64Codec. My jsfiddle example is
#  using an online base64 png file being replaced by another file. And
#  thus can be replaced by SVG file.
#
#  Some work-around on integrating attribute id. for the moment a generated
#  id will by provided, and will requiert to user to select accross a
#  gui-interface a Do provide id by svg-symbols and/or provide a base-integer
#  startup-id.
#  jsfiddle example: https://jsfiddle.net/maxiste_deams/38mk78z6/ 
# 
#  - Integrating lxml as Template replacement. And Dictionnary to attribute
#  dia-attribute value to Xml-parsed template value.
#
#  A full blown SVG(Z) renderer. As of this writing less bugs in the output
#  than the Dia SVG renderer written in C

#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


### Notice, dia module can be loaded only if dia-gnome or dia is open and
### you are loading this module from python-console from dia. Otherwise.
### SHALL keep this ScanPid, managing presence of an import and WILL
### import dia which are crucial to class SvgWebRenderer, SvgBase64Codec,
### SvgCompression. Only SvgLxmlEngine can be loaded without presence
### of dia, dia-gnome .


import sys, os, os.path, string, base64, gzip, math 
import re, io
from io import StringIO
from StringIO import StringIO
from lxml import etree



def GetIntPid( diaRegularExpression ):
  """Default Use:
             return the pid of dia, dia-gnome or containning
             dia, accross /proc/PID, where PID is a number
             and containning a file called cmdline which is
             the crude command-line from dia launch.
      Default regular expression:
        r'(?u)^[a-zA-Z\-]*dia[a-zA-Z\-]*'
  """
  IntPid=None
  Areg=re.compile( diaRegularExpression )
  pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
  for pid in pids:
    try:
      AHandler=open(os.path.join('/proc', pid, 'cmdline'), 'rb')
      Astr=StringIO( buf=AHandler.read() )
      AHandler.close()
      if Areg.search( Astr.read() ) != None:
        IntPid=pid
    except IOError:
      continue
  return IntPid


if GetIntPid( r'(?u)^[a-zA-Z\-]*dia[a-zA-Z\-]*' ) != None:
  import dia


class SvgLxmlEngine( object ):

  DictMeta = { 'line':
               {'attr':{'x1':'%.3f',
                        'y1':'%.3f',
                        'x2':'%.3f',
                        'y2':'%.3f',
                        'style':"stroke:%s;stroke-width:%.3f" } } }

  ### All template of polyline, polygon, rect, ellipse should end
  ### here.
  XmlNode = {}
  ### All information for a generation of one of the polyline,
  ### polygon, rect, ellipse, Xml node require to be store here
  NodeCreation = {'name':None ,'value':None}
  NodeAttr     = None

  ### Property Level2, touching the key, to make String 'name'
  ### accessing to content NodeCreation[name] being reflected
  ### by AttrNode -> 'name', so we can set
  ### self.AttrNode = 'name'
  ### and accessing to NodeCreation[self.AttrNode] or
  ### using NodeCreation['name'] will give the same answer.

  def SetAttrDic( self, attrname ):
    self.NodeAttr = attrname

  def GetAttrDic( self ):
    return self.NodeAttr

  AttrNode = property( GetAttrDic, SetAttrDic, None )


  ### Property Level 1 , touching the NodeCreation[name]
  def SetNode( self, attrname ):
    self.NodeCreation['name']=attrname

  def GetNode( self ):
    return self.NodeCreation['name'] 

  Node = property( GetNode, SetNode, None )
  
  def SetLineTpl( self ):
    self.Line = 'line'
    self.AttrNode = 'name'
    self.Node = self.Line
    self.AttrNode = 'value'
    self.Node = etree.Element( self.Line )
    for AttrName in self.DictMeta[self.Line].keys():
      self.line.set( AttrName , self.DictMeta[self.Line][AttrName]  )


  def __init__( self ):
    self.SetLineTpl()

  def GetSvgLineString( self ):
    return etree.tostring(self.line)

class SvgWebRenderer( SvgLxmlEngine ) :

  StrFileHeader   = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created by DiaSvgWebIntegration for web edition -->
<svg width="%.3fcm" height="%.3fcm" viewBox="%.3f %.3f %.3f %.3f"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">"""

  DrawLineTemplate      = """<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" style="stroke:%s;stroke-width:%.3f" %s/>\n"""
  DrawPolyLineTemplate  = """<polyline style="fill:none;stroke:%s;stroke-width:%.3f" %s points=\""""
  DrawPolygonTemplate   = """<polygon style="fill:none;stroke:%s;stroke-width:%.3f;" %s points=\""""
  FillPolygonTemplate   = """<polygon style="fill:%s;stroke:none;stroke-width:%.3f;" points=\""""
  DrawRectangleTemplate = """<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" style="fill:none;stroke:%s;stroke-width:%.3f;" %s/>\n"""
  DrawFillRect          = """<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" style="fill:%s;stroke:none;stroke-width:0"/>\n"""
  DrawArcNofill         = """<path style="stroke:%s;fill:none;stroke-width:%.3f;" %s"""
  DrawArcFill           = """<path style="stroke:none;fill:%s;\""""
  DrawArcPoint          = """ d ="M %.3f,%.3f A %.3f,%.3f 0 %d,%d %.3f,%.3f """
  DrawEllipse           = """<ellipse cx="%.3f" cy="%.3f" rx="%.3f" ry="%.3f" style="fill:none;stroke:%s;stroke-width:%.3f;" %s/>"""
  DrawFillEllipse       = """<ellipse cx="%.3f" cy="%.3f" rx="%.3f" ry="%.3f" style="fill:%s;stroke:none;" />"""
  DrawBezier            = """<path style="stroke:%s;fill:none;stroke-width:%.3f;" %s d=\""""
  BezierMoveTo          = """M %.3f,%.3f """
  BezierLineTo          = """L %.3f,%.3f """
  BezierCurveTo         = """C %.3f,%.3f %.3f,%.3f %.3f,%.3f """
  DrawFillBezier        = """<path stroke="none" fill="%s" stroke-width="%.3f" d=\""""
  DrawString            = '<text x="%.3f" y="%.3f" text-anchor="%s" font-size="%.2f" style="fill:%s;font-family:%s;font-style:%s;font-weight:%d;" >\n'

  FontWeightT           = (400, 200, 300, 500, 600, 700, 800, 900)
  FontStyleT            = ('normal', 'italic', 'oblique')

  CharExceptionRepl     = [ ('&', '&amp;'),('<', '&lt;'),('>', '&gt;'),('"', '&quot;'),("'", '&apos;') ,
      ('∀','&forall;'),('∂','&part;'),('Æ','&AElig;'),('Ð','&ETH;'),('Ñ','&Ntilde;'),('×','&times;'),('Þ','&THORN;'),
      ('ß','&szlig;'),('å','&aring;'),('æ','&aelig;'),('ç','&ccedil;'),('ð','&eth;'),('÷','&divide;'),('ø','&oslash;'),
      ('∃','&exist;'),('∅','&empty;'),('∇','&nabla;'),('∈','&isin;'),('∉','&notin;'),('∋','&ni;'),('∏','&prod;'),
      ('∑','&sum;'),('Α','&Alpha;'),('Β','&Beta;'),('Γ','&Gamma;'),('Δ','&Delta;'),('Ε','&Epsilon;'),('Ζ','&Zeta;'),
      ('©','&copy;'),('®','&reg;'),('€','&euro;'),('™','&trade;'),('←','&larr;'),('↑','&uarr;'),('→','&rarr;'),
      ('↓','&darr;'),('♠','&spades;'),('♣','&clubs;'),('♥','&hearts;'),('♦','&diams;'),('₠','&#8352;'),('₡','&#8353;'),
      ('₢','&#8354;'),('₣','&#8355;'),('₤','&#8356;'),('₥','&#8357;'),('₦','&#8358;'),('₧','&#8359;'),('₨','&#8360;'),
      ('₩','&#8361;'),('₪','&#8362;'),('₫','&#8363;'),('€','&#8364;'),('₭','&#8365;'),('₮','&#8366;'),('₯','&#8367;'),
      ('₰','&#8368;'),('₱','&#8369;'),('₲','&#8370;'),('₳','&#8371;'),('₴','&#8372;'),('₵','&#8373;'),('₶','&#8374;'),
      ('₷','&#8375;'),('₸','&#8376;'),('₹','&#8377;'),('☀','&#9728;'),('☁','&#9729;'),('☂','&#9730;'),('☃','&#9731;'),
      ('☄','&#9732;'),('★','&#9733;'),('☆','&#9734;'),('☇','&#9735;'),('☈','&#9736;'),('☉','&#9737;'),('☊','&#9738;'),
      ('☋','&#9739;'),('☌','&#9740;'),('☍','&#9741;'),('☎','&#9742;'),('☏','&#9743;'),('☐','&#9744;'),('☑','&#9745;'),
      ('☒','&#9746;'),('☓','&#9747;'),('☔','&#9748;'),('☕','&#9749;'),('☖','&#9750;'),('☗','&#9751;'),('☘','&#9752;'),
      ('☙','&#9753;'),('☚','&#9754;'),('☛','&#9755;'),('☜','&#9756;'),('☝','&#9757;'),('☞','&#9758;'),('☟','&#9759;'),
      ('☠','&#9760;'),('☡','&#9761;'),('☢','&#9762;'),('☣','&#9763;'),('☤','&#9764;'),('☥','&#9765;'),('☦','&#9766;'),
      ('☧','&#9767;'),('☨','&#9768;'),('☩','&#9769;'),('☪','&#9770;'),('☫','&#9771;'),('☬','&#9772;'),('☭','&#9773;'),
      ('☮','&#9774;'),('☯','&#9775;'),('☰','&#9776;'),('☱','&#9777;'),('☲','&#9778;'),('☳','&#9779;'),('☴','&#9780;'),
      ('☵','&#9781;'),('☶','&#9782;'),('☷','&#9783;'),('☸','&#9784;'),('☹','&#9785;'),('☺','&#9786;'),('☻','&#9787;'),
      ('☼','&#9788;'),('☽','&#9789;'),('☾','&#9790;'),('☿','&#9791;'),('♀','&#9792;'),('♁','&#9793;'),('♂','&#9794;'),
      ('♃','&#9795;'),('♄','&#9796;'),('♅','&#9797;'),('♆','&#9798;'),('♇','&#9799;'),('♈','&#9800;'),('♉','&#9801;'),
      ('♊','&#9802;'),('♋','&#9803;'),('♌','&#9804;'),('♍','&#9805;'),('♎','&#9806;'),('♏','&#9807;'),('♐','&#9808;'),
      ('♑','&#9809;'),('♒','&#9810;'),('♓','&#9811;'),('♔','&#9812;'),('♕','&#9813;'),('♖','&#9814;'),('♗','&#9815;'),
      ('♘','&#9816;'),('♙','&#9817;'),('♚','&#9818;'),('♛','&#9819;'),('♜','&#9820;'),('♝','&#9821;'),('♞','&#9822;'),
      ('♟','&#9823;'),('♠','&#9824;'),('♡','&#9825;'),('♢','&#9826;'),('♣','&#9827;'),('♤','&#9828;'),('♥','&#9829;'),
      ('♦','&#9830;'),('♧','&#9831;'),('♨','&#9832;'),('♩','&#9833;'),('♪','&#9834;'),('♫','&#9835;'),('♬','&#9836;'),
      ('♭','&#9837;'),('♮','&#9838;'),('♯','&#9839;'),('♰','&#9840;'),('♱','&#9841;'),('♲','&#9842;'),('♳','&#9843;'),
      ('♴','&#9844;'),('♵','&#9845;'),('♶','&#9846;'),('♷','&#9847;'),('♸','&#9848;'),('♹','&#9849;'),('♺','&#9850;'),
      ('♻','&#9851;'),('♼','&#9852;'),('♽','&#9853;'),('♾','&#9854;'),('♿','&#9855;'),('⚀','&#9856;'),('⚁','&#9857;'),
      ('⚂','&#9858;'),('⚃','&#9859;'),('⚄','&#9860;'),('⚅','&#9861;'),('⚆','&#9862;'),('⚇','&#9863;'),('⚈','&#9864;'),
      ('⚉','&#9865;'),('⚊','&#9866;'),('⚋','&#9867;'),('⚌','&#9868;'),('⚍','&#9869;'),('⚎','&#9870;'),('⚏','&#9871;'),
      ('⚐','&#9872;'),('⚑','&#9873;'),('⚒','&#9874;'),('⚓','&#9875;'),('⚔','&#9876;'),('⚕','&#9877;'),('⚖','&#9878;'),
      ('⚗','&#9879;'),('⚘','&#9880;'),('⚙','&#9881;'),('⚚','&#9882;'),('⚛','&#9883;'),('⚜','&#9884;'),('⚝','&#9885;'),
      ('⚞','&#9886;'),('⚟','&#9887;'),('⚠','&#9888;'),('⚡','&#9889;'),('⚢','&#9890;'),('⚣','&#9891;'),('⚤','&#9892;'),
      ('⚥','&#9893;'),('⚦','&#9894;'),('⚧','&#9895;'),('⚨','&#9896;'),('⚩','&#9897;'),('⚪','&#9898;'),('⚫','&#9899;'),
      ('⚬','&#9900;'),('⚭','&#9901;'),('⚮','&#9902;'),('⚯','&#9903;'),('⚰','&#9904;'),('⚱','&#9905;'),('⚲','&#9906;'),
      ('⚳','&#9907;'),('⚴','&#9908;'),('⚵','&#9909;'),('⚶','&#9910;'),('⚷','&#9911;'),('⚸','&#9912;'),('⚹','&#9913;'),
      ('⚺','&#9914;'),('⚻','&#9915;'),('⚼','&#9916;'),('⚽','&#9917;'),('⚾','&#9918;'),('⚿','&#9919;'),('⛀','&#9920;'),
      ('⛁','&#9921;'),('⛂','&#9922;'),('⛃','&#9923;'),('⛄','&#9924;'),('⛅','&#9925;'),('⛆','&#9926;'),('⛇','&#9927;'),
      ('⛈','&#9928;'),('⛉','&#9929;'),('⛊','&#9930;'),('⛋','&#9931;'),('⛌','&#9932;'),('⛍','&#9933;'),('⛎','&#9934;'),
      ('⛏','&#9935;'),('⛐','&#9936;'),('⛑','&#9937;'),('⛒','&#9938;'),('⛓','&#9939;'),('⛔','&#9940;'),('⛕','&#9941;'),
      ('⛖','&#9942;'),('⛗','&#9943;'),('⛘','&#9944;'),('⛙','&#9945;'),('⛚','&#9946;'),('⛛','&#9947;'),('⛜','&#9948;'),
      ('⛝','&#9949;'),('⛞','&#9950;'),('⛟','&#9951;'),('⛠','&#9952;'),('⛡','&#9953;'),('⛢','&#9954;'),('⛣','&#9955;'),
      ('⛤','&#9956;'),('⛥','&#9957;'),('⛦','&#9958;'),('⛧','&#9959;'),('⛨','&#9960;'),('⛩','&#9961;'),('⛪','&#9962;'),
      ('⛫','&#9963;'),('⛬','&#9964;'),('⛭','&#9965;'),('⛮','&#9966;'),('⛯','&#9967;'),('⛰','&#9968;'),('⛱','&#9969;'),
      ('⛲','&#9970;'),('⛳','&#9971;'),('⛴','&#9972;'),('⛵','&#9973;'),('⛶','&#9974;'),('⛷','&#9975;'),('⛸','&#9976;'),
      ('⛹','&#9977;'),('⛺','&#9978;'),('⛻','&#9979;'),('⛼','&#9980;'),('⛽','&#9981;'),('⛾','&#9982;'),('⛿','&#9983;')]
      

  
  TagElementClosure     = """"/>\n"""
  TagElementTextClosure = """</text>\n"""
  TagElementSvgClosure  = """</svg>"""
  
  def __init__ (self):
    self.FileHandler  = None
    self.line_width   = 0.1
    self.line_caps    = 0
    self.line_join    = 0
    self.line_style   = 0
    self.dash_length  = 0
    self.Buffer       = str()

  def WriteBuffer( self, StringText ):
    self.Buffer += StringText

  def FileWriter( self ):
    self.FileHandler.write( self.Buffer )
    self.FileHandler.close()
    
  def _open(self, filename) :
    self.FileHandler = open(filename, "w")

  def begin_render (self, data, filename) :
    self._open (filename)
    r = data.extents
    xofs = - r[0]
    yofs = - r[1]
    self.WriteBuffer( self.StrFileHeader % (r.right - r.left, r.bottom - r.top, r[0], r[1], r[2], r[3]))
    #self.f.write("<!-- %s -->\n" % (str(data.extents)))
    #self.f.write("<!-- %s -->\n" % (data.active_layer.name))

  def end_render (self) :
    self.WriteBuffer( self.TagElementSvgClosure )
    self.FileWriter( )
    

  def set_linewidth (self, width) :
    if width < 0.001 : # zero line width is invisble ?
      self.line_width = 0.001
    else :
      self.line_width = width

  def set_linecaps (self, mode) :
    self.line_caps = mode

  def set_linejoin (self, mode) :
    self.line_join = mode

  def set_linestyle (self, style) :
    self.line_style = style

  def set_dashlength (self, length) :
    self.dash_length = length

  def set_fillstyle (self, style) :
    # currently only 'solid' so not used anywhere else
    self.fill_style = style

  def set_font (self, font, size) :
    self.font = font
    self.font_size = size

  def draw_line (self, start, end, color) :
    self.WriteBuffer( self.DrawLineTemplate % ( start.x, start.y, end.x, end.y, self._rgb(color), self.line_width, self._stroke_style()) )

  def draw_polyline (self, points, color) :
    self.WriteBuffer(self.DrawPolyLineTemplate % (self._rgb(color), self.line_width, self._stroke_style()))
    for pt in points :
      self.WriteBuffer('%.3f,%.3f ' % (pt.x, pt.y))
    self.WriteBuffer( self.TagElementClosure )

  def draw_polygon (self, points, color) :
    self.WriteBuffer( self.DrawPolygonTemplate % (self._rgb(color), self.line_width, self._stroke_style()))
    for pt in points :
      self.WriteBuffer('%.3f,%.3f ' % (pt.x, pt.y))
    self.WriteBuffer( self.TagElementClosure )

  def fill_polygon (self, points, color) :
    self.WriteBuffer( self.FillPolygonTemplate % (self._rgb(color), self.line_width))
    for pt in points :
      self.WriteBuffer('%.3f,%.3f ' % (pt.x, pt.y))
    self.WriteBuffer(self.TagElementClosure)

  def draw_rect (self, rect, color) :
    self.WriteBuffer( self.DrawRectangleTemplate % ( rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top,
                                                     self._rgb(color), self.line_width, self._stroke_style()))

  def fill_rect (self, rect, color) :
    self.WriteBuffer( self.DrawFillRect % ( rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, self._rgb(color)))

  def _arc (self, center, width, height, angle1, angle2, color, fill=None) :
    # not in the renderer interface
          
    mPi180 = math.pi / 180.0
    rx = width / 2.0
    ry = height / 2.0
    sx = center.x + rx * math.cos(mPi180 * angle1)
    sy = center.y - ry * math.sin(mPi180 * angle1)
    ex = center.x + rx * math.cos(mPi180 * angle2)
    ey = center.y - ry * math.sin(mPi180 * angle2)
    largearc = (angle2 - angle1 >= 180)
    sweep = 0 # always draw in negative direction
    if not fill :
      self.WriteBuffer( self.DrawArcNofill % (self._rgb(color), self.line_width, self._stroke_style()))
    else :
      self.WriteBuffer( self.DrawArcFill % (self._rgb(color)))
    # moveto sx,sy arc rx,ry x-axis-rotation large-arc-flag,sweep-flag ex,ey 
    self.WriteBuffer( self.DrawArcPoint % (sx, sy, rx, ry, largearc, sweep, ex, ey))
    self.WriteBuffer( self.TagElementClosure )

  def draw_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color)

  def fill_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color, 1)

  def draw_ellipse (self, center, width, height, color) :
    self.WriteBuffer( self.DrawEllipse % (center.x, center.y, width / 2, height / 2, self._rgb(color), self.line_width, self._stroke_style()))

  def fill_ellipse (self, center, width, height, color) :
    self.WriteBuffer(self.DrawFillEllipse % (center.x, center.y, width / 2, height / 2, self._rgb(color)))

  def draw_bezier (self, bezpoints, color) :
    self.WriteBuffer( self.DrawBezier % (self._rgb(color), self.line_width, self._stroke_style()))
    for bp in bezpoints :
      if bp.type == 0 : # BEZ_MOVE_TO
        self.WriteBuffer( self.BezierMoveTo % (bp.p1.x, bp.p1.y))
      elif bp.type == 1 : # BEZ_LINE_TO
        self.WriteBuffer( self.BezierLineTo % (bp.p1.x, bp.p1.y))
      elif bp.type == 2 : # BEZ_CURVE_TO
        self.WriteBuffer( self.BezierCurveTo % (bp.p1.x, bp.p1.y, bp.p2.x, bp.p2.y, bp.p3.x, bp.p3.y))
      else :
        dia.message(2, "Invalid BezPoint type (%d)" * bp.type)
      self.WriteBuffer( self.TagElementClosure )

  def fill_bezier (self, bezpoints, color) :
    self.WriteBuffer( self.DrawFillBezier % (self._rgb(color), self.line_width))
    for bp in bezpoints :
      if bp.type == 0 : # BEZ_MOVE_TO
        self.WriteBuffer( self.BezierMoveTo % (bp.p1.x, bp.p1.y))
      elif bp.type == 1 : # BEZ_LINE_TO
        self.WriteBuffer( self.BezierLineTo % (bp.p1.x, bp.p1.y))
      elif bp.type == 2 : # BEZ_CURVE_TO
        self.WriteBuffer( self.BezierCurveTo % (bp.p1.x, bp.p1.y, bp.p2.x, bp.p2.y, bp.p3.x, bp.p3.y))
      else :
        dia.message(2, "Invalid BezPoint type (%d)" * bp.type)
    self.WriteBuffer( self.TagElementClosure )

  # avoid writing XML special characters (ampersand must be first to not break the rest)
  def TextSubst( self, StrVar ):
    for CharIndex in self.CharExceptionRepl :
      StrVar=StrVar.replace( CharIndex[0],CharIndex[1] )
    return StrVar 

  def draw_string (self, text, pos, alignment, color) :
    if len(text) < 1 :
      return # shouldn'this be done at the higher level 
    talign = ('start', 'middle', 'end') [alignment]
    fstyle = self.FontStyleT [self.font.style & 0x03]
    fweight = self.FontWeightT [(self.font.style  >> 4)  & 0x7]
    self.WriteBuffer( self.DrawString % (pos.x, pos.y, self._rgb(color), talign, self.font_size, self.font.family, fstyle,  fweight))
    
    self.WriteBuffer( self.TextSubst( text ) )
    self.WriteBuffer( self.TagElementTextClosure )

  def draw_image (self, point, width, height, image) :
          #FIXME : do something better than absolute pathes ?
          self.WriteBuffer('<image x="%.3f" y="%.3f"  width="%.3f" height="%.3f" xlink:href="%s"/>\n' \
                  % (point.x, point.y, width, height, image.uri))
  # Helpers, not in the DiaRenderer interface

  def _rgb(self, color) :
          # given a dia color convert to svg color string
          rgb = "#%02X%02X%02X" % (int(255 * color.red), int(color.green * 255), int(color.blue * 255))
          return rgb

  def _stroke_style(self) :
    # return the current line style as svg string
    dashlen =self.dash_length
    # dashlen/style interpretation like the DiaGdkRenderer
    dotlen = dashlen * 0.1
    caps = self.line_caps
    join = self.line_join
    style = self.line_style
    st = ""
    if style == 0 : # LINESTYLE_SOLID
      pass
    elif style == 1 : # DASHED
      st = 'stroke-dasharray:%.2f,%.2f;' % (dashlen, dashlen)
    elif style == 2 : # DASH_DOT,
      gaplen = (dashlen - dotlen) / 2.0
      st = 'stroke-dasharray:%.2f,%.2f,%.2f,%.2f;' % (dashlen, gaplen, dotlen, gaplen)
    elif style == 3 : # DASH_DOT_DOT,
      gaplen = (dashlen - dotlen) / 3.0
      st = 'stroke-dasharray:%.2f,%.2f,%.2f,%.2f,%.2f,%.2f;' % (dashlen, gaplen, dotlen, gaplen, dotlen, gaplen)
    elif style == 4 : # DOTTED
      st = 'stroke-dasharray:%.2f,%.2f;' % (dotlen, dotlen)

    if join == 0 : # MITER
      pass # st = st + ' stroke-linejoin="bevel"'
    elif join == 1 : # ROUND
      st = st + ' stroke-linejoin:round;'
    elif join == 2 : # BEVEL
      st = st + ' stroke-linejoin:bevel;'

    if caps == 0 : # BUTT
      pass # default stroke-linecap="butt"
    elif caps == 1 : # ROUND
      st = st + ' stroke-linecap:round;'
    elif caps == 2 : # PROJECTING
      st = st + ' stroke-linecap:square;' # is this the same ?
    st='style="%s"' % ( st )
    return st

class SvgCompression(SvgWebRenderer) :

  def FileWriter( self ):
    self.FileHandler.write( self.Buffer )

  def _open(self, filename) :
    # There is some (here) not wanted behaviour in gzip.open/GzipFile :
    # the filename with path is not only used to adress the file but also
    # completely stored in the file itself. Correct it here.
    path, name = os.path.split(filename)
    os.chdir(path)
    self.FileHandler = gzip.open (name, "wb")

class SvgBase64Codec( SvgWebRenderer ):

  StrHeader = "data:image/svg;base64,{}"

  def FileWriter( self ):
    self.FileHandler.write( self.StrHeader.format( base64.b64encode( self.Buffer ) ) )

  def _open(self, filename) :
    path, name = os.path.split(filename)
    os.chdir(path)
    gzip.open (name, "w")

# dia-python keeps a reference to the renderer class and uses it on demand

try:
  dia.register_export ("SVG plain (uses of style attribute)", "svg", SvgWebRenderer())
  dia.register_export ("SVG Base64 (uses of style attribute)", "svg.base64", SvgBase64Codec())
  dia.register_export ("SVG compressed (uses of style attribute)", "svgz", SvgCompression())
except NameError:
  print "This message happen because dia or pydia is not\nloaded from your console.\n\nTemporary   \"deferring\"   registration  of  module. \nThis python  module  is  loaded  out  of  a  dia\nenvironment; And  can be  loaded  from dia-python\nconsole  or  loading explicitly  pydia  modules\nfrom  « plug-ins / python » dia  path.\n\nSvgLxmlEngine class can be used alone."
  


