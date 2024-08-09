<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Unter&ouml;d Gew&auml;chshaus</title>
<!-- gwxhaus GUI test -->

<link rel="stylesheet" href="styles.css">
 
<script type="text/javascript" src="js/tools.js"></script>
<script type="text/javascript" src="js/timer.js"></script>
<script type="text/javascript" src="js/gAjax.js"></script>

<script type="text/javascript">
  //defaults
  var m_timerButton = 1;
  var m_reloadTime = 900;
  var m_reloadTimeSens = 2000;
  var vIntervalId=0;
  var vIntervalId2=0;
  
  //data stuff
  var m_ioGetGwxSens = "getGwxSensors.php";
  var m_ioGetWifiController = "getWifiController.php";
  var m_ioGetvsupplyhdl = "getVSupply.php";
  
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
      
  function iohdlSens(text){
      if(!iohdlSens.state) iohdlSens.state =0;
      iohdlSens.state = 1-iohdlSens.state;
      if(text=="" || text.includes("<title>504 ")) {
          oFileioSens.load(m_ioGetGwxSens); 
          return;
      }
      try{
          lines = text.split(";");
          lines.forEach( line => 
          //for each(var line in lines)
          {
            text= trim(line);
            //if(text == "") continue;
     
            if(text.includes(":")) {
                var s=text.split(":")
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
                if(k=="Spannung") {
                    var s = parseFloat(val.split("=")[1]);
                    write2Id("cusb", val);
                    if(s<4.5) write2Id("cusb2", " !Spannung zu gering. Defekt, oder Stromausfall!")                
                 }
                if(k=="ts") write2Id("ts", val+":"+s[2]+":"+s[3] );
            }
            if(text.includes("Batt=")) {
                var v = text.split("=")[1];
                //add2Id("log",v);
                var v2 = parseFloat(v);
                var p = Math.round(v2/4.5*100);
                if(v2 >3.5) 
                    write2Id("cbat", "Backupbatterie ok.");
                else {
                    if(p <20) write2Id("cbat", "Backupbatterie unter 20% ! ");
                    else write2Id("cbat", "Backupbatterie wird entladen. ");
                    add2Id("cbat", ""+p);
                }
                //add2Id("log",v2);
            }
          }  );
      }catch (error) {
          console.error(error);  
      }
      oFileioSens.load(m_ioGetGwxSens); 
  }//--------------------------------------------      
      
  function wifihdl(text){
      if(!wifihdl.state) wifihdl.state =0;
      wifihdl.state = 1-wifihdl.state;
      if(wifihdl.state) write2Id("hbc", " /"); else write2Id("hbc", " \\");
      //write2Id("wifictrl", text);
      if(text=="" || text.includes("<title>504 ")) {
          //no valid data - init next data callback
          oFileioWifiCtrl.load(m_ioGetWifiController); 
          return;
      }
      try {
          var jsn = JSON.parse(text);
          //add2Id("hbc", jsn.DHT11);
          v = jsn.DHT11.Temperature;
          if(v==null) v="?"; else v=v.toFixed(1);
          write2Id("dht11T", v);
          write2Id("dht11H", jsn.DHT11.Humidity);
          v = jsn.DHT11.DewPoint;
          if(v==null) v="?"; else v=v.toFixed(1);
          write2Id("dht11D", v);
          write2Id("ct", jsn.ESP32.Temperature.toFixed(1));
          write2Id("cts", jsn.Time);
          write2Id("wifictrl", "Warte auf neue Daten...");
      } catch (error) {
          console.error(error);  
          write2Id("wifictrl", "dauert länger...");
      }
      oFileioWifiCtrl.load(m_ioGetWifiController); 
  }//--------------------------------------------     
  

      
  function vsupplyhdl(text){
      if(!vsupplyhdl.state) vsupplyhdl.state =0;
      vsupplyhdl.state = 1-vsupplyhdl.state;
      //if(vsupplyhdl.state) write2Id("hbc", " /"); else write2Id("hbc", " \\");
      //add2Id("log", text);
      if(text=="" || text.includes("<title>504 ")) {
          //no valid data - init next data callback
          oFileiovsupplyhdl.load(m_ioGetvsupplyhdl); 
          return;
      }
      try {
          var jsn = JSON.parse(text);

          v = jsn.ANALOG.A1;
          if(v==null) v="?"; else v=(v/10).toFixed(1);
          write2Id("L1", v);
          v = jsn.ANALOG.A1;
          if(v==null) v="?"; else v=(v/10).toFixed(1);
          write2Id("L2", v);
          v = jsn.ANALOG.A1;
          if(v==null) v="?"; else v=(v/10).toFixed(1);
          write2Id("L3", v);
        
          write2Id("Lct", jsn.ESP32.Temperature.toFixed(1));
          write2Id("Lts", jsn.Time);
          write2Id("VSupply", "Warte auf neue Daten...");
      } catch (error) {
          console.error(error);  
          write2Id("VSupply", "dauert länger...");
      }
      oFileiovsupplyhdl.load(m_ioGetvsupplyhdl); 
  }//--------------------------------------------     
  

  function wasseraus(){
      write2Id("hbs","wasser aus!");
  }
  function wasseran(minuten){
      write2Id("hbs","wasser an fuer "+minuten+" min.");
  }
</script>
</head>    

<body onload="startAjax(); ">
    
<h1>Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.4.0
<hr>

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
<h3>Wasser Haus1</h3>
Ventile noch nicht angeschlossen
<s><table><tr class="strikeout"><td>Status Wasser: </td><td id="w1">-</td></tr><br></table></s>
Das sind nur Demo Buttons, die sind im Moment noch nicht an die Elektrik angeschlossen.<br>
<button onclick="wasseraus()" name="butTimer">Wasser aus</button> 
<button onclick="wasseran(15)" >Wasser an 15min</button>
<button onclick="wasseran(120)">Wasser an 2h</button> 
<h3>Wasser Haus2</h3>
Ventile noch nicht angeschlossen
<s><table><tr class="strikeout"><td>Status Wasser: </td><td id="w2">-</td></tr><br></table></s>
Das sind nur Demo Buttons, die sind im Moment noch nicht an die Elektrik angeschlossen.<br>
<button onclick="wasseraus()" name="butTimer">Wasser aus</button><br>
<button onclick="wasseran(15)" >Wasser an 15min</button><br>
<button onclick="wasseran(120)">Wasser an 2h</button><br>
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
<tr><td>Letztes Lebenszeichen um:</td><td id="cts">-</td></tr>
</table>
<hr>
<h3>Stromversorgung</h3>
<h4>Verteilerkasten Links</h4>
<table>
<tr><td>L1</td><td>L2</td><td>L3</td><td>Einheit</td><tr>
<tr><td id="L1">-</td><td id="L2">-</td><td id="L3">-</td><td>Volt</td><tr>
</table><table>    
<tr><td>Controllertemperatur: </td><td id="Lct">-</td><td>°C</td></tr>    
<tr><td>Letztes Lebenszeichen um:</td><td id="Lts">-</td></tr>
</table>
<h4>Controller-wifi-Schaltkasten</h4>
<pre id="hbc">Lade Daten...</pre>
<div id="wifictrl">-</div>
<table>
<tr><td>Controllertemperatur: </td><td id="ct">-</td><td>°C</td></tr>
<tr><td>Batterieladung: </td><td id="cbat">-</td><td>%</td></tr>
<tr><td>Spannung: </td><td id="cusb">-</td><td id="cusb2"></td></tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="cts">-</td></tr>
</table>
<hr><hr>
<pre id="log">-</pre>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

