#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- file : LxmlWxGladeReader.py -*-

import sys, io, re, os, os.path ,string, base64, gzip, math 

from io import StringIO
from io import BytesIO

from StringIO import StringIO

import lxml
from lxml import etree

import tempfile
from tempfile import TemporaryFile

class XmlGladeProperty( object ):
  """This class is a Property-class to help WxGladeReader to work.

  The goal is to developt a rapid method to read from a wxglade file holding
  in xml-format, componnent that make a windows being generated in python. This
  WxGladeReader, will developt a dictionnary related instance in the Class of
  this file and make call linked to this instead of creating attribute inside the
  class. To make WxGladeReader easy to read, It should add a Property-class made
  from property member help this class access easily to lxml.etree , etree.iterparse
  and managing xml-attribute conform to etree.iterparse that generate both events,
  elements. And many possibilities including the parser.

  As the same fashion as XRC method left in wx sets, require a lot of exception and
  sometimes , example left on the internet are not accurate and not working at all.
  This is why it's a simple artefact help ready directly the wxglade file or ui
  creation and should generate almost same elements as python class file.
  """

  ListKeyName = [ 'eventlist', 'xmldataobj', 'filename', 'obj', 'objaction', 'bufferdata', 'typename', 'attrname' ]
  ListPropertyValue = [ 'Rewind' ]
  ListTypeBuffer = [ 'StringIO', 'BytesIO', 'TemporaryFile' ]
  ### 'StringIO', 'BytesIO', 'TemporaryFile' 
  
  ### 
  ### Key to hold component of property 
  ###
  ### Or replaced by self.StaticAttributeCreation( self.ListKeyName )
  #eventlist=ListKeyName[0]
  #xmldataobj=ListKeyName[1]
  #filename=ListKeyName[2]
  #obj=ListKeyName[3]
  #objAction=ListKeyName[4]

  ### 
  ### Value accepted by somes property 
  ### 
  ### Or replaced by self.StaticAttributeCreation( self.ListPropertyValue )
  #Rewind=ListPropertyValue[0]
  PropertyListDef=list()
  XmlDictType={ 'eventlist':list(),
                'xmldataobj':None,
                'filename':None,
                'obj':None,
                'objaction':None,
                'bufferdata':None}

  XmlPropertyConf={ 'Events':[ 'GetEvents', 'SetEvents', 'ResetEvents'],
                    'BufferData':['GetBufferData','SetBufferData','ResetBufferData'], 
                    'DataIO':[ 'GetDataIO', 'SetDataIO', 'ResetDataIO']
                    }

  UseAttributeCreationFilter = False
  XmlDict=dict( )

  #XmlDict[eventlist] = list()
  #XmlDict[xmldataobj] = None

  def SetPrePropertyList( self, value ):
    if type( value ).__name__ == type(list()).__name__:
      print "Receiving Function from a list:{}".format( value )
      self.PropertyListDef.extend( value )
    else:
      self.PropertyListDef = value

  def GetPrePropertyList( self ):
    ListProperty=list()
    print "Next Property will use theses function:{}".format( self.PropertyListDef )
    ListProperty.extend( map( lambda n: getattr( self, n), self.PropertyListDef) )
    #for item in self.PropertyListDef:
    #  ListProperty.append( getattr(self, item ) ) 
    return ListProperty

  def ResetPrePropertyList( self ):
    self.PropertyListDef=list()

  PreProperty=property( GetPrePropertyList, SetPrePropertyList, ResetPrePropertyList ) 

  def PropertyTypeConf( self, dictType, dictProperty ):
    for key in dictType.keys() :
      print "Dictionnary key:{}, initialized to type: {}".format( key, type(dictType[key]) )
      dictProperty[key]=dictType[key]
  
  def StaticAttributeCreation( self, ListAttr, defaultSuffix="Attribute" ):
    for item in ListAttr:
      print "Creating {}: {}".format( defaultSuffix,item )
      setattr( self, item, item )
      #self.__class__.__setattr__( getattr( self, item ), item )

  ### Identical to StaticAttributeCreation be rely on filter action
  ### only, no for no extra-debug... 
  def StaticAttributeCreationFilter( self, ListAttr ):
    filter( lambda item: setattr( self, item, item ), ListAttr )


  """PropertyGenerator require XmlPropertyConf to work and property PreProperty
  which is a property to create a list of function name and will by retreived
  inside PropertyGenerator with the Key from DictProperty which is suppose to
  be the Property name. This PropertyGenerator try to generate Property from
  the __init__ and require to call the function-name in form 'self.Function'
  instead of generating a property from Class inline call.

  This example only re-use know function, but a case like developping a higher-
  generic pattern-class having 3 function for (Getter, Setter, Reset), where
  parameter launched in a __init__ will change the Getter, Setter, Reset, and
  instanciating it with different parameter will make the Property
  acting differently...

  Acting differently like...
  - Having a property storing it's value somewhere, defining it to use
  our XmlDict will Get and Set from it.
  - 
  """
  def PropertyGenerator( self, DictProperty ):
    for strKey in DictProperty.keys( ):
      print "Generating property name: {}".format( strKey )
      self.PreProperty=DictProperty[strKey]
      setattr( self, strKey,  property( *self.PreProperty ) )
      ### Must re-initialize the self.PreProperty to avoid cumuling
      ### function name for next Property.
      del self.PreProperty
      #self.__class__.__setattr__( strKey , property( *self.PreProperty ) ) 
    

  def __init__( self ):
    self.events=None
    #self.StaticAttributeCreation( self.ListKeyName )
    #self.StaticAttributeCreation( self.ListPropertyValue )
    #self.PropertyTypeConf( self.XmlDictType, self.XmlDict )
    #self.PropertyGenerator( self.XmlPropertyConf )
    
  def SetEvents( self, value ):
    if type( value ).__name__ == type(list()).__name__:
      self.XmlDict[self.eventlist].extend( value )
    else:
      self.XmlDict[self.eventlist].append( value )

  def GetEvents( self ):
    return self.XmlDict[self.eventlist]

  def ResetEvents(self):
    self.XmlDict[self.eventlist]=list()

  #Events=property( GetEvents,SetEvents ,ResetEvents )

  def SetBufferData( self, value  ):
    if self.typename not in self.XmlDict[self.bufferdata].keys():
      if value in self.ListTypeBuffer:
        self.XmlDict[self.bufferdata]={self.typename:value}
        if self.attrname not in self.XmlDict[self.bufferdata].keys():
          self.XmlDict[self.bufferdata][self.attrname]=list()
      else:
        self.XmlDict[self.bufferdata]={self.typename:None}
    if self.XmlDict[self.bufferdata][self.typename] == None:
      if value in self.ListTypeBuffer:
        self.XmlDict[self.bufferdata]={self.typename:value}
        if self.attrname not in self.XmlDict[self.bufferdata].keys():
          self.XmlDict[self.bufferdata][self.attrname]=list()
    if self.XmlDict[self.bufferdata][self.typename] != None:
      if type( value ).__name__ == type(list()).__name__:
        self.XmlDict[self.bufferdata][self.attrname].extend( value )
      else:
        self.XmlDict[self.bufferdata][self.attrname].append( value )

  def GetBufferData( self ):
    StrTypeName=self.XmlDict[self.bufferdata][self.typename]
    print "Underlying information for DataIO will be use under type: {}".format( StrTypeName )
    ### First, allow linking the Type to self to make able to
    ### create variable from this class.
    setattr( self, StrTypeName , eval(StrTypeName) )
    if len( self.XmlDict[self.bufferdata][self.attrname] ) > 0:
      TypeReturn=getattr( self, StrTypeName)( *self.XmlDict[self.bufferdata][self.attrname] )
    else:
      TypeReturn=getattr( self, StrTypeName)( ) 
    return TypeReturn

  def ResetBufferData( self ):
    ### Removing Class-based type enforced from Setter
    delattr( self, self.XmlDict[self.bufferdata][self.typename] )
    self.XmlDict[self.bufferdata].clear()  

  def SetDataIO( self, value ):
    FileRead=open( value , 'r' )
    ### BytesIO( FileRead.read() ) 
    self.XmlDict[self.xmldataobj]={ self.filename:value,
                                    self.obj:self.BufferData }
    self.XmlDict[self.xmldataobj][self.obj].write( FileRead.read() )
    FileRead.close() 
    
  def GetDataIO( self ):
    return self.XmlDict[self.xmldataobj][self.obj]
    
  def ResetDataIO( self ):
    self.XmlDict[self.xmldataobj][self.obj].close()
    self.XmlDict[self.xmldataobj].clear()

class WxGladeReader( XmlGladeProperty ):

  

  def __init__( self, filename ):
    super( XmlGladeProperty, self ).__init__(  )
    if self.UseAttributeCreationFilter is True:
      self.StaticAttributeCreationFilter( self.ListKeyName )
      self.StaticAttributeCreationFilter( self.ListPropertyValue )
    else:
      self.StaticAttributeCreation( self.ListKeyName )
      self.StaticAttributeCreation( self.ListPropertyValue, defaultSuffix='Property Value' )
    self.PropertyTypeConf( self.XmlDictType, self.XmlDict )
    self.PropertyGenerator( self.XmlPropertyConf )


    ### Starting from generated Property BufferData,
    ### superseding the DataIO, it configure DataIO to
    ### use BytesIO, StringIO, TemporaryFile as memory
    ### entry:
    ### First use of Property self.BufferData should feed
    ### self.XmlDict[self.bufferdata][self.typename]
    ### Second use of Property self.BufferData should feed
    ### self.XmlDict[self.bufferdata][self.attrname]
    ### as example StringIO hold key buf='' so we can
    ### add the file-read from that entry, or use
    ### property self.DataIO.
    ### Another candidate TemporaryFile
    ### require mode[, r, b, w, rw+ ...],
    ### suffix=[file suffix],
    ### prefix=[file prefix],
    ### dir=[location of temporary file ]
    self.BufferData = 'StringIO'
     
    ### Starting from generated Property DataIO:
    self.DataIO = filename
    ### Preparing the event statement with Property Events
    self.Events = ["start", "end"]
    

  #def FromParser( self ):
  #  self.parser = etree.XMLParser(remove_blank_text=True)
  #  self.root = etree.XML(self.DataIO, self.parser)
    
  def PartialInspecter( self, StrFileOut ):
    FileOutput=file( StrFileOut, 'w' )
    #root = etree.XML(self.DataIO, self.parser)
    for event, element in etree.iterparse( self.DataIO, events=self.Events ):
      FileOutput.write( "Event:{:5s}, name:{:4s}, text:[{:s}]\n".format(event, element.tag, element.text) )
      #print("Event:{:5s}, name:{:4s}, text:[{:s}]".format(event, element.tag, element.text))
    FileOutput.close() 


if __name__ == "__main__":
  AGladeReader = WxGladeReader( './DiaImplement-option.wxg' )
  AGladeReader.PartialInspecter( './DiaImplement-option-out.txt' )

