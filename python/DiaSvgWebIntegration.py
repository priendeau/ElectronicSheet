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
import wx

class PropertyWarning( Warning ):
  StrMsg = 'Warning on property, {}'

  def __init__( self, value ):
    Warning.__init__( self, self.StrMsg.format( value ) )

class EmptyTextString( Warning ):
  StrMsg = 'Warning raised for Empty Text-String found inside Text-Vector :[{}]'

  def __init__( self, value ):
    Warning.__init__( self, self.StrMsg.format( value ) )


class FunctionDecorator( object ):

  @staticmethod
  def FunctionPrint( ListIndex ):
    StrPrint=str()
    item=None 
    if len( ListIndex ) <= 1:
      StrPrint="{} ".format( item )
    else:
      for item in ListIndex:
        StrPrint += " {}-> ".format( item )
    return StrPrint
  
  @staticmethod
  def NameFunc( ListIndex ):
    """
    This Decorator Will:
      perform an Display output of the actual function entry.
          
    """
    def decorator( func ):
        def inner( *args ):
          ListIndex.append( func.func_name )
          print "Entry in Function:{}".format( FunctionDecorator.FunctionPrint( ListIndex ) )
          func( *args )
          ListIndex.pop() 
        return inner
    return decorator

  


class SvgLxmlEngine( FunctionDecorator ):

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
      self.Line.set( AttrName , self.DictMeta[self.Line][AttrName]  )


  def __init__( self ):
    self.SetLineTpl()

  def GetSvgLineString( self ):
    return etree.tostring(self.Line)

class SvgWebRenderer( SvgLxmlEngine ) :

  ### 
  ### This List is used to add the function after a function with decorator NameFunc
  ### is used. Once the function end, the decorator remove the last function by poping
  ### it-out. The display consist of a cast of a list() in string and do show if more
  ### than one function is used and have not exited ( function using another function).
  ### 
  ListFunctionReference = list()  
  
  StrFileHeader   = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created by DiaSvgWebIntegration for web edition -->
<svg width="{:0.3f}cm" height="{:0.3f}cm" viewBox="{:0.3f} {:0.3f} {:0.3f} {:0.3f}"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cc="http://creativecommons.org/ns#"
 xmlns:svg="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">\n"""

  ErrorLineTemplate         = """<!-- {} -->\n"""
                            #parameter cx, cy, rx, ry, stroke, stroke-width ; ? 
  DrawEllipseTemplate       = """<ellipse cx="{:0.3f}" cy="{:0.3f}" rx="{:0.3f}" ry="{:0.3f}" style="fill:none;stroke:{};stroke-width:{:0.3f};{}" />\n"""
  DrawLineTemplate          = """<line x1="{:0.3f}" y1="{:0.3f}" x2="{:0.3f}" y2="{:0.3f}" style="stroke:{};stroke-width:{:0.3f};" />\n"""
  DrawPolyLineTemplate      = """<polyline style="fill:none;stroke:{};stroke-width:{:0.3f};{}" points="{:s}" />\n"""
  DrawPolygonTemplate       = """<polygon style="fill:none;stroke:{};stroke-width:{:0.3f};{}" points="{:s}" />\n"""
  DrawRectangleTemplate     = """<rect x="{:0.3f}" y="{:0.3f}" width="{:0.3f}" height="{:0.3f}" style="fill:none;stroke:{};stroke-width:{:0.3f};{}" />\n"""
  DrawArcNofillTemplate     = """<path style="stroke:{};fill:none;stroke-width:{:0.3f};" d="{:s}" />\n"""
  DrawArcPointTemplate      = """M {:0.3f},{:0.3f} A {:0.3f},{:0.3f} 0 {:0.0f},{:0.0f} {:0.3f},{:0.3f}"""
  DrawBezierTemplate        = """<path style="fill:none;stroke:{};stroke-width:{:0.3f};{}" d="{:s}" />\n"""
                            #parameter: cx, cy, rx, ry, fill:color, 
  BezierMoveToTemplate      = """M {:0.3f},{:0.3f} """
  BezierLineToTemplate      = """L {:0.3f},{:0.3f} """
  BezierCurveToTemplate     = """C {:0.3f},{:0.3f} {:0.3f},{:0.3f} {:0.3f},{:0.3f} """

  DrawFillPolygonTemplate   = """<polygon style="fill:{};stroke:none;stroke-width:{:0.3f};{}" points="{:s}" />\n"""
  DrawFillRectTemplate      = """<rect x="{:0.3f}" y="{:0.3f}" width="{:0.3f}" height="{:0.3f}" style="fill:{};stroke:none;stroke-width:{:0.3f};{}"/>\n"""
  DrawArcFillTemplate       = """<path style="fill:{};stroke:none;" d="{:s}" />\n"""
  DrawFillEllipseTemplate   = """<ellipse cx="{:0.3f}" cy="{:0.3f}" rx="{:0.3f}" ry="{:0.3f}" style="fill:{};stroke:{};stroke-width:{:0.3f};{}" />\n"""
  Point2DTemplate           = """{:0.3f},{:0.3f} """
                              # Red   Green Blue
  Color3SpaceTemplate       = "#{:02X}{:02X}{:02X}"
                              # Red  Green  Blue  Opacity, but actually unused. 
  Color4SpaceTemplate       = "#{:02X}{:02X}{:02X}{:02X}"
  DrawFillBezierTemplate    = """<path  style="fill:{};stroke:none;stroke-width:{:0.3f};" d="{:s}" />\n"""
  DrawStringTemplate        = """<text x="{:0.3f}" y="{:0.3f}" text-anchor="{:s}" font-size="{:0.2f}" style="fill:{};font-family:{:s};font-style:{:s};font-weight:{:0.0f};" >{:s}</text>\n"""
  DrawImageTemplate         = """<image x="{:0.3f}" y="{:0.3f}" width="{:0.3f}" height="{:0.3f}" xlink:href="{:s}"/>\n"""
  
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
         0:'{:s}:none;',
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

  ### Common to all Property where setter is able to filter more than
  ### one value at the time :
  PropertyTypeCheck=[ type(tuple()), type(list()) ]

  
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
  StatementFormatList=[ 'value', 'format', 'storeFloat', 'storeInt' ]
  setValue          = StatementFormatList[0]
  setFormat         = StatementFormatList[1]
  setStoreFloat     = StatementFormatList[2]
  setStoreInt       = StatementFormatList[3]

  ### Used by property StorageActionAttr .
  BuildStatementAction = None 

  ### used by property StorageReadAttr .
  BuildStatementReader = None 

  # used in function FormatTemplate and also 
  # reffered in FormatTemplate to be associated with property VariableFormat
  TemplateString = None 

  ### 
  ### This is the section of attribute and reference used 
  ### by property FormatHandler.
  ###
  ### role inside FormatHandler
  ###
  ### set value to "append" with setAppend will:
  ### - make ValueFormatHandler appending information to 
  ### self.(AttrClassName) 
  ### 
  ### set value to "initialize" with setInitialize will:
  ### - make ValueFormatHandler Initializing the content
  ### of self.(AttrClassName) to parsed information.
  ### 
  ### 

  ValueFactoryRef   = None 
  FHPropertyValue   = None 
  FormatHandlerList=[ "append","initialize" ]
  setAppend         = FormatHandlerList[0]
  setInitialize     = FormatHandlerList[1]


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

  def WindowsInterface( self ):
    app = wx.App(False)
    frame = wx.Frame(None, wx.ID_ANY, "Options for SVG (style attribute)")
    frame.Show(True)
    app.MainLoop()
  
  def __init__ ( self ):
    super( SvgLxmlEngine, self ).__init__(  )
    self.FileHandler      = None
    self.line_width       = 0.1
    self.line_caps        = 0
    self.line_join        = 0
    self.line_style       = 0
    self.dash_length      = 0
    self.Buffer           = StringIO()
    self.Text             = None 
    self.BezPointsList    = None 
    self.PointStringValue = None
    self.ColorSpaceObject = None
    self.FormatStrokeValue= None
    self.LineSpaceStyle   = None
    self.LineJoinValue    = None
    self.LineCapsValue    = None
    self.StrokeStyleValue = None
    self.ShowOptionWindows= False

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
        if value in hasattr(self, value ):
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
  ### Function for property BuildStatementAttr,
  ### and daughter property StorageActionAttr, ReaderActionAttr
  ### which configure and Action and a Reader to store and to
  ### the information. 
  ###
  ### Notice: will be integrated in phase3 only. 
  ###

  def Float( self, value):
    return float( value )

  def Int(self, value):
    return int( value )
  
  def Str( self, value ):
    return str( value )
  
  def valueAction( self, value ):
    ### Getting the type of the value
    ### in this case it both support int, float, str, as long they are
    ### found inside __builtins__ class .
    ### This candidate is good for both setValue and setFormat
    AttrType=type( value ).__name__ 
    print "SetBuildStatement Storing through function: {}\n\tStoring a Type:{}, value:[{}], order: {}".format( self.valueAction.__name__, AttrType, value , len(self.ListBuildStatement)+1 )
    if AttrType not in [ 'float', 'int', 'str' ]:
      self.ListBuildStatement.append( value )
    else:
      self.ListBuildStatement.append( getattr( self , AttrType.capitalize() )( value ) )
      
    ### This line is personally more efficient than :
    ### 'eval( "{}( {} )".format(AttrType, value) )'
    ### Other alternative include making our own self.float(), self.int() inside this
    ### class to let call getter without __builtins__:
    ### ex:
    ### class SvgWebRenderer( SvgLxmlEngine ):
    ###   Int( self, value ):
    ###     return int( value )
    ###   Float( self, value ):
    ###     return float( value )
    ###   def valueAction( self, value ):
    ###     AttrType=type( value ).__name__ 
    ###     self.ListBuildStatement.append( getattr( self , AttrType.capitalize() )( value ) )
    ### 

  def valueReader( self, ListItem ):
    ### No Transformation 
    return ListItem

  def formatReader( self, ListItem ):
    ### do Transform value into Type of value,
    ### often used in value display during debug.
    ReturnList=list()
    for item in ListItem :
      ValueStore="type:{}, value:[{}]"
      ReturnList.append( ValueStore.format( type( item ).__name__, item ) )
    return ReturnList 

  def storeFloatAction( self, value ):
    print "SetBuildStatement Storing through function: {}".format( self.storeFloatAction.__name__ )
    self.ListBuildStatement.append( float( value ) )
    ### This one is a candidate for BuildStatementAttr == setStoreFloat
    ### allowing to use Setter from BuildStatement to store in Float format.

  def storeFloatReader( self, ListItem  ):
    ### Do ensure value are in Float type
    ReturnList=list()
    for item in ListItem:
      ReturnList.append( float( item ) )
    return ReturnList 

  def storeIntAction( self, value ):
    print "SetBuildStatement Storing through function: {}".format( self.storeIntAction.__name__ )
    self.ListBuildStatement.append( int( value ) )
    ### This one is a candidate for BuildStatementAttr == setStoreInt
    ### allowing to use Setter from BuildStatement to store in Int format.

  def storeIntReader( self, ListType ):
    ### Do ensure value are in Int type 
    ReturnList=list()
    for item in ListType:
      ReturnList.append( int( item ) )
    return ReturnList 
    

  ###
  ### Function for property StorageActionAttr
  ### Unlike BuildStatement, have it's Attribute to configure
  ### it's storage, StorageActionAttr, is another sub-property
  ### to use unique Attribute in storage to avoid 
  ### overdevelopping Agent to filter condition during storage 
  ### action, It does configure a name to store the information.
  ###
  def SetStorageActionAttr( self , value ):
    if value in self.StatementFormatList :
      if value in [ self.setValue, self.setFormat ]:
        self.BuildStatementAction = "valueAction"
      else:
        self.BuildStatementAction = "{}Action".format( value )

  def GetStorageActionAttr( self ):
    return self.BuildStatementAction

  def ResetStorageActionAttr( self ):
    self.BuildStatementAction = None

  StorageActionAttr = property(GetStorageActionAttr,SetStorageActionAttr, ResetStorageActionAttr )

  def SetReaderActionAttr( self, value ):
    ### Unlike SetStorageActionAttr, that do own exception like
    ### choosing setValue or setFormat for either BuildStatementAttr
    ### and StorageActionAttr does now own specific storage difference,
    ### do own specificities to hold the value 'as-is' until they are
    ### getting-out with a Getter. Here, There is an exception for
    ### every value ReaderActionAttr may require to be set .
    ### Notice, ReaderActionAttr is also setted like daughter of
    ### StorageActionAttr and inside BuildStatementAttr. 
    self.BuildStatementReader = "{}Reader".format( value )

  def GetReaderActionAttr( self ):
    return self.BuildStatementReader

  def ResetReaderActionAttr( self ):
    self.BuildStatementReader = None 


  ReaderActionAttr = property(GetReaderActionAttr,SetReaderActionAttr, ResetReaderActionAttr )

  def SetBSAttr( self, value ):
    if value in self.StatementFormatList:
      self.BuildStatementValue = value
      ### Configuring the StorageActionAttr at the same times. 
      self.StorageActionAttr = value
      self.ReaderActionAttr = value 
    else:
      raise PropertyWarning, "BuildStatementAttr, Incorrect value assigned to this property, based on Setter {}".format( self.SetBSAttr.func_name )

  def GetBSAttr( self ):
    return self.BuildStatementValue

  def ResetBsAttr( self ):
    self.BuildStatementValue = None
    ### Also Launching the Reset Member from following property:
    del self.StorageActionAttr
    del self.ReaderActionAttr 

  BuildStatementAttr = property( GetBSAttr, SetBSAttr, ResetBsAttr )
  
  ###
  ### Function for property BuildStatement
  ###
  ### Notice: base
  ### BuildStatement, replace property
  ### VariableFormat, hence to have similar 
  ### design, but return information inside 
  ### dict Statement[Buffer]. 
  ###
  ### Notice1:
  ### This part is clean since StorageActionAttr take
  ### over this step and do propose an unique action
  ### for all BuildStatementAttr value it can take
  ###if self.BuildStatementAttr == self.setStoreFloat:
  ###  for item in value:
  ###       self.ListBuildStatement.append( float( item )  )
  ###else:
  ###  for item in value:
  ###    self.ListBuildStatement.append( item )
  ###
  ### Notice2:
  ###
  ### Since StorageActionAttr is configured inside
  ### BuildStatementAttr, it not required to code
  ### specific exception for setStoreFloat, setStoreInt
  ### ... valueAction, storeFloatAction, storeIntAction
  ### are taking the value with uses of Getter of StorageActionAttr
  ### this mean we should coding this sequence as getattr( self, self.StorageActionAttr )( item )
  ### to take advantage of StorageActionAttr property. 
  ### The Getter of StorageActionAttr get rid of all
  ### theses lines. 
  #if self.BuildStatementAttr == self.setStoreFloat:
  #  self.ListBuildStatement.append( float(value) )
  #else:
  #  self.ListBuildStatement.append( value )
  ###
  ###
  ### Notice3:
  ### Actual uses of ReaderActionAttr does replace all this code
  ### under Getter of BuildStatement.
  ###
  ##      if self.BuildStatementAttr == self.setStoreFloat:
  ##        for item in self.ListBuildStatement:
  ##          ReturnList.append( float(item) )
  ##      if self.BuildStatementAttr == self.setValue:
  ##        ReturnList=self.ListBuildStatement
  ##    elif self.BuildStatementAttr == self.setFormat:
  ##      for item in self.ListBuildStatement:
  ##        ReturnList.append(type(item))
  ##    return ReturnList 
  ###
  ###
  ### Scheduled for phase2 
  ### 
  def SetBuildStatement( self, value ):
    """This Property-setter support following calling convention:\n\tBuildStatement = Variable\n\tBuildStatement = Variabl1, Variable2\n\tBuildStatement = [ Variable1, Variable2 ]\n"""
    ### First step, validating and forcing BuildStatementAttr
    ### to be set to setValue only if there is no already
    ### attribued value.
    if self.BuildStatementAttr not in self.StatementFormatList:
      if self.BuildStatementAttr == None:
        ### in case where BuildStatementAttr is clean and this property
        ### already receiving value, it enforce the  BuildStatementAttr
        ### to setValue . 
        self.BuildStatementAttr = self.setValue 
      else:
        raise PropertyWarning, "BuildStatementAttr not configured before using property BuildStatement, based on Setter, {}".format( self.SetBuildStatement.func_name ) 
        
    if type(value) in self.PropertyTypeCheck :
      if len( value ) > 0:
        for item in value:
          ### See Notice1 under Function for property BuildStatement
          getattr( self, self.StorageActionAttr )( item )
    else:
      ### See Notice2 under Function for property BuildStatement
      getattr( self, self.StorageActionAttr )( value )

  def GetBuildStatement( self ):
    ###ReturnList=[]
    ###ReturnValueList=[ self.setValue, self.setStoreFloat ]
    ### No longer needed since all value BuildStatementAttr may
    ### take will have a StoreAction and a Reader associated. 
    ###if self.BuildStatementAttr in ReturnValueList:
      ### See Notice3 under Function for property BuildStatement
    return getattr( self, self.ReaderActionAttr )( self.ListBuildStatement )

  def DelBuildStatement( self ):
    """This is a Property-reset or reseting of the ListVariableFormat list. It also
require to reset the BuildStatementAttr, since a type-check of SetBuildStatement, do
require having a clean BuildStatementAttr (BuildStatementAttr==None) to start a type
check-validity in case receving argument."""
    self.ListBuildStatement=list()
    del self.BuildStatementAttr
    

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
    if type(value) in self.PropertyTypeCheck :
      if len( value ) > 0:
        for item in value:
          self.ListVariableFormat.append( item )
      else:
          self.ListVariableFormat.append( value[0] )
    else:
      self.ListVariableFormat.append( value )

  def GetVariableFormat( self ):
    return self.ListVariableFormat

  def DelVariableFormat( self ):
    """This is a Property-reset or reseting of the ListVariableFormat list."""
    self.ListVariableFormat=None
    self.ListVariableFormat=list()

  """VariableFormat Property used inside _stroke_style and _colorSpace function. Since both are not called altogether, they are working during uses of BuilStatement property. Explainned early in function SetStrokeDash to work by appending variable inside a list() and does use printf-defined type-format know by %d, %s, %[0-9]+f used inside most template, before merge to SvgLxmlEngine"""
  VariableFormat = property( GetVariableFormat, SetVariableFormat, DelVariableFormat )

  

  ### 
  ### End-of property VariableFormat
  ### 

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def FormatStroke( self, StrDashType, StyleId  ):
    print "dasharray configuration:{}".format( str( self.VariableFormat ) )
    StrReturnFormat=str() 
    if len(self.VariableFormat) > 0:
      StrReturnFormat=self.StrokeType[StrDashType][StyleId].format( self.StrokeType[StrDashType]['name'] ).format( *self.VariableFormat ) 
    else:
      StrReturnFormat=self.StrokeType[StrDashType][StyleId].format( self.StrokeType[StrDashType]['name'] )
    del self.VariableFormat 
    self.FormatStrokeValue=StrReturnFormat
    print "FormatStroke return: DashType{}, StyleId{}, result:[ {} ]".format( self.StrokeType[StrDashType]['name'], self.StrokeType[StrDashType][StyleId], self.FormatStrokeValue )
    

  def FormatTemplate( self ):
    StrReturnFormat=str()
    if len(self.VariableFormat) > 0:
      StrReturnFormat=self.TemplateString.format( *self.VariableFormat ) 
    else:
      StrReturnFormat=self.TemplateString 
    return StrReturnFormat


  ### Function: ValueFormatHandler
  ### A function to replace hand-made format and aim to return
  ### the error withing parsing problem. in common function some
  ### call of self.VariableFormat or self.BuildStatement simply
  ### not working. This function does the same as:
  ###
  ### self.[NAME] = [Template].format( property([self.VariableFormat|self.BuildStatement]))
  ### And it throw you the error, showing you the template and
  ### display elements not
  ###
  ### Demonstration of uses:
  ###
  ### this line :
  ### StrArcPoint=self.DrawArcPointTemplate.format( *self.BuildStatement )
  ### Will be replaced by 
  ### self.ValueFormatHandler( self.DrawArcPointTemplate, 'BuildStatement', 'ArcPoint' )
  ### it will generate a self.ArcPoint accessible everywhere in the class. 
  ###
  ###


  ###
  ### Function for property ValueFactory.
  ### Used inside ValueFormatHandler as property 
  ### to store inside class a tuple of 2 value. 
  ### usually the AttrClassName and the result
  ### this one is taked back by a FormatHandler
  ### handled inside function ValueFormatHandler
  ### to either help overwriting value in the
  ### class or appending value to current
  ### class-attribute. 
  def SetValueFactory( self, value ):
    if len(value) == 2:
      if type( value[0] ).__name__ != 'property' :
        raise PropertyWarning, "ValueFactory First value should be a tuple inline list-based property\n\t:example:\n\tself.FormatHandler = self.BuildStatement,value2\n\tself.FormatHandler = self.VariableFormat,value2. Raised by Setter, {}".format( self.SetValueFactory.func_name )
      else:
        self.ValueFactoryRef = value
    else:
      raise PropertyWarning, "ValueFactory Does require inline-tuple use of this property\n\t:example: self.FormatHandler = value1,value2. And should not exceed 2 value.\n\tRaised by Setter, {}".format( self.SetValueFactory.func_name )

  def GetValueFactory( self ):
    return self.ValueFactoryRef

  def ResetValueFactory( self ):
    self.ValueFactory = None

  ValueFactory=property( GetValueFactory, SetValueFactory, ResetValueFactory ) 
  
  ###
  ### Function for property FormatHandler.
  ### Used inside ValueFormatHandler as property
  ### to write to a new variable or appending to 
  ### existing one, information like Parsed 
  ### information, from either BuildStatement or
  ### VariableFormat.
  ### ValueFormatHandler, consist to be an 
  ### equivalent to TemplateToValueParser less
  ### not writing to a Buffer and accept List-property
  ### builder. 
  ###
  ###
  
  def SetFormatHandler( self, value ):
      if value in self.FormatHandlerList:
        self.FHPropertyValue=value
      else:
        raise PropertyWarning, "FormatHandler not configured before using ValueFormatHandler; Raised by Setter, {}".format( self.SetFormatHandler.func_name ) 
    
  def GetFormatHandler( self ):
    attrName, StringParsed = self.ValueFactory
    if self.FHPropertyValue == self.setInitialize:
      setattr( self, attrName, StringParsed )
    if self.FHPropertyValue == self.setAppend:
      if hasattr( self, attrName ):
        setattr( self, attrName, "{}{}".format( getattr( self, attrName ), StringParsed ) )
      else:
        raise PropertyWarning, "FormatHandler can not append to non existing class-attribute; Raised by Getter, {}".format( self.GetFormatHandler.func_name ) 

  def ResetFormatHandler( self ):
    self.FHPropertyValue=None 

  FormatHandler=property( GetFormatHandler, SetFormatHandler, ResetFormatHandler)
    
  def ValueFormatHandler( self, StrTemplate, AttrProperty, AttrClassName ):
    StrParse=str()
    try:
      StrParse=getattr( StrTemplate, 'format')( *getattr(self,AttrProperty) )
    except( TypeError, ValueError, AttributeError ):
      print "Exception raised,\n\tTemplate:{}\n\tvalue:{}\n".format( StrTemplate, str( getattr( self, AttrProperty ) ) )
    else:
      print "Sucessfully parsed Template:\n\t{}".format( StrTemplate.format( *getattr( self, AttrProperty ) ) )
      self.ValueFactory = AttrClassName, StrParse
      self.FormatHandler
      getattr( getattr( self.__class__, AttrProperty ), 'fdel')()
      getattr( self.ValueFactory, 'fdel')()
      getattr( self.FormatHandler, 'fdel')()

  def TemplateToValueParser( self, StrTemplate ):
    try:
      self.RenderToBuffer = StrTemplate.format( *self.BuildStatement )
    except ( TypeError, ValueError, AttributeError ):
      self.BuildStatementAttr = self.setFormat
      print "Exception raised,\n\tTemplate:{}\n\tvalue:{}\n".format( StrTemplate, str(self.BuildStatement) )
      ### Required to erase the self.BuildStatement, even if the exception is raised:
      del self.BuildStatement
      #self.BuildStatementAttr = self.setFormat
      #print "Template:{},\nValue by type:{}\n".format( self.BuildStatement )
    else:
      print "Sucessfully parsed Template:\n\t{}".format( StrTemplate.format( *self.BuildStatement ) )
      ### It's important to free the BuildStatement property, to let the new statement
      ### of vector adding new information without leaving anciens one and let the
      ### String.format(...) throwing a TypeError . 
      del self.BuildStatement
      ### A function calling TemplateToValueParser, should'nt require to clean
      ### self.BuildStatementAttr since this function does it at the end. 
      self.BuildStatementAttr = self.setValue


  def WriteBuffer( self, StringText ):
    self.Buffer += StringText

  def FileWriter( self ):
    """Using the StringIO.getvalue() from RenderToBuffer property it
    retreive all the String buffered from all elements called during
    a render action from dia."""
    self.FileHandler.write( self.RenderToBuffer )
    self.FileHandler.close()
  
  def _open(self, filename) :
    if self.ShowOptionWindows is True :
      self.WindowsInterface( )
    self.FileHandler = open(filename, "w")

  def begin_render (self, data, filename) :
    self._open( filename )
    r = data.extents
    xofs = - r[0]
    yofs = - r[1]
    #del self.BuildStatement
    ### Because the begin_render is the first instruction it should'nt require to
    ### clean the BuildStatement.
    self.BuildStatementAttr = self.setStoreFloat 
    self.BuildStatement = float(r.right - r.left), float(r.bottom - r.top), r[0], r[1], r[2], r[3]
    self.TemplateToValueParser( self.StrFileHeader )
    del self.BuildStatementAttr
    self.BuildStatementAttr = self.setValue

    #self.RenderToBuffer = self.StrFileHeader.format( self.BuildStatement )
    #self.f.write("<!-- %s -->\n" % (str(data.extents)))
    #self.f.write("<!-- %s -->\n" % (data.active_layer.name))

  def end_render(self) :
    self.RenderToBuffer = self.TagElementSvgClosure
    self.FileWriter( )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_linewidth (self, width) :
    if width < 0.05 : # zero line width is invisble ?
      self.line_width = 0.05
    else :
      self.line_width = width

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_linecaps (self, mode) :
    self.line_caps = mode

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_linejoin (self, mode) :
    self.line_join = mode

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_linestyle (self, style) :
    self.line_style = style

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_dashlength (self, length) :
    self.dash_length = length

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_fillstyle (self, style) :
    # currently only 'solid' so not used anywhere else
    self.fill_style = style

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def set_font (self, font, size) :
    self.font = font
    self.font_size = size

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_line (self, start, end, color) :
    del self.BuildStatement
    self._colorSpace( color )
    self._stroke_style()
    self.set_linewidth( 0 )
    self.BuildStatement = start.x, start.y, end.x, end.y, self.ColorSpaceObject, self.line_width, self.StrokeStyleValue 
    self.TemplateToValueParser( self.DrawLineTemplate )    

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_polyline (self, points, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self._colorSpace(color)
    self._stroke_style()
    self._setPointString( points ) 
    self.BuildStatement = self.ColorSpaceObject, self.line_width, self.StrokeStyleValue, self.PointStringValue  
    self.TemplateToValueParser( self.DrawPolyLineTemplate )
    
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_polygon (self, points, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self._colorSpace(color)
    self._stroke_style()
    self._setPointString( points )
    self.set_linewidth( 0 )
    self.BuildStatement = self.ColorSpaceObject, self.line_width, self.StrokeStyleValue, self.PointStringValue 
    self.TemplateToValueParser( self.DrawPolygonTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_rect (self, rect, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self._colorSpace(color)
    self._stroke_style()
    self.set_linewidth( 0 )
    self.BuildStatement = rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, self.ColorSpaceObject, self.line_width, self.StrokeStyleValue
    self.TemplateToValueParser( self.DrawRectangleTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color)


  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_ellipse (self, center, width, height, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    #parameter cx, cy, rx, ry, stroke, stroke-width ; ?
    self._colorSpace(color)
    self._stroke_style()
    self.set_linewidth( 0 )
    self.BuildStatement = center.x, center.y, width / 2, height / 2, self.ColorSpaceObject, self.line_width, self.StrokeStyleValue
    self.TemplateToValueParser( self.DrawEllipseTemplate )
      
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_bezier (self, bezpoints, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    ### Unless it don't hold all the elements even part of complex one,
    ### it's useless to prepare a self.BuildStatement for color, line
    ### because the loop of bezpoints will throw an TypeError after first
    ### parsed elements and final template will hodl about nothing except
    ### over-crowed informations.
    self._colorSpace(color)
    self._setBezPoint( bezpoints )
    self._stroke_style()
    self.set_linewidth( 0 )
    self.BuildStatement = self.ColorSpaceObject, self.line_width, self.StrokeStyleValue, self.BezPointsList
    self.TemplateToValueParser( self.DrawBezierTemplate )
    ### No more need to close an element, all template were adjusted to hold second level of
    ### parsing, making them complete instead of concatenating part
    #self.WriteBuffer( self.TagElementClosure )

  ### Inside binding/dia-render.cpp  / binding/dia-render.h which is
  ### probably the main interface sending API-call, it offer another
  ### draw_text, where belong to dia document :
  ### 
  ### An Object with :
  ###    Properties( as dict() form ) hold
  ###    and element Properties['property'] have an attribute text
  ###    where it hold it's own sub-attribute:
  ###     -color
  ###     -font
  ###     -height
  ###     -position
  ###     -text 
  ### 
  ### --> draw a Text.  It holds its own information like position, style, ...
  ### void 
  ###     dia::Renderer::draw_text (Text* text)
  ### Belong to dia-documents pydiadoc.png available at 
  ### https://wiki.gnome.org/Apps/Dia/Python?action=AttachFile&do=view&target=pydiadoc.png
  ### 
  ### text can hold 
  ###   text.color
  ###   text.font
  ###   text.height
  ###   text.position -> text.position.x
  ###                    text.position.y
  ###   and text.text
  ###  
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_text (self, text) :
    if len(text.text) > 0 :
      talign = self.TextAlign [text.alignment]
      fstyle = self.FontStyleT [text.font.style & 0x03]
      fweight = self.FontWeightT [(text.font.style  >> 4)  & 0x7]
      #del self.BuildStatement, see message inside TemplateToValueParser .
      ### This BuildStatement hold 9 variables to parse within this Template.
      #parameter: x, y, text-anchor, font-size, fill:color, font-family, font-style, font-weight, text
      self._colorSpace(text.color)
      self.TextSubst( text.text )
      self.BuildStatement = text.position.x, text.position.y, talign ,text.font_size, self.ColorSpaceObject, text.font.family, fstyle,  fweight, self.Text
      self.TemplateToValueParser( self.DrawStringTemplate )
    else:
      raise EmptyTextString( text.text ) 

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_string (self, text, pos, alignment, color) :
    if len(text) > 0 :
      talign = self.TextAlign [alignment]
      fstyle = self.FontStyleT [self.font.style & 0x03]
      fweight = self.FontWeightT [(self.font.style  >> 4)  & 0x7]
      #del self.BuildStatement, see message inside TemplateToValueParser .
      ### This BuildStatement hold 9 variables to parse within this Template.
      #parameter: x, y, text-anchor, font-size, fill:color, font-family, font-style, font-weight, text
      self._colorSpace(color)
      self.TextSubst( text )
      self.BuildStatement = pos.x, pos.y, talign ,self.font_size, self.ColorSpaceObject, self.font.family, fstyle,  fweight, self.Text
      self.TemplateToValueParser( self.DrawStringTemplate )
    else:
      raise EmptyTextString( text ) 
    
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def draw_image (self, point, width, height, image) :
    #FIXME : do something better than absolute pathes ?
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self.BuildStatement = point.x, point.y, width, height, image.uri 
    self.TemplateToValueParser( self.DrawImageTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def fill_arc (self, center, width, height, angle1, angle2, color) :
    self._arc(center, width, height, angle1, angle2, color, 1)

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def fill_ellipse (self, center, width, height, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    #parameter: cx, cy, rx, ry, fill:color,
    self._colorSpace( color )
    RadiusH=height / 2
    RadiusW=width / 2
    self._stroke_style()
    self.set_linewidth( 0 )
    self.BuildStatement = center.x, center.y, RadiusW, RadiusH, self.ColorSpaceObject, "none", self.line_width , self.StrokeStyleValue
    self.TemplateToValueParser( self.DrawFillEllipseTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def fill_bezier (self, bezpoints, color) :
    #del self.BuildStatement, see message inside TemplateToValueParser .
    self._colorSpace(color)
    self._setBezPoint( bezpoints  ) 
    self.BuildStatement = self.ColorSpaceObject , self.line_width , self.BezPointsList
    self.TemplateToValueParser( self.DrawFillBezierTemplate )
    #self.WriteBuffer( self.TagElementClosure )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def fill_polygon (self, points, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self._colorSpace(color)
    self._setPointString( points )
    self._stroke_style()
    self.BuildStatement = self.ColorSpaceObject, self.line_width , self.StrokeStyleValue , self.PointStringValue  
    self.TemplateToValueParser( self.DrawFillPolygonTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def fill_rect (self, rect, color) :
    #del self.BuildStatement , see message inside TemplateToValueParser .
    self._colorSpace(color)
    self.set_linewidth( 0 )
    self._stroke_style()
    self.BuildStatement = rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, self.ColorSpaceObject, self.line_width, self.StrokeStyleValue
    self.TemplateToValueParser( self.DrawFillRectTemplate )

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
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
    StrArcPoint=self.DrawArcPointTemplate.format( *self.BuildStatement )

    if not fill :
      ### Since self.BuildStatement was used to parse self.DrawArcPointTemplate, which is
      ### only the end-element, it require to reset the BuildStatement to add information
      ### about color, line, stroke, and at last All the Point, forming the arc.
      ### Other condition to use the Reset, DrawArcPointTemplate was parsed using the
      ### BuildStatement
      del self.BuildStatement
      self._colorSpace(color)
      self._stroke_style()
      self.BuildStatement = self.ColorSpaceObject, self.line_width, self.StrokeStyleValue , StrArcPoint
      self.TemplateToValueParser( self.DrawArcNofillTemplate )
    else :
      ### Since self.BuildStatement was used to parse self.DrawArcPointTemplate, which is
      ### only the end-element, it require to reset the BuildStatement to add information
      ### about color of the arc and the Point forming the Arc. 
      ### Other condition to use the Reset, DrawArcPointTemplate was parsed using the
      ### BuildStatement
      del self.BuildStatement
      self._colorSpace(color)
      self.BuildStatement = self.ColorSpaceObject, StrArcPoint 
      self.TemplateToValueParser( self.DrawArcFillTemplate )


  # avoid writing XML special characters (ampersand must be first to not break the rest)
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def TextSubst( self, StrVar ):
    print "TextSubstitution, processing {} characters exception.".format( len(self.CharExceptionRepl) )
    for CharIndex in self.CharExceptionRepl :
      StrVar=StrVar.replace( CharIndex[0],CharIndex[1] )
    print "Text from String Vector:[{}]".format( StrVar )
    self.Text=StrVar 

    # Helpers, not in the DiaRenderer interface
  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _setPointString( self, points ):
    StrPointList=str()
    for pt in points :
      StrPointList += self.Point2DTemplate.format(pt.x, pt.y)
    self.PointStringValue=StrPointList

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _setBezPoint(self, bezpoints):
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
        StrBezier+=self.BezierMoveToTemplate.format( *self.BuildStatement )
      elif bp.type == 1 : # BEZ_LINE_TO
        ### Same as *Part1, except it's self.BezierLineToTemplate that is the end
        ### element introduced inside BuildStatement 
        self.BuildStatement = bp.p1.x, bp.p1.y
        StrBezier+=self.BezierLineToTemplate.format( *self.BuildStatement )
      elif bp.type == 2 : # BEZ_CURVE_TO
        ### Same as *Part1, except it's self.BezierLineToTemplate that is the end
        ### element introduced inside BuildStatement 
        self.BuildStatement = bp.p1.x, bp.p1.y, bp.p2.x, bp.p2.y, bp.p3.x, bp.p3.y
        StrBezier+=self.BezierCurveToTemplate.format( *self.BuildStatement )
      else :
        dia.message(2, "Invalid BezPoint type (%d)" * bp.type)
      ### Since a loop-resence does enforce the fact BuildStatement will receive
      ### new argument for each elements of bp it mean at the end StrBezier will
      ### hold n-amount of a mix of BezierMoveToTemplate/BezierLineToTemplate/
      ### BezierCurveToTemplate, and even leaving the loop, self.BuildStatement
      ### should be empty, be cause This section fill information for the last
      ### elements, it will be inserted (StrBezier) at the end.
      del self.BuildStatement
    self.BezPointsList = StrBezier
    #return StrBezier 

  def _testColorSpaceName( self, color, StrName ):
    IsColorInAttr=False
    for ColorName in self.ColorSpace[StrName]:
      if IsColorInAttr is False:
        if hasattr( color , ColorName ):
          IsColorInAttr=True
    if IsColorInAttr is True:
      print "Color Space is : {}, using componnent named:{}".format( StrName, str( self.ColorSpace[StrName] ) )
    return IsColorInAttr

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _colorSpace(self, color) :
    # given a dia color convert to svg color string
    # a tweak in case creator of Dia opt for opacity
    # in diagram...
    self.BuildStatementAttr = self.setStoreInt
    StrTemplateChoice=str(self.Color3SpaceTemplate)
    ### Testing if atribute 'red' or 'hue' exist...
    if self._testColorSpaceName( color, 'RGB' ) is True :
      ### This mean color are coded in RGB style.
      self.BuildStatement = int( color.red ) * 255, int( color.green ) * 255, int( color.blue ) * 255
      print "Actual color value:[#{:02X}{:02X}{:02X}]".format( *self.BuildStatement )
    if self._testColorSpaceName( color, 'HSV' ) is True  :
      ### This mean color are coded in HSV style. 
      self.BuildStatement = 255 * int(color.hue),255 * int(color.saturation),255 *int(color.value)
    if hasattr( color , 'opacity'):
      ### make an addition, adding color in 4 spaces instead, and adding opacity at the end....
      ### How beautiful are Property, simplify the branching statement like to not
      ### develop and opacity branch-condition if the attribute does or does not exist.
      StrTemplateChoice=str(self.Color4SpaceTemplate)
      self.BuildStatement = 255 * int(color.opacity)

    self.ColorSpaceObject = StrTemplateChoice.format( *self.BuildStatement )    
    # And it's extremely inportant to reset the VariableFormat since
    # it's commonly use to build a stroke and do introduce
    # color... This mean, and SHOULD HAVE to execute _colorSpace(...) before
    # it's template to parse...
    del self.BuildStatement
    #self.BuildStatementAttr = self.setValue
    #return StrColorSpace

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _line_space_style( self ):
    del self.VariableFormat
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
      self.FormatStroke( 'dasharray', self.line_style )
      StrTypeLine=StrTypeLine.format( self.FormatStrokeValue )

    print "dasharray: {}".format( str( self.VariableFormat ) )
    #del self.VariableFormat
    self.LineSpaceStyle = StrTypeLine
    #return StrTypeLine

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _line_join_style( self ):
    StrLineJoin="{}"
    if self.line_join == 0 : # MITER
      StrLineJoin=""
    else:
      self.FormatStroke( 'linejoin', self.line_join )
      print "FormatStroke return: {}".format( self.FormatStrokeValue )
      StrLineJoin=StrLineJoin.format( self.FormatStrokeValue )
    print "linejoin: {}".format( self.line_join )
    self.LineJoinValue = StrLineJoin
    

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _line_caps_style( self ):
    StrLineCaps="{}"
    if self.line_caps == 0 : # BUTT
      StrLineCaps=""
    else:
      self.FormatStroke( 'linecap', self.line_caps )
      StrLineCaps=StrLineCaps.format( self.FormatStrokeValue  )
    print "line_caps: {}".format( self.line_caps )
    self.LineCapsValue=StrLineCaps

  @SvgLxmlEngine.NameFunc( ListFunctionReference )
  def _stroke_style(self) :
    #self._line_space_style() 
    StrStrokeStyle = "{}{}{}"
    self._line_space_style()
    self._line_join_style()
    self._line_caps_style()
    self.StrokeStyleValue = StrStrokeStyle.format( self.LineSpaceStyle , self.LineJoinValue, self.LineCapsValue)

  ### Other specialisation not implemented but present inside binding/dia-render.cpp , dia-render.h
  ###
  ### a polyline with round coners
  ### void 
  ###     dia::Renderer::draw_rounded_polyline (Point *points, 
  ###      int num_points, Color *color, double radius )
  ### 
  ### --> specialized draw_rect() with round corners
  ### 
  ### void 
  ###     dia::Renderer::draw_rounded_rect (Point *ul_corner, 
  ###      Point *lr_corner, Color *color, real radius)
  ### 
  ### --> specialized draw_rect() with round corners
  ### 
  ### void 
  ###     dia::Renderer::fill_rounded_rect (Point *ul_corner, 
  ###      Point *lr_corner, Color *color, real radius ) 
  ### 
  ### --> specialized draw_line() for renderers with an own concept of Arrow
  ### 
  ### void 
  ###     dia::Renderer::draw_line_with_arrows  (Point *start, 
  ###      Point *end, real line_width, Color *line_color, 
  ###      Arrow *start_arrow, Arrow *end_arrow)
  ### 
  ### --> specialized draw_line() for renderers with an own concept of Arrow
  ### 
  ### void 
  ###     dia::Renderer::draw_arc_with_arrows (Point *start, 
  ###      Point *end, Point *midpoint, real line_width, Color 
  ###      *color, Arrow *start_arrow, Arrow *end_arrow)
  ### 
  ### --> specialized draw_polyline() for renderers with an own concept of Arrow
  ### 
  ### void 
  ###     dia::Renderer::draw_polyline_with_arrows (Point *points,
  ###      int num_points, real line_width, Color *color, Arrow 
  ###      *start_arrow, Arrow *end_arrow)
  ### 
  ### --> specialized draw_rounded_polyline() for renderers with an 
  ###   own concept of Arrow
  ### void 
  ###     dia::Renderer::draw_rounded_polyline_with_arrows (Point
  ###      *points, int num_points, real line_width, Color *color, 
  ###      Arrow *start_arrow, Arrow *end_arrow, real radius ) 
  ### 
  ### --> specialized draw_bezier() for renderers with an own
  ###    concept of Arrow
  ### void
  ###     dia::Renderer::draw_bezier_with_arrows ( BezPoint *points, int
  ###      num_points, real line_width, Color *color, Arrow *start_arrow,
  ###      Arrow *end_arrow)
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 
  ### 


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



IntPidDia=GetIntPid( r'(?u)^([a-zA-Z\-_]*dia|dia)+[a-zA-Z\-_]+' )
try:
  if IntPidDia != None:
    print "dia application found: PID: {}".format( IntPidDia )
    try:
      import dia
      dia.register_export ("SVG (uses of style attribute)", "svg", SvgWebRenderer())
      dia.register_export ("SVG Base64 (uses of style attribute)", "svg.base64", SvgBase64Codec())
      dia.register_export ("SVG compressed (uses of style attribute)", "svgz", SvgCompression())
    except ImportError:
      print "This message happen because dia or pydia is not\nloaded from dia python console.\n\nTemporary   \"deferring\"   registration  of  module. \nThis python  module  is  loaded  out  of  a  dia\nenvironment; And  can be  loaded  from dia-python\nconsole  or  loading explicitly  pydia  modules\nfrom  « plug-ins / python » dia  path.\n\nSvgLxmlEngine class can be used alone."
  else:
    raise NameError
except NameError :
  print """Module like SvgWebRenderer, SvgBase64Codec, SvgCompression, are dia or\npydia dependent and can not be loaded alone or out of dia c-API interface.\nSvgLxmlEngine class can be used alone.\n\n"""
  


