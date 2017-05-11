#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- file : LxmlWxGladeReader.py -*-

import sys, io, re, os, os.path ,string, base64, gzip, math 

from io import StringIO
from io import BytesIO

from StringIO import StringIO

from lxml import etree



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

  ListKeyName = [ 'eventlist', 'xmldataobj', 'filename', 'obj', 'objaction' ]
  ListPropertyValue = [ 'Rewind' ]
  
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
                'objaction':None }

  XmlPropertyConf={ 'Events':[ 'GetEvents', 'SetEvents', 'ResetEvents'],
                    'DataIO':[ 'GetDataIO', 'SetDataIO', 'ResetDataIO']}

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

  def SetDataIO( self, value ):
    FileRead=open( value , 'r' )
    self.XmlDict[self.xmldataobj]={ self.filename:value,
                                    self.obj:BytesIO( FileRead.read() ) }
  def GetDataIO( self ):
    return self.XmlDict[self.xmldataobj][self.obj]
    
  def ResetDataIO( self ):
    self.XmlDict[self.xmldataobj][self.obj].close()
    self.XmlDict[self.xmldataobj]=None 

class WxGladeReader( XmlGladeProperty ):

  def __init__( self, filename ):
    super( XmlGladeProperty, self ).__init__(  )
    self.StaticAttributeCreation( self.ListKeyName )
    self.StaticAttributeCreation( self.ListPropertyValue, defaultSuffix='Property Value' )
    self.PropertyTypeConf( self.XmlDictType, self.XmlDict )
    self.PropertyGenerator( self.XmlPropertyConf )

    ### Starting from generated Property DataIO:
    self.DataIO = filename
    ### Preparing the event statement with Property Events
    self.Events = ["start", "end"]
    
  def PartialInspecter( self ):
    for event, element in etree.iterparse(self.DataIO, events=self.Events ):
      print("%5s, %4s, %s" % (event, element.tag, element.text))



if __name__ == "__main__":
  AGladeReader = WxGladeReader( './DiaImplement-option.wxg' )
