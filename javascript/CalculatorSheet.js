/*
 * File : CalculatorSheet.js 
 * 
 * 
 * */

function lm317current() 
{
  
  var IntVref = new Number( document.VoltageLM317.vref.value ) ; 
  
  var IntCurrent = new Number( document.CurrentLM317.current.value ) ; 
  var IntOhms = IntVref / (IntCurrent / 1000); 
  var IntPower = IntVref * (IntCurrent / 1000); 
  
  document.CurrentLM317.ohms.value = IntOhms.toFixed(2); 
  document.CurrentLM317.power.value = IntPower.toFixed(4);
}
 
function lm317voltage() 
{
  var IntResistor1 = new Number( document.VoltageLM317.R1.value ); 
  var IntResistor2 = new Number( document.VoltageLM317.R2.value ); 
  var IntVoltageOut = new Number( document.VoltageLM317.vout.value ); 
  var IntVref = new Number( document.VoltageLM317.vref.value ); 
  var IntVolTageOut ;  
  IntVolTageOut = IntVref * ( 1 + ( IntResistor1 / IntResistor2 ) + ) 
  // Z = IntResistor1 * (( IntVoltageOut / vref ) - 1) ; 
  
  document.VoltageLM317.R2.value = IntVolTageOut.toFixed(4) ;
 }

function lm317voltageFromResitor() 
{
  var IntResistor1 = new Number( document.VoltageLM317.R1.value ); 
  var IntResistor2 = new Number( document.VoltageLM317.R2.value ); 
  var IntVref = new Number( document.VoltageLM317.vref.value ); 
  var IntVoltageOut ;  
  var temp = IntVref * (1 + ( IntResistor2 / IntResistor1 )); 
  Z = temp.toFixed(2); 
  document.Calc.voutb.value = Z;	
  
}

