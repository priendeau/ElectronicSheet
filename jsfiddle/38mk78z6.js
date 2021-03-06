/*
 * File : 38mk78z6.js
 * */


function Base64()
{
  this.TableConversionChar="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" ;
  this.CharConv=String.fromCharCode ;
  this.BitStorageAperture=Math.round( Math.log(this.TableConversionChar.length) / Math.log(2) ) ;
  this.CharBitLength = 8 ;
  this.IntChecksum = Math.pow( 2 ,this.CharBitLength )-1 ; 
  this.CharConversionAt = function( )
  {
   var e={} ;  
   for( i=0 ; i< this.TableConversionChar.length ; i++ )
   {
    e[ this.TableConversionChar.charAt(i)]=i;
   } ;
   return e ;
  }
}

Base64.prototype.decode = function(s)
{
  
  var i,c,x,a ; 
  var b=0,l=0,r='' ;
  var L=s.length ;
  var e=this.CharConversionAt() ; 
  
  for( x=0 ; x < L ; x++ )
  {
   c=e[ s.charAt(x) ];
   b=( b << this.BitStorageAperture ) + c;
   l += this.BitStorageAperture;
   while( l >= this.CharBitLength )
   { 
    ( ( a=( b >>> ( l-= this.CharBitLength ) ) & this.IntChecksum ) || 
      ( x < ( L-2 ) ) ) && 
              ( r+=this.CharConv(a) );
   }
  }
  return r;
 }
 
Base64.prototype.encode = function(input) 
{
 var output = "";
 var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
 var i = 0;

 input = Base64._utf8_encode(input);

 while (i < input.length) 
 {

  chr1 = input.charCodeAt( i++ );
  chr2 = input.charCodeAt( i++ );
  chr3 = input.charCodeAt( i++ );

  enc1 = chr1 >> 2;
  enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
  enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
  enc4 = chr3 & 63;

  if (isNaN(chr2)) 
  {
   enc3 = enc4 = 64;
  } 
  else if (isNaN(chr3)) 
  {
   enc4 = 64;
  }

  output = output + 
    this.TableConversionChar.charAt(enc1) + 
    this.TableConversionChar.charAt(enc2) + 
    this.TableConversionChar.charAt(enc3) + 
    this.TableConversionChar.charAt(enc4);

 }

 return output;
} 


function DocGetDataAttr( ElementName, Attribute )
{
 var StrDataAttr="data-__NAME__" ; 
 return ElementName.getAttribute(StrDataAttr.replace("__NAME__",Attribute)) ;
}

function DataRenderFunction( StrData )
{
 var ElementImageNode  = 
 document.getElementById( StrData ) ;
 var ElementFDD = 
 document.getElementById( "FDD" ) ;
 var ArrayTagFunctionDef = 
 DocGetDataAttr(ElementFDD ,"DataRenderFunctionTagParse").split(',') ;
 var StrDebugStatus =
 DocGetDataAttr(ElementImageNode ,"debug" ).toLowerCase() ;
 var StrFunctionName = 
 DocGetDataAttr(ElementImageNode ,"function" ) ; 
 var StrFunctionStringDebug="false";
 var StrFunctionStringParam = 
 DocGetDataAttr(ElementImageNode, StrFunctionName ) ; 
 var StrTplFunctionTpl = 
 DocGetDataAttr(ElementImageNode, "FunctionTemplate" ) ;
 
 /*
 If inside the templated function It can find the __DEBUG__ tag it will inspect for attribute data-[functionname]Debug="value" to get the value . 
 */
 if( StrTplFunctionTpl.indexOf("__DEBUG__") > 0 )
 {
  StrFunctionStringDebug = 
  DocGetDataAttr( ElementImageNode, StrFunctionName + "Debug" ) ;
 }
 if( StrDebugStatus == "true" )
 {
  alert("Dataset "
        +StrFunctionName 
        + " result:" 
        + StrFunctionStringParam ) ;
 }

 var ArrayInfo=StrFunctionStringParam.split(';') ;
 var StrStringLoad = StrTplFunctionTpl ; 
 var StrItem ;
 
 for (IntC=0; IntC <= ArrayTagFunctionDef.length-1; IntC++) 
 {
  StrItem=ArrayTagFunctionDef[IntC].toString() ;
  if( StrItem.indexOf("__DEBUG__") >= 0 )
  {
   StrStringLoad=StrStringLoad.replace(
   StrItem,StrFunctionStringDebug ) ;
  }
  if( StrItem.indexOf("__TAG__") >= 0)
  {
   StrStringLoad=StrStringLoad.replace( 
   StrItem,ArrayInfo[0] ) ;
  }
  if( StrItem.indexOf("__ID__") >= 0)
  {
   StrStringLoad=StrStringLoad.replace(
   StrItem,ArrayInfo[1] ) ;
  }
  if( StrItem.indexOf("__FUNCT__") >= 0)
  {
   StrStringLoad=StrStringLoad.replace(
   StrItem,StrFunctionName) ; 
  }
 }
 
 if( StrDebugStatus == "true" )
 {
  alert("Following function will be called:" + StrStringLoad ) ;  
 }
 return StrStringLoad ; 
}

function ImageLoader()
{
 var FunctionCall = DataRenderFunction( "ImageLoader" ) ; 
 eval( FunctionCall ) ; 
}

function PinOutImage(StrTag, StrId, Debug)
{
 var strHeader="data:image/jpeg;base64," ; 
 var BufferBase64Img = "/9j/4AAQSkZJRgABAQEAYABgAAD/4QAWRXhpZgAASUkqAAgAAAAAAA"+
"AAAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"+
"HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQ"+
"wLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"+
"MjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCADhAFgDASIAAhEBAxEB/8"+
"QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgED"+
"AwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwR"+
"VS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVW"+
"V1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpK"+
"Wmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo"+
"6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBg"+
"cICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdh"+
"cRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nz"+
"g5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaH"+
"iImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0t"+
"PU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3"+
"+ql/eR2FlNdSthIk3EA8k+gqwzKELMwCjqTXA+NtbjmMdhBKrIoEsx"+
"RsgnsKmTshpXZhXfjDxCjs8eqbc/MsflIcAn1xVX/hNfEqtk6qD7eR"+
"H/hWPNK7vnPA6ColR5HWONC0jMFRepYmpRdkbh8d+Jhk/wBox8djDH"+
"/hTh498Tdr+FvbyV/wruvD3guw0y3WS9hjurxvmcyrkJ7KOlamo+HN"+
"K1C3aOSxtwcZVlQKR+I6VXKTdHmy+PfEpPzXcA/7YCpv+E88RKB/pF"+
"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"+
"/9k=";

 var StrJQueryLocator="__TAG__#__ID__" ;
 StrJQueryLocator=StrJQueryLocator.replace( "__TAG__" , StrTag  );
 StrJQueryLocator=StrJQueryLocator.replace( "__ID__", StrId ) ; 
 var NodeImgAddImage = document.getElementById(StrTag) ;
 var ImageLoader = new Image(  );
 ImageLoader.src=strHeader + BufferBase64Img ; 
 
 var StrImageInfoTpl="Initial image information\nHeight: __HEIGHT__\nWidth: __WIDTH__" ; 
 var StrImageInfo=StrImageInfoTpl ; 
 StrImageInfo=StrImageInfo.replace("__HEIGHT__", ImageLoader.height ) ; 
 StrImageInfo=StrImageInfo.replace("__WIDTH__", ImageLoader.width) ;
 if( Debug == "true")
 {
 alert( StrImageInfo ) ;
 }
 
 
 //ImageLoader.src=BufferBase64Img ; 
 //alert( "image height: " +  ImageLoader.height ) ; 
 /*ImageLoader.height=88 ; 
 ImageLoader.width=225 ; */
 
 //NodeImgAddImage.getAttribute("src").toString().length ) ; 
 
 //alert("New image length:" + BufferBase64Img.length ) ; 
 $( StrJQueryLocator ).attr("src", ImageLoader.src);
 if( Debug == "true")
 {
  alert("After image update" ) ; 
 }
 
 
}

function downloadURI(uri, ImgId ) 
{
  var link = document.createElement("a");
  link.download = name;
  link.href = uri;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  delete link;
}

function UpdateVref()
{
 var VForm = SVG( 'VectorFormula' ) ;
 var FormDebug = document.getElementById("VectorFormula") ;
 var IsDebug = new Boolean(false) ;
 if ( String(VForm.attr("debug")).toLowerCase() === "true" )
 {
  IsDebug=true ; 
 }
 
 var VoltageRef = document.getElementById("vref") ; 
 
 //var StrVRef = VoltageRef.textContent ; 
 var StrVRef = VoltageRef.textContent ; 
 
 if ( IsDebug == true ) 
 { 
  alert("Voltage Reference at creation:" + StrVRef ) ;  
 } 
 
 var NmVref = Number( StrVRef ) ;
 
 //var IntVref ;
 var IsUnderVref = new Boolean( NmVref < 1.25 ); 
 var IsOverVref = new Boolean( NmVref > 2.00 ); 
 var IsNoVref= new Boolean( NmVref == 0.0 ) ; 
 var StrAnswer ;
 StrAnswer = "NmVref < 1.25 : __IsUnderVref__\nNmVref > 2.00 : __IsOverVref__\nNmVref == 0.0: __IsNoVref__" ; 
 
 StrAnswer= StrAnswer.replace("__IsUnderVref__",IsUnderVref.toString()) ; 
 StrAnswer= StrAnswer.replace("__IsOverVref__",IsOverVref.toString()) ; 
 StrAnswer= StrAnswer.replace("__IsNoVref__",IsNoVref.toString()) ; 
 
 if ( IsDebug == true ) 
 { 
  alert( StrAnswer ) ; 
 }
 
 if ( IsDebug == true ) 
 { 
  if(  IsUnderVref == true  )
  {
   alert( "Voltage reference must be higher than 1.25 volts ." ) ; 
  }
  if( IsOverVref == true )
  {
    alert( "Voltage reference must be lower than 2.0 Volts." ) ; 
  }
 }
 
 if( IsNoVref == true )
 {
  IntVref=1.25 ; 
  if ( IsDebug == true ) 
  {
   alert("Voltage Reference set to default:" + IntVref ) ;  
  }
  
 }
 //VoltageRef.value = IntVref.toString() ; 
 //document.getElementById("vref") .value
 
 $(document).ready(function(){$("tspan#vref").text( IntVref.toString() ) ;}); 
 

}
  
function UpdateFilledAnswer( OriginForm )
{
 /*  var ItemToDisable = document.VoltageLM317.isolation ; */
 var FormHandler = document.forms[OriginForm.name] ; 
 var FieldToDisable = OriginForm[FormHandler.isolation] ; 
 alert( "Field: have change state." + FormHandler  ) ; 
 // +  document.VoltageLM317Interface.ItemToDisable.disabled ) ;
 /*var ArrayListDsbl= new Array(
   document.VoltageLM317Interface.vout,
   document.VoltageLM317Interface.R2 ) ;  */ 
 
}

function UpdateFieldReadOnly( IdElement )
{
 var ElementDef = document.getElementById( UpdateFieldReadOnly.name ) ;
 var StrFormId = DocGetDataAttr( ElementDef, "form" ) ;
 var IsDebug = DocGetDataAttr( ElementDef, "debug" ) ;
 var FormHandler = document.getElementById( StrFormId );
   
 if( IsDebug == "true" )
 {
  alert("Element to set Read-Only: " + IdElement ) ; 
 }
 var JQFindInput = $(FormHandler).find("input:text");
 var ElmROResult ; 
   
 if( IsDebug == "true" )
 { 
  alert("Number of field within form having input:text :" 
  + JQFindInput.length ) ;
 }
   
 for( IntX=0 ; IntX <= JQFindInput.length-1; IntX++ )
 {
  ElmROResult=$("#"+JQFindInput[IntX].id).attr("readonly") ;

  if( IsDebug == "true" )
  { 
   alert("Processing ID from type=text " + JQFindInput[IntX].id ) ;
  }
    /*alert("Status of id: " + JQFindInput[IntX].id + ":" + ROResult ) ;*/
    
    /*alert("Inspection of ID:" + JQFindInput[IntX].id ) ; */
  if( JQFindInput[IntX].id == IdElement 
      & ElmROResult != "readonly" )
  {
   if( IsDebug == "true" )
   { 
    alert("ID: " + JQFindInput[IntX].id 
    + " is about to become readonly" ) ;
   }
   $("#"+JQFindInput[IntX].id).attr("readonly","");
  }
  if( JQFindInput[IntX].id != IdElement 
      & ElmROResult == "readonly" )
  { 
   if( IsDebug == "true" )
   { 
    alert("ID: " + JQFindInput[IntX].id 
    + " is about to become active" ) ;
   }
       
   $("#"+JQFindInput[IntX].id).removeAttr('readonly') ;
  }
     
 }
}
  
function AddIdtoTag(Tag, StartIdName)
{
 var TagList = document.getElementsByTagName( Tag );
 var StrContent="" ;
 var IntId ; 
 for(x=0; x <= TagList.length-1; x++ )
 {
   StrContent=StartIdName + IntId ; 
   TagList[x].setAttribute("id" , StrContent ) ;
 }
}
  
