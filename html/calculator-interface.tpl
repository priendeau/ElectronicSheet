<style>
.BorderStyle * { 
    display: initial;
    margin: 5px;
    margin-top: 5px;
    margin-bottom: 5px ;
    border: 2px solid lightgrey;
    padding: 30px;
    color: white; 
}
.BorderStyleEmpty * { 
    display: block;
    border: 2px solid lightgrey;
    color: white;
    padding: 25px;
    margin: 15px;
    align: center; 
}

.TableBorder {
    border: 2px solid purple;
    background-color: lightgrey ; 
    top: 1px ;
    bottom: 1px;
    display: block;
    background-color: white;
    padding: 5px;
    margin: 5px;
    align: center; 
    
}
</style>

<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<script type="text/javascript" src="https://raw.githubusercontent.com/svgdotjs/svg.js/master/dist/svg.min.js"></script>
<script type="text/javascript" src="file:///home/maxiste/bin/html/js/LM317Formula-Handler.js" ></script>



  <div id="content" class="site-content" role="main">
   <h1 class="entry-title-h1"> Electronic Sheet, Common Electronic part calculation sheet.</h1>
   <div class="entry-inner">
    <h2 class="entry-title-h2">LM3xx Voltage Calculator</h2>
    <div class="entry-content">
     <p>The <a href="pdf1.alldatasheet.com/datasheet-pdf/view/11662/ONSEMI/LM317/+01574UllREMIcxRYtE+/datasheet.pdf"><b>LM317</b></a> (LM317T), and high current <a href="www.ti.com/lit/ds/symlink/lm338.pdf"><b>LM338</b></a> (LM338T) are <b>voltage regulators</b> which can take an input voltage of 3-40 Volts DC, and output a fixed output voltage from 1.2 to 37 Volts DC.</p>
     <div align="center">
     <table cellpadding="5" border="0">
      <tbody>
       <tr>
       <td><img src="file:///home/maxiste/bin/html/images/labelled-lm317t-pinout.jpg" alt="Labelled pinout for LM317T voltage regulator"></td>
       <td><img src="file:///home/maxiste/bin/html/images/lm317t-voltage-regulation-circuit.gif" alt="LM317T Voltage Calculator" width="228" height="202"></td>
       </tr>
      </tbody>
     </table>
     </div> <!-- div-align-center -->
     <p>The output <b>voltage</b> from the LM317 and LM338 is set using two <a href="http://www.reuk.co.uk/Resistor-Colour-Codes.htm">resistor</a> (R1 and R2)</p> 
     <p>with theirs respective calues chosen according to the following notes from datasheet.</p>
     <br/>
     <p>The LM317 is a 3-terminal floating floating regulator. In operation, The LM317 develops and maintains a nominal 1.25V(*1) reference (Vref) between it's output and adjustement terminal. This reference volttage is converted to a programming current (IPROG) by R1 (see Figure 17), and this constant current flows through ground. The regulated output voltage is given by this equation:</p>
     <table align="center">
      <tbody >
       <tr>
       </tr>
       <tr>
       <div class="TableBorder">
       <!-- <td style="text-align: center;"><img src="file:///home/maxiste/Pictures/Electronic/LM317-voltage-formulas.png"></td> -->
       <svg id='VectorFormula' name='LM317TVoltage' width="410" height="130" onload="UpdateVref();" debug="false" >
       <text x="20" y="45" transform="" style="font-style:normal;font-weight:normal;font-size:24.15px;line-height:25px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" >V</text>
       <text x="35" y="50" transform=""  style="font-style:normal;font-weight:normal;font-size:14.11px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">out
       <tspan x="285" y="50" style="font-style:normal;font-weight:normal;font-size:14.11px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:-50%;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">Adj</tspan>
       <tspan x="320" y="50">2</tspan>
       </text>

       <text x="65" y="45" transform="" style="font-style:normal;font-weight:normal;font-size:14.11px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
       <tspan x="65" y="45" >=</tspan>
       <tspan x="85" y="45" id="vref" name="VoltageRef" >0.00</tspan>
       <tspan x="120" y="45">V</tspan>
       <tspan x="135" y="45">x</tspan>
       <tspan x="260" y="45">+</tspan>
       <tspan x="280" y="45" id='Intensity' name='Intensity' >I</tspan>
       <tspan x="310" y="45" id='RSecondIntensity' name='R2Intensity' >R</tspan>
       </text>
       <text x="75" y="12" transform="scale(2,5)" style="font-style:normal;font-weight:normal;font-size:10px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
       <tspan x="75" y="12" >(</tspan>
       <tspan x="125" y="12">)</tspan>
       </text>
       <text x="170" y="46" transform="" style="font-style:normal;font-weight:normal;font-size:20px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">1 +</text>
       <line x1="215" y1="40" x2="240" y2="40" style="stroke:rgb(0,0,0);stroke-width:2" />
       <text x="170" y="46" transform="" style="font-style:normal;font-weight:normal;font-size:20px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
       <tspan x="220" y="34" id='RFirst' name='R1'>R</tspan>
       <tspan x="220" y="60" id='RSecond' name='R2'>R</tspan>
       </text>
       <text x="170" y="46" transform="" style="font-style:bold;font-weight:normal;font-size:12px;line-height:6.61458302px;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
       <tspan x="238" y="38">1</tspan>
       <tspan x="238" y="64">2</tspan>
       </text>
       <rect x="80" y="12" rx="9" ry="20" width="180" height="85"
        style="fill:#d95326;stroke:black;stroke-width:3;opacity:0.2" />
       <text x="90" y="86" fill="#646464" font-size="14" font-family="Verdana" >Voltage Section</text>
       <rect x="270" y="1" rx="9" ry="20" width="125" height="75"
        style="fill:#3e8e3e;stroke:black;stroke-width:3;opacity:0.2" />
       <text x="280" y="20" fill="#646464" font-size="14" font-family="Verdana" >Current Section</text>

       </svg>
       </div>
       </tr>
      </tbody>
     </table>
      <h2>The LM317/LM338 Voltage Calculator</h2></font></td></tr></tbody></table></form><p></p>
      <form action="file:///home/maxiste/bin/html/calculator-interface.html" name="VoltageLM317">
      <table width="450" align="center">
       <tbody>
        <tr>
         <td valign="top">Vout: <input size="4" name="vout" value="6.00"><br>
          <font color="red" size="1">Target Output Voltage<br><b>1.5 to 37.0 Volts</b>
          </font>
         </td>
         <td valign="top">Vref: <input size="4" name="vref" value="1.25"><br>
          <font color="green" size="1">Nominal voltage<br><b>1.25 and lower than 2.0 volts</b>
          </font>
         </td>
         <td valign="top">R1: <input size="4" name="R1" value="240"><br>
          <font color="red" size="1">R1 Resistor Value<br><b>0.1 Ohms to 2k Ohms</b></font>
         </td>
         <td valign="top">R2: <input size="4" name="R2" value="" readonly="">
          <input value="Calculate" onclick="lm317voltage()" type="button">
          <br>
          <font color="green" size="1"><b>Click</b> <i>Calculate</i> to display the<br>calculated <b>R2</b> value here.</font>
         </td>
        </tr>
       </tbody>
      </table>
      </form>
      <div align="justify">
       <p>The results given above can be used to put together a <b>voltage regulator</b>, but the calculated value of <i>R2</i> will not be a standard/stock resistor value. Since the accuracy of the voltage regulator itself will be up to 5% out, and resistor values are not exact, it is common to use a <b>Potentiometer</b> (aka <i>variable resistor</i> or <i>trim pot</i>) for some or all of <i>R2</i>. This enables the output voltage to be manually fine-tuned to provide the exact voltage required.</p>
      </div>
      <br>Enter values of R1 and R2 below to calculate the corresponding value of <i>Vout</i>.
      <br>
      <br>
      <form action="file:///home/maxiste/bin/html/calculator-interface.html" name="CurrentLM317">
       <table width="450" align="center">
        <tbody>
         <tr>
           <td valign="top">R1: <input size="4" name="R1b" value="330">
            <br>
            <font color="red" size="1">R1 Resistor Value
            <br><b>0.1 Ohms to 2k Ohms</b>
            </font>
           </td>
           <td valign="top">R2: <input size="4" name="R2b" value="2000">
            <br>
            <font color="red" size="1">R2 Resistor Value</font>
           </td>
           <td valign="top">Vout: <input size="4" name="voutb" value="" readonly=""> 
            <input value="Calculate" onclick="lm317voltageFromResitor()" type="button">
            <br>
            <font color="green" size="1"><b>Click</b> <i>Calculate</i> to display the<br>calculated <b>Vout</b> value here.
            </font>
           </td>
          </tr>
         </tbody>
       </table>
      </form>     
     
      <div>Below is our automated <b>voltage calculator</b> for the LM317 and LM338 regulators.Simply enter your target output voltage V<sub>out</sub> and chosen value for R1 (0.1 to 2k Ohms). click Calculate and the required value of R2 will be displayed</div>
     <p>Where an accurate voltage might be required, it is much easier to use standard (stock) resistors to put together an <b>LM317 or LM338 voltage regulator</b>. Below are tables of output voltages for different combinations of the most commonly found resistors.</p>
     <h3>LM317/LM338 Current Calculator</h3>
     <p>If you would like to use the <b>LM317T</b> or <b>LM338T</b> to output a fixed current rather than voltage, click here to visit our <a href="http://www.reuk.co.uk/LM317-Current-Calculator.htm"><b>LM317 Current Calculator</b></a>.</p>
     <p><span class="newt">NEW</span> For voltage regulators required to output more than 1.5A, click here to view <a href="http://www.reuk.co.uk/LM317-High-Current-Voltage-Regulator.htm"><b>LM317T High Current Voltage Regulator</b></a> for more information and a circuit plan.</p>
     <form action="http://www.reuk.co.uk/LM317-Current-Calculator.htm" name="CurrentLM317">
      <h2>LM317/LM338 Current Calculator</h2>
      <div align="justify"><p>Below is our automated <b>current calculator</b> for the LM317 and LM338 linear voltage regulators. Simply enter your desired output current (measured in milliamps), and the value of the required resistor and its power rating will be displayed:</p></div>
      <br>
      <br>
      <div align="justify">Target Output <b>Current</b> <input size="5" name="current" value="25"> milliamps <input value="Calculate" onclick="lm317current()" type="Button"><br><b>Resistor</b> Value: <input name="ohms" size="4" value="" readonly=""> Ohms with a <b>power rating</b> greater than: <input name="power" size="4" value="" readonly=""> Watts</div></form>
   </div><!-- .entry-content -->
  </div><!-- entry-inner -->
 </div><!-- id-content" class-site-content" role-main" -->
