<?php session_start(); ?>
<!DOCTYPE html>
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
            line = line.replace( '}', "", line);
            line = line.replace( "{SSerialReceived:", "", line);
            line= trim(line);
            //if(line == "") continue;
     
            if(line.includes(":")) {
                var s=line.split(":")
                var k=s[0].trim();
                var val=s[1].trim();
                if(k=="sp") {
                    write2Id("wind", Math.round(val*10)/10);
                    add2Id("wind", " m/s = "+Math.round(val*36)/10+" km/h");
                    if(val > 9) {
                        write2Id("windtext", "Sturm");
                    }else{
                        write2Id("windtext", "Ruhig");
                    }
                }
                if(k=="Sturm") add2Id("windtext", ". Sturm-modus! Wert:"+val);
                if(k=="T1") write2Id("T1", val+" &deg;C");
                if(k=="T2") write2Id("T2", val+" &deg;C");
                if(k=="H1") write2Id("H1", val+" %rel.");
                if(k=="H2") write2Id("H2", val+" %rel.");
                
                if(k=="W1") write2Id("w1", val);
                if(k=="W2") write2Id("w2", val);
                if(k=="W3") write2Id("w3", val);
                if(k=="W4") write2Id("w4", val);
                
                if(line.includes(", W2:")) {
                    // old: "W1:Zu, W2:Zu; "
                    var ww = val.split(",")
                    write2Id("w1", ww[0]);
                    write2Id("w2", s[2]);
                }
                if(k=="M1") write2Id("md1", val);
                if(k=="M2") write2Id("md2", val);
                //Fenster
                if(k=="F1") write2Id("fen1", val+" %");
                if(k=="F2") write2Id("fen2", val+" %");
                if(k=="mn") {
                    if(val==0) write2Id("manu", "");
                    else {
                        var rest = ""
                        val = parseInt(val)
                        if(val > 3600) {
                            h= parseInt(val/3600);
                            rest = h+" Stunden, ";
                            val -= h*3600;
                        }
                        if(val >60) {
                            m = parseInt(val/60);
                            rest += m +" Minuten, ";
                            val -= m*60;
                        }
                        rest += val+" Sekunden";
                        write2Id("manu",
                        "<hr><h2 style=color:red;>Manueller Modus aktiv!</h2>Restdauer: "
                        +rest);
                    }
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
                if(v2 >3.5) 
                    write2Id("cbat", "Backupbatterie ok.");
                else {
                    if(p <20) write2Id("cbat", "Backupbatterie unter 20% ! ");
                    else write2Id("cbat", "Backupbatterie wird entladen. ");
                    add2Id("cbat", ""+p);
                }
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
  }//--------------------------------------------      
      
  function wifihdl(text){
      write2Id("wifictrl", text);
      //write2Id("log", text);
      if(text=="" || text.includes("<title>504 ")) {
          return;
      }
      try {
          var jsn = JSON.parse(text);
          //add2Id("hbc", jsn.DHT11);
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
  }//--------------------------------------------     
  
  function vsupplyhdl(text){
      //add2Id("log", text);
      if(text=="" || text.includes("<title>504 ")) {
          return;
      }
      try {
          var Vmin = 200;
          var jsn = JSON.parse(text);
          var vdiv = 10.86
          var v1 = jsn.ANALOG.A1;
          if(v1 == null) return;
          v1=(v1/vdiv).toFixed(1);
          var v2 = jsn.ANALOG.A2;
          if(v2 == null) return;
          v2=(v2/vdiv).toFixed(1);
          var v3 = jsn.ANALOG.A3;
          if(v3 == null) return;
          v3=(v3/vdiv).toFixed(1);
          var err = 0;
          write2Id("vert1", "");
          if(v1 < Vmin) {
              err++;  
              add2Id("vert1","L1 Unterspannung! ");
          }
          if(v2 < Vmin) {
              err++;  
              add2Id("vert1","L2 Unterspannung! ");
          }
          if(v3 < Vmin) {
              err++;  
              add2Id("vert1","L3 Unterspannung! ");
          }
          if(err==0) { 
              add2Id("vert1","OK.");
          }else{
               add2Id("vert1", err + " Fehler!");
           }
          
          write2Id("Lct", jsn.ESP32.Temperature.toFixed(1));
          write2Id("Lts", jsn.Time);
          //write2Id("VSupply", "Warte auf neue Daten...");
      } catch (error) {
          console.error(error);  
          //write2Id("VSupply", "dauert länger...");
      }
  }//--------------------------------------------     
  

  function wasseraus(id){
      fetch("switcher.php?w"+id+"=0");
      write2Id("hbs","wasser aus!");
  }
  function wasseran(id,minuten){
      fetch("switcher.php?w"+id+"="+minuten);
      write2Id("hbs","wasser an fuer "+minuten+" min.");
  }
  function motor(id,richtung){
      fetch("switcher.php?m"+id+"="+richtung);
      write2Id("motinfo","Motor "+id+"="+richtung);
  }
  function switcher(text){
      fetch("switcher.php?"+text);
  }  
  //------------------------------
</script>
</head>    

<body onload="timer1An(); ">
    
<h1>Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Version 0.6.3 (unvollendet)
<?php
if(isset($_SESSION["user"])) {
  echo "<hr>Angemeldet als: ".$_SESSION["user"];
  echo " &nbsp;&nbsp;<a href='logout.php'><button>Logout</button></a>";
  echo ' &nbsp;&nbsp;<button onclick=switcher("manually=60")>Manuell 1min</button></a>';
  echo ' &nbsp;&nbsp;<button onclick=switcher("manually=0")>Manuell off</button></a>';
}
?>
<div id="manu"></div>
<hr>

<h3 id="gwxsensoren">Gew&auml;chshaus Sensoren</h3>
<pre id="hbs">Lade Daten...</pre>
<table>
<tr><td>Wind: </td><td id="wind">-</td><td id="windtext">Still</td></tr></tr>
<tr><td>Haus1: </td><td id="T1">-</td><td id="H1">-</td></tr>
<tr><td>Haus2: </td><td id="T2">-</td><td id="H2">-</td></tr>

<!--
Heartbeat: [<textbox id="hb">.</textbox>] <br>
-->
<tr><td>Letzte Nachricht: </td><td id="ts">-</td></tr>
</table>
<hr>
<h3 id="wasser">Wasser</h3>
<h4>Wasser Haus 1</h4>
<table><tr><td>A:</td><td id="w1">-</td><td>B:</td><td id="w3">-</td></tr></table>
<?php
if(isset($_SESSION["user"])) {
    echo '
<button onclick="wasseraus(1)" name="butTimer">Wasser aus</button> &nbsp;
<button onclick="wasseran(1,1)" >Wasser an</button>&nbsp;
<button onclick="wasseran(1,15)" ><s>Wasser an 15min</button>&nbsp;
<button onclick="wasseran(1,120)">Wasser an 2h</s></button> 
';
}
?>
<h4>Wasser Haus2</h4>
<table><tr><td>A:</td><td id="w2">-</td><td>B:</td><td id="w4">-</td></tr></table>
<?php if(isset($_SESSION["user"])) { echo '
<button onclick="wasseraus(2)" name="butTimer">Wasser aus</button>&nbsp;
<button onclick="wasseran(2,1)" >Wasser an</button>&nbsp
<button onclick="wasseran(2,15)" ><s>Wasser an 15min</button>&nbsp;
<button onclick="wasseran(2,120)">Wasser an 2h</s></button>
';}?>
<h4 id="zisterne">Wasserstand Zisterne</h4>
<table><tr><td>Zisterne</td><td id="zistm">?</td><td>m =</td><td id="zistl">?</td><td>Liter</td></tr></table>
<hr>

<h3 id="bodenfeuchte">Bodenfeuchte</h3>
Haus1: ??% &nbsp;&nbsp;&nbsp;&nbsp; Haus2: ??%

<h2>Fenster Status</h2>
<table><tr><td>Haus1:</td><td id="fen1">-</td><td>Haus2:</td><td id="fen2">-</td></tr></table> 
<hr>

<h3 id="controller">Controller</h3>
<pre id="motinfo"></pre>
<table>
<tr><td>Haus1:</td><td id="md1">-</td><td>Haus2:</td><td id="md2">-</td></tr>
</table>
<?php if(isset($_SESSION["user"])) { echo '
Haus1 Fenster: <button onclick="motor(1,\'u\')" >Auf</button> &nbsp;
<button onclick="motor(1,\'0\')" >Stop</button> &nbsp;
<button onclick="motor(1,\'d\')" >Zu</button> &nbsp;
<br><br>
Haus2 Fenster: <button onclick="motor(2,\'u\')" >Auf</button> &nbsp;
<button onclick="motor(2,\'0\')" >Stop</button> &nbsp;
<button onclick="motor(2,\'d\')" >Zu</button></s> &nbsp;<br>
';}?>
</s>
<hr>

<h3 id="">Sensor im Sicherungskasten </h3>
<pre id="hbc">Lade Daten...</pre>
<div id="wifictrl">-</div>
<table>
<tr><td>Aussensensor: </td><td id="dht11T">-</td><td>°C / Feuchte: <td id="dht11H">-</td><td>%rel. / Taupunkt: </td><td id="dht11D">-</td><td>°C</td><tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="ctsa">-</td></tr>
</table>
<hr>
<h3 id="strom">Stromversorgung</h3>
<h4>Verteilerkasten Links</h4>
<table>
<tr><td>Stromversorgung:</td><td id="vert1">-</td></tr>    
<tr><td>Controllertemperatur: </td><td id="Lct">-</td><td>°C</td></tr>    
<tr><td>Letztes Lebenszeichen um:</td><td id="Lts">-</td></tr>
</table>
<h4 id="gwxcontroller">Controller-wifi-Schaltkasten</h4>
<pre id="hbc">Lade Daten...</pre>
<div id="wifictrl">-</div>
<table>
<tr><td>Controllertemperatur: </td><td id="ct">-</td><td>°C</td></tr>
<tr><td>Batterieladung: </td><td id="cbat">-</td><td>%</td></tr>
<tr><td>Spannung: </td><td id="cusb">-</td><td id="cusb2"></td></tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="cts">-</td></tr>
</table>
<hr>
<?php
if(!isset($_SESSION["user"])) {
echo '<a href="login.php"><button>Login</button></a><hr>';
}
if(isset($_SESSION['rights']) && str_contains($_SESSION['rights'], "-c,")){
echo '<a href="config.php"><button>Einstellungen</button></a><hr>';    
}
?>
<pre id="log">-</pre>
<a href="tec1.php">Techn. Details</a><br>
<br>
<a href="anleitung.htm">Anleitung</a>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

