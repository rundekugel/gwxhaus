<!DOCTYPE html>
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Technik Unter&ouml;d Gew&auml;chshaus</title>
<!-- gwxhaus GUI test -->

<link rel="stylesheet" href="styles.css">
 
<script type="text/javascript" src="js/tools.js"></script>
<script type="text/javascript" src="js/timer.js"></script>
<script type="text/javascript" src="js/gAjax.js"></script>

<script type="text/javascript">
  //defaults
  var m_timerButton = 1;
  var m_reloadTime = 950;
  var vIntervalId=0;
  
  //data stuff
  var m_ioGetGwxSens = "s2.php";
  var m_ioGetWifiController = "w2.php";
  var m_ioGetvsupplyhdl = "v1.php";
  
  //cFileContent is the ajax callback
  oFileioSens = new cFileContent(iohdlSens);
  oFileioWifiCtrl = new cFileContent(wifihdl);
  oFileiovsupplyhdl = new cFileContent(vsupplyhdl);
  //--------------------------------------------
    

  function startAjax(){
    oFileioSens.load(m_ioGetGwxSens); 
    oFileioWifiCtrl.load(m_ioGetWifiController);
    oFileiovsupplyhdl.load(m_ioGetvsupplyhdl);
  }

  function timer1(){
    startAjax();
  }

  function timer1An() {
      startAjax();
      vIntervalId = setInterval ( "timer1()", m_reloadTime );
  }//-------------------
            
  function iohdlSens(text){
      //add2Id("log", "s:"+text);
      //write2Id("log", "s:"+text);

      if(text=="" || text.includes("<title>504 ")) {
          return;
      }

      try{
          lines = text.split(";");
          lines.forEach( line => 
          {
            line = line.replaceAll( '"', "", line);
            line = line.replace( '\\r\\n}', "", line);
            line = line.replace( "{SSerialReceived:", "", line);
            line= trim(line);
            //if(line == "") continue;
            add2Id("log", " -l:"+line);
            if(line.includes(":")) {
                var s=line.split(":")
                var k=s[0].trim();
                var val=s[1].trim();
                if(k=="sp") {
                    write2Id("wind", Math.round(val*10)/10);
                    write2Id("wkmh", Math.round(val*36)/10);
                }
                if(k=="th1") write2Id("th1", val+s[2]+s[3]);
                if(k=="th2") write2Id("th2", val+s[2]+s[3]);
                if(k.includes("asser")) {
                    var ww = val.split(",")
                    write2Id("w1", ww[0]);
                    write2Id("w2", s[2]);
                }
                if(k.includes("otor")) {
                    var ww = val.split(",")
                    write2Id("m1", ww[0]);
                    write2Id("m2", s[2]);
                }
                if(k=="USB=") {
                    var s = parseFloat(val.split("=")[1]);
                    write2Id("cusb", val);
                    write2Id("cusb2", "ok");
                    if(s<4.5) write2Id("cusb2", " !Spannung zu gering. Defekt, oder Stromausfall!")                
                 }
                if(k=="ts") write2Id("ts", val+":"+s[2]+":"+s[3] );
            }
            if(line.includes("Bat.=")) {
                var v = line.split("=")[1];
                //add2Id("log",v);
                var v2 = parseFloat(v);
                var p = Math.round(v2/4.5*100);
                write2Id("cbat", v2);
                add2Id("cbat", "("+p+"%)");

                //add2Id("log",v2);

            if(line.includes("USB=")) {
                var s = parseFloat(line.split("=")[1]);
                write2Id("cusb", line);
                if(s<4.5) write2Id("cusb2", " !Spannung zu gering. Defekt, oder Stromausfall!")                
             }                
            }
          }  );
      }catch (error) {
          console.error(error);  
      }
      //oFileioSens.load(m_ioGetGwxSens); 
  }//--------------------------------------------      
      
  function wifihdl(text){
      write2Id("wifictrl", text);
      add2Id("log", text);
      if(text=="" || text.includes("<title>504 ")) {
          //no valid data - init next data callback
          //oFileioWifiCtrl.load(m_ioGetWifiController); 
          return;
      }
      try {
          var jsn = JSON.parse(text);
          add2Id("log", text);
          write2Id("ct", jsn.ESP32.Temperature.toFixed(1));
          write2Id("cts", jsn.Time);  
          write2Id("ctsa", jsn.Time);    
          v = jsn.DHT11.Temperature;
          if(v==null) v="?"; else v=v.toFixed(1);
          write2Id("dht11T", v);
          write2Id("dht11H", jsn.DHT11.Humidity);
          v = jsn.DHT11.DewPoint;
          if(v==null) v="?"; else v=v.toFixed(1);
          write2Id("dht11D", v);
          write2Id("wifictrl", "Warte auf neue Daten...");
      } catch (error) {
          console.error(error);  
          write2Id("wifictrl", "dauert länger...");
      }
      //oFileioWifiCtrl.load(m_ioGetWifiController); 
  }//--------------------------------------------     
  
  function vsupplyhdl(text){
      add2Id("log", text);
      
      if(text=="" || text.includes("<title>504 ")) {
          return;
      }
      try {
          var jsn = JSON.parse(text);
          var vdiv = 10.86
          v = jsn.ANALOG.A1;
          if(v==null) v="?"; else v=(v/vdiv).toFixed(2);
          write2Id("L1", v);
          v = jsn.ANALOG.A2;
          if(v==null) v="?"; else v=(v/vdiv).toFixed(2);
          write2Id("L2", v);
          v = jsn.ANALOG.A3;
          if(v==null) v="?"; else v=(v/vdiv).toFixed(2);
          write2Id("L3", v);
        
          write2Id("Lct", jsn.ESP32.Temperature.toFixed(1));
          write2Id("Lts", jsn.Time);
          //write2Id("VSupply", "Warte auf neue Daten...");
      } catch (error) {
          console.error(error);  
          //write2Id("VSupply", "dauert länger...");
      }
  }//--------------------------------------------     
  

  function wasseraus(){
      write2Id("hbs","wasser aus!");
  }
  function wasseran(minuten){
      write2Id("hbs","wasser an fuer "+minuten+" min.");
  }
</script>
</head>    

<body onload="timer1An(); ">
    
<h1>Technik Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.1.2
<hr>
<a href="gwxhaus.php">Einfache Ansicht</a>
<h3>Gew&auml;chshaus Sensoren</h3>
<pre id="hbs">Lade Daten...</pre>
<table>
<tr><td>Wind: </td><td id="wind">-</td><td>m/s =</td><td id="wkmh">-</td><td>km/h</td></tr></tr>
<tr><td>Haus1: </td><td id="th1">-</td><td> %rel.</td></tr>
<tr><td>Haus2: </td><td id="th2">-</td><td> %rel.</td></tr>

<!--
Heartbeat: [<textbox id="hb">.</textbox>] <br>
-->
<tr><td>Letzte Nachricht: </td><td id="ts">-</td></tr>
</table>
<hr>
<h3>Wasser</h3>
Ventile noch nicht angeschlossen

<s><table><tr class="strikeout"><td>Status Wasser1: </td><td id="w1">-</td></tr><br></table></s>
<s><table><tr class="strikeout"><td>Status Wasser2: </td><td id="w2">-</td></tr><br></table></s>

<hr>
<h3>Motoren</h3>
<!--table><tr class="strikeout"><td>Motor1: </td><td id="m1">-</td></tr><br></table></s>
<table><tr class="strikeout"><td>Motor2: </td><td id="m2">-</td></tr><br></table></s>
-->
<hr>
<h3>Bodenfeuchte</h3>
Haus1: ??% &nbsp;&nbsp;&nbsp;&nbsp; Haus2: ??%
<h2>Fenster Status</h2>
Haus1: ?.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Haus2: ?
<hr>

<h3>Controller</h3>
<table>
<tr class="strikeout"><td>Motoren noch nicht angeschlossen Haus1:</td><td id="m1">-</td><td><s>Haus2:</td><td id="m2">-</td></tr>
</table>
<hr>

<h3>Sensor im Sicherungskasten </h3>
<pre id="hbc">Lade Daten...</pre>
<div id="wifictrl">-</div>
<table>
<tr><td>Aussensensor: </td><td id="dht11T">-</td><td>°C / Feuchte: <td id="dht11H">-</td><td>%rel. / Taupunkt: </td><td id="dht11D">-</td><td>°C</td><tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="ctsa">-</td></tr>
</table>
<hr>
<h3>Stromversorgung</h3>
<h4>Verteilerkasten Links</h4>
<table>
<tr><td>L1</td><td>L2</td><td>L3</td><td>Einheit</td><tr>
<tr class="strikeout"><td id="L1">-</td><td id="L2">-</td><td id="L3">-</td><td>Volt</td><tr>
</table><table>    
<tr class="strikeout"><td>Controllertemperatur: </td><td id="Lct">-</td><td>°C</td></tr>    
<tr><td>Letztes Lebenszeichen um:</td><td id="Lts">-</td></tr>
</table>
<h4>Controller-wifi-Schaltkasten</h4>
<pre id="hbc">Lade Daten...</pre>
<div id="wifictrl">-</div>
<table>
<tr><td>Controllertemperatur: </td><td id="ct">-</td><td>°C</td></tr>
<tr><td>Batterieladung: </td><td id="cbat">-</td><td>V</td></tr>
<tr><td>Spannung: </td><td id="cusb">-</td><td id="cusb2"></td></tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="cts">-</td></tr>
</table>
<hr><hr>
<pre id="log">-</pre>
<a href="gwxhaus.php">Einfache Ansicht</a>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

