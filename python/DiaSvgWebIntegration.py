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


### 
### Status of development: phase2, let it work properly and ensure code
### is cleaned and not recurrent. Uses all the important property like
### VariableFormat, BuildStatement and correctly brace error and
### possible error with try/except .
###

###
### for phase3, adding implementation of
### ActionSelection, StatementAct , BuildStatementAttr, finishing  
### StatementAct property. Since All templated excepted the 
### StrFileHeader, which come in Header part, middle part where 
### rendering start and end_render seems to be imperative and 
### called by the API, almost all template are to be loaded,
### feeded and buffered prior to be written . Uses of property
### BuildStatementAttr should cover addition of A-Template, and 
### B-parsing it uppon calling the getter. StatementAct
### setter is somewhat definied and do have a process-description
### to configure templating and parsing inside a middle part or
### full-part of a template, ActionSelection being a Top-property
### of StatementAct , BuildStatementAttr, once thoses are
### configured, it should start the process to be ready to store
### with self.RenderToBuffer or claim an error. Somewhat like
### function TemplateToValueParser except it manage a bit more 
### how variable are passed to BuildStatement. View on function
### somes are using BuildStatement with constructed String 
### coming from middle part. ActionSelection should get rid 
### of this itself. As example , _getPointString is used when a
### variable of signature of point is passed in function, thus
### make draw_polyline, draw_polygon, fill_polygon, requiring to
### uses BuildStatement with _getPointString( points ) to make
### the template complete, while making BuildStatementAttr tell
### to Background information from class to let pass a variables
### 'points' to pass in a _getPointString( points ), when
### StatementAct does have a filter in points in sub-member
### having 'attribute x an y', have no choice to tell to
### ActionSelection to do provide a Getter of
### _getPointString( points ) for template like
### self.DrawPolyLineTemplate . _getBezPoint is the another
### example and thus have similar candidate to make even simpler
### call of  function like draw_bezier, fill_bezier. And so forth,
### _colorSpace is mandatory associated to color, _stroke_style
### have it's own implementation but dump a string.... Such
### element while phase3 will end in a good conclusion to
### seemlesly convert dia diagram into svg, Phase3 will have to
### transform rest of caveat in reading an SVG into a clean
### an simple property before going in XML with phase4.
### 
### 


import sys, io, re, os, os.path ,string, base64, gzip, math 
from io import StringIO
from StringIO import StringIO
from lxml import etree



class SvgLxmlEngine( object ):

  DictMeta = { 'line':
         {'attr':{'x1':'%.3f',
            'y1':'%.3f',
            'x2':'%.3f',
            'y2':'%.3f',
            'style':"stroke:%s;stroke-width:%.3f" } } }

  ### Notice: will be integrated in phase 4, after using
  ### BuildStatementAttr in all of function. 

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
<svg width="{:.3f}cm" height="{:.3f}cm" viewBox="{:.3f} {:.3f} {:.3f} {:.3f}"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cc="http://creativecommons.org/ns#"
 xmlns:svg="http://www.w3.org/2000/svg"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">\n"""

  ErrorLineTemplate         = """<!-- {:s} -->\n"""
  DrawLineTemplate          = """\t<line x1="{:.3f}" y1="{:.3f}" x2="{:.3f}" y2="{:.3f}" style="stroke:{:s};stroke-width:{:.3f};{:s}" />\n"""
  DrawPolyLineTemplate      = """\t<polyline style="fill:none;stroke:{:s};stroke-width:{:.3f};{:s}" points="{:s}" />\n"""
  DrawPolygonTemplate       = """\t<polygon style="fill:none;stroke:{:s};stroke-width:{:.3f};{:s}" {:s} points="{}" />\n"""
  DrawFillPolygonTemplate   = """\t<polygon style="fill:{:s};stroke:none;stroke-width:{:.3f};" points="{:s}" />\n"""
  DrawRectangleTemplate     = """\t<rect x="{:.3f}" y="{:.3f}" width="{:.3f}" height="{:.3f}" style="fill:none;stroke:{:s};stroke-width:{:.3f};{:s}" />\n"""
  DrawFillRectTemplate      = """\t<rect x="{:.3f}" y="{:.3f}" width="{:.3f}" height="{:.3f}" style="fill:{:s};stroke:none;stroke-width:0;{:s}"/>\n"""
  DrawArcNofillTemplate     = """\t<path style="stroke:{:s};fill:none;stroke-width:{:.3f};{:s}" d="{:s}" />\n"""
  DrawArcFillTemplate       = """\t<path style="fill:{:s};stroke:none;" d="{:s}" />\n"""
  DrawArcPointTemplate      = """M {:.3f},{:.3f} A {:.3f},{:.3f} 0 {:d},{:d} {:.3f},{:.3f}"""
  DrawEllipseTemplate       = """\t<ellipse cx="{:.3f}" cy="{:.3f}" rx="{:.3f}" ry="{:.3f}" style="fill:none;stroke:{:s};stroke-width:{:.3f};{:s}" />"""
  DrawFillEllipseTemplate   = """<ellipse cx="{:.3f}" cy="{:.3f}" rx="{:.3f}" ry="{:.3f}" style="fill:{:s};stroke:none;" />\n"""
  DrawBezierTemplate        = """\t<path style="fill:none;stroke:{:s};stroke-width:{:.3f};{:s}" d="{:s}" />\n"""
  BezierMoveToTemplate      = """M {:.3f},{:.3f} """
  BezierLineToTemplate      = """L {:.3f},{:.3f} """
  BezierCurveToTemplate     = """C {:.3f},{:.3f} {:.3f},{:.3f} {:.3f},{:.3f} """
  Point2DTemplate           = """{:3.f},{:3.f}"""
                              # Red   Green Blue
  Color3SpaceTemplate       = "#{:02X}{:02X}{:02X}"
                              # Red  Green  Blue  Opacity, but actually unused. 
  Color4SpaceTemplate       = "#{:02X}{:02X}{:02X}{:02X}"
  DrawFillBezierTemplate    = """\t<path  style="fill:{:s};stroke:none;stroke-width:{:.3f};" d="{:s}" />\n"""
  DrawStringTemplate        = """\t<text x="{:.3f}" y="{:.3f}" text-anchor="{:s}" font-size="{:.2f}" style="fill:{:s};font-family:{:s};font-style:{:s};font-weight:{:d};" >{:s}</text>\n"""
  DrawImageTemplate         = """\t<image x="{:.3f}" y="{:.3f}" width="{:.3f}" height="{:.3f}" xlink:href="{:s}"/>\n"""
  
  FontWeightT           = (400, 200, 300, 500, 600, 700, 800, 900)
  FontStyleT            = ('normal', 'italic', 'oblique')
  TextAlign             = ('start', 'middle', 'end')

  ColorSpace = {'HSV' : ['hue','saturation','value'] ,
                'RGB' : ['red','green','blue'] }
  
  StrokeType = {
  'dasharray':{ 'name':'stroke-dasharray',
          1:'{:s}:{:.2f},{:.2f};',
          2:'{:s}:{:.2f},{:.2f},{:.2f},{:.2f};',
          3:'{:s}:{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f};',
          4:'{:s}:{:.2f},{:.2f};'},
  'linejoin':{ 'name':'stroke-linejoin' ,
         0:'',
         1:'{:s}:round;',
         2:'{:s}:bevel;'},
  'linecaps':{ 'name':'stroke-linecap',
         0:'{:s}:butt;',
         1:'{:s}:round;',
         2:'{:s}:square;' } }
  
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

  ### This is an array or list of value to be pushed inside the StrokeDash
  ### Configuration, used by property VariableFormat
  ListVariableFormat = []

  ### This is an array or list of value to be pushed inside the Template
  ### value, used by property BuildStatement
  ListBuildStatement = []
  BuildStatementValue = None 
  
  ActionSelectionList=[ 'Template', 'Variable', 'Error', 'Buffer', 'Commit' ]

  ### 
  ### This is the section of attribute and reference used 
  ### by property ActionSelection and BuildStatement.
  ###
  ### role ActionSelection  
  ###  -> to set the Statement-index to one of 
  ###    -> template to receive and emit template in a process
  ###       of BuildStatement. 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  setTemplate       = ActionSelectionList[0]
  setBuffer         = ActionSelectionList[1]
  setError          = ActionSelectionList[2]
  setBuffer         = ActionSelectionList[3]
  setCommit         = ActionSelectionList[4]

  ### 
  ### This is the section of attribute and reference used 
  ### by property BuildStatement.
  ###
  ### role inside BuildStatement
  ###  BuildStatement only append value to a List , upon
  ### uses of getter it return  the whole array or list 
  ### to print request usually a formating services of 
  ### String. 
  ### 
  ### Using BuildStatementAttr to specify a How the 
  ### Property should return the list, setting 
  ### BuildStatementAttr to setValue which is the 
  ### first action the Property does if the There is
  ### no value to BuildStatementAttr. setValue mean
  ### BuildStatement property should return list of
  ### value.
  ### Choosing setFormat will change the return method
  ### to gather the type of every value. Usefull in 
  ### string-template (not Template class) to throw
  ### additional information if a TypeError occur during
  ### parsing.
  ### 
  StatementFormatList=[ 'value', 'format' ]
  setValue          = StatementFormatList[0]
  setFormat         = StatementFormatList[1]


  """
  Utility of Statement

  Statement[Template], does hold the template aka the xml-tag line,
  polyline, polygon, rect...

  Statement[Variable], hold the stacked variable
  list to be parsed with Template rules. 

  Statement[Error] ,  hold  cumuled  error  during
  information parsing in Buffer. This information is
  pushed  inside  the  file  in
  form : <!-- ERROR INFORMATION ---> .
  This information is  writed  before  the

  Statement[Result]  and should  not interfere with
  Buffer  itself. 

  Statement[Buffer], hold the  work in  progress.
  It hold the Element, oming with actual structure
  to allow 1-element  to hold partial structure,
  A Statement[Template] can grow due to it's section d=""
  used by element like path, polyline and polygon,
  own attribute like 'point', and 'd' . 

  Statement[Commit], process to write-down of Error
  in comment and the arbritrary Xml elements with
  appropriate attribute. 
  """  
  Statement ={
  'Template':str(),
  'Result':str(),
  'Error':[],
  'Buffer':str() }

  
  Buffer              = None 
  PStatementAct       = None
  PStatementDictIndex = None
  PBuildStatement     = None
  
  def __init__ (self):
    self.FileHandler  = None
    self.line_width   = 0.1
    self.line_caps    = 0
    self.line_join    = 0
    self.line_style   = 0
    self.dash_length  = 0
    self.Buffer       = StringIO()

  def SetBuffer( self, value ):
    self.Buffer.write( value )

  def GetBuffer( self ):
    return self.Buffer.getvalue()

  def ResetBuffer( self ):
    self.Buffer.reset()

  RenderToBuffer = property( GetBuffer, SetBuffer, ResetBuffer )
  

  ###
  ### Function for property ActionSelection
  ###
  ### Notice: will be integrated in phase3 only.
  """
 Note1:
 Set inside ActionSelection from New statement
 a present ActionSelection
 in property of ActionSelection
   - Used first time:
   setStatementAct does :
   - set PStatementAct to possibly [ 'Template', 'Result',
   'Error', 'Buffer', 'Commit' ] choice by using either
   setTemplate, setBuffer, setError, setBuffer, setCommit
 - Used second time:
   setStatementAct does :
  - set self.PStatementDictIndex a tuple type value for
   - assigning attribute for a reserved Dictionnary-Index
     for storing inside Statement[PStatementAct] for it's
     value collected in second call.
         
 Note2:
   Start using it 3rd, 4th 5th time to address
   information to corresponding
   Statement[PStatementAct].
   Ex example :
   Incase Statement[PStatementAct=Template],
   PStatementDictIndex=DrawPolyLineTemplate
   where the definition of
   DrawPolyLineTemplate remain in an unfinished
   Xml-tag having first, it's tag-name, it's
   style definied, it remain not-complete because
   serialisation of dia object did not call the
   rasterized point-to-point information.
   calling this property with another sample 
   of template like a 2-floats template '%.2f,%.2f;'
   to fill all the point in a table of points
   from original draw_polyline , will require to 
   call this property 3rd, 4th, n-th time until we
   have all the point . """
 
  def setStatementAct( self, value ):
    ### Description, See Note1:
    ### Notice: will be integrated in phase3 only.
    
    if self.PStatementAct == None :
      self.PStatementAct = value
    else:
      if self.PStatementDictIndex == None:
        ### From already existing Statement
        if value in self.has_attr( value ):
          if value == self.setTemplate :
            ### In case statement Template was already assign
            ### adding inside PStatementDictIndex the information
            self.PStatementDictIndex  = ( '__setitem__' , self.PStatementAct )
            ### Set the Dict-Statement for a new Template:
            getattr( self.PStatementDictIndex, self.PStatementDictIndex[0])( self.PStatementDictIndex[1] , value )
          if value == self.setBuffer :
            pass
            ### To add for phase3.
        else:
          pass
          ### To add for phase3.
          ### Description, See Note2:

  def getStatementAct( self ):
    ### To add for phase3.
    pass

  def resetStatementAct( self ):
    ### To add for phase3.
    pass

  ### Notice: will be integrated in phase3 only.
  StatementAct = property( getStatementAct, setStatementAct, resetStatementAct ) 

  ###
  ### End-of property ActionSelection
  ###


  ###
  ### Function for property BuildStatementAttr
  ###
  ### Notice: will be integrated in phase3 only. 
  ###
  def SetBSAttr( self, value ):
    if value in self.StatementFormatList:
      self.BuildStatementValue = value

  def GetBSAttr( self ):
    return self.BuildStatementValue

  def ResetBsAttr( self ):
    self.BuildStatementValue = None

  BuildStatementAttr = property( GetBSAttr, SetBSAttr, ResetBsAttr )
  
  ###
  ### Function for property BuildStatement
  ###
  ### BuildStatement, replace property
  ### VariableFormat, hence to have similar 
  ### design, but return information inside 
  ### dict Statement[Buffer]. 
  ###
  ### Scheduled for phase2 
  ### 
  def SetBuildStatement( self, value ):
    """This Property-setter support following calling convention:\n\tBuildStatement = Variable\n\tBuildStatement = Variabl1, Variable2\n\tBuildStatement = [ Variable1, Variable2 ]\n"""
    ### First step, validating and forcing BuildStatementAttr
    ### to be set to setValue only if there is no already
    ### attribued value.
    if self.BuildStatementAttr == None:
      self.BuildStatementAttr = self.setValue 
    if type(value) in [ type(tuple()), type(list()) ] :
      if len( value ) > 0:
        for item in value:
          self.ListBuildStatement.append( item )
    else:
      self.ListBuildStatement.append( value )

  def GetBuildStatement( self ):
    ReturnList=[]
    if self.BuildStatementAttr == self.setValue:
      ReturnList=self.ListBuildStatement
    elif self.BuildStatementAttr == self.setFormat:
      for item in self.ListBuildStatement:
        ReturnList.append(type(item))
    return ReturnList 

  def DelBuildStatement( self ):
    """This is a Property-reset or reseting of the ListVariableFormat list."""
    self.ListBuildStatement=list()

  """VariableFormat Property used inside _stroke_style function. Explainned early in function SetStrokeDash to work by appending variable inside a list() and does use printf-defined type-format know by %d, %s, %[0-9]+f used inside most template, before merge to SvgLxmlEngine"""
  BuildStatement = property( GetBuildStatement, SetBuildStatement, DelBuildStatement )
  
  ###
  ### End-of property BuildStatement
  ###

  ### 
  ### Function for property VariableFormat
  ### Used in stroke action, not element action.
  ### Reason : conflict by using a template ,
  ### and feeding variable when 1 of the variable
  ### is a _stroke_style which call itself 
  ### VariableFormat too to extend afinity of your
  ### element. 
  ###
  
  def SetVariableFormat( self, value ):
    """This Property-setter support following calling convention:\n\tVariableFormat = Variable\n\tVariableFormat = Variable1, Variable2\n\tself.VariableFormat = [ Variabl1, Variable2 ]\n"""
    if type(value) == type(tuple()) or type(value) == type(list()) :
      if len( value ) > 0:
        for item in value:
          self.ListVariableFormat.append( item )
    else:
      self.ListVariableFormat.append( value )

  def GetVariableFormat( self ):
    return self.ListVariableFormat

  def DelVariableFormat( self ):
    """This is a Property-reset or reseting of the ListVariableFormat list."""
    self.ListVariableFormat=list()

  """VariableFormat Property used inside _stroke_style and _colorSpace function. Since both are not called altogether, they are working during uses of BuilStatement property. Explainned early in function SetStrokeDash to work by appending variable inside a list() and does use printf-defined type-format know by %d, %s, %[0-9]+f used inside most template, before merge to SvgLxmlEngine"""
  VariableFormat = property( GetVariableFormat, SetVariableFormat, DelVariableFormat )

  

  ### 
  ### End-of property VariableFormat
  ### 

  def FormatStroke( self, StrDashType, StyleId  ):
    StrReturnFormat=str() 
    if len(self.VariableFormat) > 0:
      StrReturnFormat=self.StrokeType[StrDashType][StyleId].format( self.StrokeType[StrDashType]['name'] ).format( self.VariableFormat ) 
    else:
      StrReturnFormat=self.StrokeType[StrDashType][StyleId].format( self.StrokeType[StrDashType]['name'] )
    return StrReturnFormat

  def FormatTemplate( self ):
    StrReturnFormat=str()
    if len(self.VariableFormat) > 0:
      StrReturnFormat=self.TemplateString.format( self.VariableFormat ) 
    else:
      StrReturnFormat=self.TemplateString 
    return StrReturnFormat

  def TemplateToValueParser( self, StrTemplate ):
    ### A function calling TemplateToValueParser, should'nt require to clean
    ### self.BuildStatementAttr since this function does it at the end. 
    self.BuildStatementAttr = self.setValue
    try:
      self.RenderToBuffer = StrTemplate.format( self.BuildStatement )
    except TypeError:
      self.BuildStatementAttr = self.setFormat
      print "Template:{},\nValue by type:{}\n".format( self.BuildStatement )
    ### It's important to free the BuildStatement property, to let the new statement
    ### of vector adding new information without leaving anciens one and let the
    ### String.format(...) throwing a TypeError . 
    del self.BuildStatement


  def WriteBuffer( self, StringText ):
    self.Buffer += StringText

  def FileWriter( self ):
    """Using the StringIO.getvalue() from RenderToBuffer property it
    retreive all the String buffered from all elements called during
    a render action from dia."""
    self.FileHandler.write( self.RenderToBuffer )
    self.FileHandler.close()
  
  def _open(self, filename) :
    self.FileHandler = open(filename, "w")

  def begin_render (self, data, filename) :
    self._open( filename )
    r = data.extents
    xofs = - r[0]
    yofs = - r[1]
    #del self.BuildStatement
    ### Because the begin_render is the first instruction it should'nt require to
    ### clean the BuildStatement. 
    self.BuildStatement = r.right - r.left, r.bottom - r.top, r[0], r[1], r[2], r[3]
    self.RenderToBuffer = self.StrFileHeader.format( self.BuildStatement )
    #self.f.write("<!-- %s -->\n" % (str(data.extents)))
    #self.f.write("<!-- %s -->\n" % (data.active_layer.name))

  def end_render(self) :
    self.RenderToBuffer = self.TagElementSvgClosure
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
    del self.BuildStatement
    self.BuildStatement = start.x, start.y, end.x, end.y, self._colorSpace(color), self.line_width, self._stroke_style()
    self.TemplateToValueParser( self.DrawLineTemplate )    
    
  def _getPointString( self, point ):
    StrPointList=str()
    for pt in points :
      StrPointList += self.Point2DTemplate.format(pt.x, pt.y)
    return StrPointList

  def draw_polyline (self, points, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self.BuildStatement = self._colorSpace(color), self.line_width, self._stroke_style(), _getPointString( points ) 
    self.TemplateToValueParser( self.DrawPolyLineTemplate )
    
  def draw_polygon (self, points, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self.BuildStatement = self._colorSpace(color), self.line_width, self._stroke_style(), _getPointString( points ) 
    self.TemplateToValueParser( self.DrawPolygonTemplate )

  def fill_polygon (self, points, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self.BuildStatement = self._colorSpace(color), self.line_width , _getPointString( points ) 
    self.TemplateToValueParser( self.DrawFillPolygonTemplate )

  def draw_rect (self, rect, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser . 
    self.BuildStatement = rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top,
    self._colorSpace(color), self.line_width, self._stroke_style()
    self.TemplateToValueParser( self.DrawRectangleTemplate )

  def fill_rect (self, rect, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser . 
    self.BuildStatement = rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, self._colorSpace(color)
    self.TemplateToValueParser( self.DrawFillRectTemplate )

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
    #del self.BuildStatement , see message inside TemplateToValueParser . 
    self.BuildStatement = sx, sy, rx, ry, largearc, sweep, ex, ey 
    StrArcPoint=self.DrawArcPointTemplate.format( self.BuildStatement )

    if not fill :
      ### Since self.BuildStatement was used to parse self.DrawArcPointTemplate, which is
      ### only the end-element, it require to reset the BuildStatement to add information
      ### about color, line, stroke, and at last All the Point, forming the arc.
      ### Other condition to use the Reset, DrawArcPointTemplate was parsed using the
      ### BuildStatement
      del self.BuildStatement
      self.BuildStatement = self._colorSpace(color), self.line_width, self._stroke_style() , StrArcPoint
      self.TemplateToValueParser( self.DrawArcNofillTemplate )
    else :
      ### Since self.BuildStatement was used to parse self.DrawArcPointTemplate, which is
      ### only the end-element, it require to reset the BuildStatement to add information
      ### about color of the arc and the Point forming the Arc. 
      ### Other condition to use the Reset, DrawArcPointTemplate was parsed using the
      ### BuildStatement
      del self.BuildStatement
      self.BuildStatement = self._colorSpace(color), StrArcPoint 
      self.TemplateToValueParser( self.DrawArcFillTemplate )

  def draw_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color)

  def fill_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color, 1)

  def draw_ellipse (self, center, width, height, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self.BuildStatement = center.x, center.y, width / 2, height / 2, self._colorSpace(color), self.line_width, self._stroke_style()
    self.TemplateToValueParser( self.DrawEllipseTemplate )
      

  def fill_ellipse (self, center, width, height, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self.BuildStatement = center.x, center.y, width / 2, height / 2, self._colorSpace(color)
    self.TemplateToValueParser( self.DrawFillEllipseTemplate )

  def draw_bezier (self, bezpoints, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    ### Unless it don't hold all the elements even part of complex one,
    ### it's useless to prepare a self.BuildStatement for color, line
    ### because the loop of bezpoints will throw an TypeError after first
    ### parsed elements and final template will hodl about nothing except
    ### over-crowed informations. 
    self.BuildStatement = self._colorSpace(color), self.line_width,
    self._stroke_style(), self._getBezPoint( bezpoints  ) 
    self.TemplateToValueParser( self.DrawBezierTemplate )
    ### No more need to close an element, all template were adjusted to hold second level of
    ### parsing, making them complete instead of concatenating part
    #self.WriteBuffer( self.TagElementClosure )

  def fill_bezier (self, bezpoints, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self.BuildStatement = self._colorSpace(color), self.line_width , self._getBezPoint( bezpoints  )
    self.TemplateToValueParser( self.DrawFillBezierTemplate )
    #self.WriteBuffer( self.TagElementClosure )

  # avoid writing XML special characters (ampersand must be first to not break the rest)
  def TextSubst( self, StrVar ):
    for CharIndex in self.CharExceptionRepl :
      StrVar=StrVar.replace( CharIndex[0],CharIndex[1] )
    return StrVar 

  def draw_string (self, text, pos, alignment, color) :
    if len(text) < 1 :
      return # shouldn'this be done at the higher level 
    talign = self.TextAlign [alignment]
    fstyle = self.FontStyleT [self.font.style & 0x03]
    fweight = self.FontWeightT [(self.font.style  >> 4)  & 0x7]
    #del self.BuildStatement, see message inside TemplateToValueParser .
    ### This BuildStatement hold 9 variables to parse within this Template.
    self.BuildStatement = pos.x, pos.y, self._colorSpace(color), talign, self.font_size,
    self.font.family, fstyle,  fweight, self.TextSubst( text )
    self.TemplateToValueParser( self.DrawStringTemplate )

  def draw_image (self, point, width, height, image) :
    #FIXME : do something better than absolute pathes ?
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self.BuildStatement = point.x, point.y, width, height, image.uri 
    self.TemplateToValueParser( self.DrawImageTemplate )

    # Helpers, not in the DiaRenderer interface

  def _getBezPoint(self, bezpoints):
    StrBezier=str() 
    ### Since there is no information on bezpoints, they may have more than one
    ### entity and should worry about BuildStatement every-loop . 
    for bp in bezpoints :
      if bp.type == 0 : # BEZ_MOVE_TO
        ### *Part1
        ### This is also mean BuildStatement hold:
        ### BuildStatement -> [ self._rgb(color), self.line_width, self._stroke_style() ] AND
        ### formatted self.BezierMoveToTemplate 
        self.BuildStatement = bp.p1.x, bp.p1.y 
        StrBezier+=self.BezierMoveToTemplate.format( self.BuildStatement )
      elif bp.type == 1 : # BEZ_LINE_TO
        ### Same as *Part1, except it's self.BezierLineToTemplate that is the end
        ### element introduced inside BuildStatement 
        self.BuildStatement = bp.p1.x, bp.p1.y
        StrBezier+=self.BezierLineToTemplate.format( self.BuildStatement )
      elif bp.type == 2 : # BEZ_CURVE_TO
        ### Same as *Part1, except it's self.BezierLineToTemplate that is the end
        ### element introduced inside BuildStatement 
        self.BuildStatement = bp.p1.x, bp.p1.y, bp.p2.x, bp.p2.y, bp.p3.x, bp.p3.y
        StrBezier+=self.BezierCurveToTemplate.format( self.BuildStatement )
      else :
        dia.message(2, "Invalid BezPoint type (%d)" * bp.type)
      ### Since a loop-resence does enforce the fact BuildStatement will receive
      ### new argument for each elements of bp it mean at the end StrBezier will
      ### hold n-amount of a mix of BezierMoveToTemplate/BezierLineToTemplate/
      ### BezierCurveToTemplate, and even leaving the loop, self.BuildStatement
      ### should be empty, be cause This section fill information for the last
      ### elements, it will be inserted (StrBezier) at the end.
      del self.BuildStatement
    return StrBezier 

  def _testColorSpaceName( color, StrName ):
    IsColorInAttr=True
    ColorAttr=self.ColorSpace[StrName] 
    for ColorName in ColorAttr:
      if IsColorInAttr is True:
        if not hasattr( color , ColorName ):
          IsColorInAttr=False
    return IsColorInAttr

  def _colorSpace(self, color) :
    # given a dia color convert to svg color string
    # a tweak in case creator of Dia opt for opacity
    # in diagram...
    StrTemplateChoice=self.Color3SpaceTemplate
    ### Testing if atribute 'red' or 'hue' exist...
    if self._testColorSpaceName( color, 'RGB' ):
      ### This mean color are coded in RGB style. 
      self.VariableFormat = int(255 * color.red),int(color.green * 255),int(color.blue * 255)
    if self._testColorSpaceName( color, 'HSV' ):
      ### This mean color are coded in HSV style. 
      self.VariableFormat = int(255 * color.hue),int(color.saturation * 255),int(color.value * 255)
    if hasattr( color , 'opacity'):
      ### make an addition, adding color in 4 spaces instead, and adding opacity at the end....
      ### How beautiful are Property, simplify the branching statement like to not
      ### develop and opacity branch-condition if the attribute does or does not exist.
      StrTemplateChoice=self.Color4SpaceTemplate
      self.VariableFormat = int(color.opacity * 255)

    rgb = StrTemplateChoice.format( self.VariableFormat )
    # And it's extremely inportant to reset the VariableFormat since
    # it's commonly use to build a stroke and do introduce
    # color... This mean, and SHOULD HAVE to execute _colorSpace(...) before
    # it's template to parse...
    del self.VariableFormat   
    return rgb

  def _line_space_style( self ):
    StrTypeLine="{}"
    # return the current line style as svg string
    dashlen =self.dash_length
    # dashlen/style interpretation like the DiaGdkRenderer
    dotlen = dashlen * 0.1
    if self.line_style == 0 : # LINESTYLE_SOLID
      StrTypeLine = ""
    elif self.line_style == 1 : # DASHED
      self.VariableFormat = dashlen, dashlen
    elif self.line_style == 2 : # DASH_DOT,
      gaplen = (dashlen - dotlen) / 2.0
      self.VariableFormat = dashlen, gaplen, dotlen, gaplen
    elif self.line_style == 3 : # DASH_DOT_DOT,
      gaplen = (dashlen - dotlen) / 3.0
      self.VariableFormat = dashlen, gaplen, dotlen, gaplen, dotlen, gaplen
    elif self.line_style == 4 : # DOTTED
      self.VariableFormat = dotlen, dotlen

    if self.line_style != 0:
      StrTypeLine=StrTypeLine.format( self.FormatStroke( 'dasharray', style ) )
          
    del self.VariableFormat
    return StrTypeLine

  def _line_join_style( self ):
    StrLineJoin="{}"
    if self.line_join == 0 : # MITER
      StrLineJoin=""
    else:
      StrLineJoin=StrLineJoin.format( self.FormatStroke( 'linejoin', self.line_join ) )
    return StrLineJoin 

  def _line_caps_style( self ):
    StrLineCaps="{}"
    if self.line_caps == 0 : # BUTT
      StrLineCaps=""
    else:
      StrLineCaps=StrLineCaps.format( self.FormatStroke( 'linecap', self.line_caps ) )
    return StrLineCaps

  def _stroke_style(self) :
    self._line_space_style() 
    StrStrokeStyle = "{0}{1}{2}"
    StrStrokeStyle=StrStrokeStyle.format( self._line_space_style() , self._line_join_style(), self._line_caps_style() )

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



IntPidDia=GetIntPid( r'(?u)^[a-zA-Z\-]*dia[a-zA-Z\-]*' )
try:
  if IntPidDia != None:
    print "dia application found: PID: {}".format( IntPidDia )
  else:
    raise NameError
    try:
      import dia
    except ImportError:
      print "This message happen because dia or pydia is not\nloaded from dia python console.\n\nTemporary   \"deferring\"   registration  of  module. \nThis python  module  is  loaded  out  of  a  dia\nenvironment; And  can be  loaded  from dia-python\nconsole  or  loading explicitly  pydia  modules\nfrom  « plug-ins / python » dia  path.\n\nSvgLxmlEngine class can be used alone."
    dia.register_export ("SVG plain (uses of style attribute)", "svg", SvgWebRenderer())
    dia.register_export ("SVG Base64 (uses of style attribute)", "svg.base64", SvgBase64Codec())
    dia.register_export ("SVG compressed (uses of style attribute)", "svgz", SvgCompression())
except NameError :
  print """Module like SvgWebRenderer, SvgBase64Codec, SvgCompression, are dia or\npydia dependent and can not be loaded alone or out of dia c-API interface.\nSvgLxmlEngine class can be used alone.\n\n"""
  


