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
  alert("Voltage Reference set to default:" + IntVref ) ;  
 }
 //VoltageRef.value = IntVref.toString() ; 
 //document.getElementById("vref") .value
 
 $(document).ready(function(){$("tspan#vref").text( IntVref.toString() ) ;}); 
 

}
