<?php session_start(); ?>
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
  var m_timerButton = 1
  
  //data stuff
  var m_ioGetGwxSens = "s2.php";
  var m_ioGetWifiController = "w2.php";
  var m_ioGetvsupplyhdl = "v1.php";
  
  //cFileContent is the ajax callback
  oFileioSens = new cFileContent(iohdlSens);
  oFileioWifiCtrl = new cFileContent(wifihdl);
  oFileiovsupplyhdl = new cFileContent(vsupplyhdl);
  //--------------------------------------------
    

  function add2Log(text){
    if(document.getElementById("cb_log").checked){
        add2Id("log",text);
    }
  }

  function startAjax(){
    add2Log("---------------------");
    oFileioSens.load(m_ioGetGwxSens); 
    oFileioWifiCtrl.load(m_ioGetWifiController);
    oFileiovsupplyhdl.load(m_ioGetvsupplyhdl);
  }

  function timer1(){
    if(m_timerButton){
        startAjax();
    }
  }

  function timer1An() {
      if(0==m_timerButton){
          return;
      }
      startAjax();
      vIntervalId = setInterval( "timer1()", m_reloadTime );
  }//-------------------
  
  function timerButton(){
      m_timerButton = 1 - m_timerButton; 
      write2Id("butTimer","asdf");
      if(m_timerButton) {
          write2Id("butTimer","Stop");
          timer1An();    //init next
      } else {
          if(vIntervalId){
            clearInterval(vIntervalId);
          }          
          write2Id("butTimer","Continue");
      }
  }//-----------------------  
            
  function iohdlSens(text){
      add2Log("s:"+text);

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
                
                if(k=="M1") write2Id("md1", val);
                if(k=="M2") write2Id("md2", val);
                //Fenster
                if(k=="F1") write2Id("fen1", val+" %");
                if(k=="F2") write2Id("fen2", val+" %");
                if(k=="mn") {
                    if(val==0) write2Id("manu", "");
                    else {
                        write2Id("manu",
                        "<hr><h2 style=color:red;>Manueller Modus aktiv!</h2>Restdauer: "
                        +val+" Sekunden");
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
                var v2 = parseFloat(v);
                var p = Math.round(v2/4.5*100);
                write2Id("cbat", v2);
                add2Id("cbat", "("+p+"%)");

            if(line.includes("USB=")) {
                var s = parseFloat(line.split("=")[1]);
                write2Id("cusb", line);
                if(s<4.5) write2Id("cusb2", " !Spannung zu gering. Defekt, oder Stromausfall!")                
             }                
            }
            
            if(line.includes("__module__") || line.includes("globs:")) {
                g=line.split("__module__")[1];
                g=line.split("}")[0];
                var t =document.getElementById("ts").innerHTML;
                write2Id("globs", t+"<br>"+g);
             }
            if(line.includes("#komm") || line.includes("cfg:")) {
                var t=document.getElementById("ts").innerHTML;
                write2Id("cfg", t+"<br>"+line);
            }
          }  );
      }catch (error) {
          console.error(error);  
      }
  }//--------------------------------------------      
      
  function wifihdl(text){
      write2Id("wifictrl", text);
      add2Log(text);
      if(text=="" || text.includes("<title>504 ")) {
          //no valid data
          return;
      }
      try {
          var jsn = JSON.parse(text);
          add2Log(text);
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
      add2Log(text);
      
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
  function manually(seconds){
      fetch("switcher.php?manually="+seconds);
  }  
  function switcher(text){
      fetch("switcher.php?"+text);
  }  
  
  function settime(){
    var currentdate = new Date();
    var rtc = "rtc="+ currentdate.getFullYear()+","+(currentdate.getMonth()+1)
                    +","+currentdate.getDate()+",1,"+ currentdate.getHours() +","
                    + currentdate.getMinutes() + "," + currentdate.getSeconds();
    add2Log("setRTC: "+rtc);
    switcher(rtc);
  }  
  
  function ch_refresh(){
      add2Id("log","refresh:");
      r=parseInt(document.getElementById("refresh").value);
      add2Id("log","r:"+r+"<br>");
      m_reloadTime = r;
      if(vIntervalId){
        clearInterval(vIntervalId);
        vIntervalId=0;
      }          
      if(m_timerButton) vIntervalId = setInterval( "timer1()", m_reloadTime );
  }
  //-------------------------------------------- 
</script>
</head>    

<body onload="timer1An(); ">
    
<h1>Technik Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.2.1
<hr>
<!--label for="refresh">HTML Update Interval:</label-->
HTML Update Interval:
<select name="refresh" id="refresh" onchange="ch_refresh()">
<option value="500">0,5s</option>
<option value="1000">1s</option>
<option value="2000">2s</option>
<option value="5000">5s</option>
<option value="10000">10s</option>
<option value="30000">30s</option>
<option value="60000">1m</option>
<option value="60000">10m</option>
<option value="3600000">1h</option>
</select>
 &nbsp; &nbsp; 
<a href="gwxhaus.php">Einfache Ansicht</a> &nbsp; &nbsp; 
<button id="butTimer" onclick="timerButton()">Stop</button> &nbsp; &nbsp; 
<button onclick="startAjax()">Poll 1</button> &nbsp; &nbsp; 

<?php
if(isset($_SESSION["user"])) {
  echo "<hr>Angemeldet als: ".$_SESSION["user"];
  echo " &nbsp;&nbsp;<a href='logout.php'><button>Logout</button></a>";
  echo ' &nbsp;&nbsp;<button onclick="manually(600)">Manuell 10min</button></a>';
  echo ' &nbsp;&nbsp;<button onclick="manually(0)">Manuell off</button></a>';
  echo ' &nbsp;&nbsp;Rechte: '.$_SESSION['rights'];
}
?>
<div id="manu"></div>
<hr>

<h3>Gew&auml;chshaus Sensoren</h3>
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
<h3>Wasser</h3>
<table><tr><td>1A:</td><td id="w1">-</td><td>1B:</td><td id="w3">-</td></tr>
<tr><td>2A:</td><td id="w2">-</td><td>2B:</td><td id="w4">-</td></tr></table>
<?php if(isset($_SESSION["user"])) { echo '
1:
<button onclick="wasseraus(1)" name="butTimer">Wasser1 aus</button> &nbsp;
<button onclick="wasseran(1,1)" >Wasser1 an</button>&nbsp;
<button onclick="wasseran(1,15)" ><s>Wasser1 an 15min</button>&nbsp;
<button onclick="wasseran(1,120)">Wasser an 2h</s></button> 
<br><br>2:
<button onclick="wasseraus(2)" name="butTimer">Wasser2 aus</button>&nbsp;
<button onclick="wasseran(2,1)" >Wasser2 an</button>&nbsp
<button onclick="wasseran(2,15)" ><s>Wasser2 an 15min</button>&nbsp;
<button onclick="wasseran(2,120)">Wasser2 an 2h</s></button>
';}?>
<hr>
<!--
Heartbeat: [<textbox id="hb">.</textbox>] <br>
-->
<tr><td>Letzte Nachricht: </td><td id="ts">-</td></tr>
</table>
<hr>
<h3>Bodenfeuchte</h3>
Haus1: ??% &nbsp;&nbsp;&nbsp;&nbsp; Haus2: ??%

<h2>Fenster Status</h2>
<table><tr><td>Haus1:</td><td id="fen1">-</td><td>Haus2:</td><td id="fen2">-</td></tr></table> 
<hr>

<h3>Controller</h3>
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
<tr><td>Batterieladung: </td><td id="cbat">-</td><td>V</td></tr>
<tr><td>Spannung: </td><td id="cusb">-</td><td id="cusb2"></td></tr>
<tr><td>Letztes Lebenszeichen um:</td><td id="cts">-</td></tr>
</table>
<?php
if(isset($_SESSION["user"])) {
  echo ' &nbsp;&nbsp;<button onclick=manually(6000)>Manuell 100min</button></a>';
  echo ' &nbsp;&nbsp;<button onclick="manually(0)">Manuell off</button></a>';
  echo '<br><br>Show variables: <button onclick=switcher("globs?")>Globals</button></a>';
  echo ' &nbsp;&nbsp;<button onclick=switcher("cfg?=?")>Config</button></a>';
  echo ' &nbsp;&nbsp;<button onclick=switcher("m1=?")>Motor</button></a>';
  echo '<br>&nbsp;&nbsp;<button onclick=settime()>Set Time</button></a> ';
  if(isset($_SESSION['rights']) && str_contains($_SESSION['rights'], "c")){
    echo ' &nbsp;&nbsp; <a href="config.php">Einstellungen</a><hr>';    
  }  
}else{
  echo '<a href="login.php"><button>Login</button></a><hr>';
}
?>
<h4>Globs</h4>
<div id="globs">-</div>
<h4>Config</h4>
<div id="cfg">-</div>
<hr>
<input type="checkbox" name="x" id="cb_log" value="off" > Log on. &nbsp; &nbsp; 
<button id="clrLog" onclick="write2Id('log','')">Clear Log</button> &nbsp; &nbsp; 
<a href="gwxhaus.php">[Einfache Ansicht]</a> &nbsp; &nbsp;
<button onclick="startAjax()">Poll 1</button> &nbsp; &nbsp; 
<br>
<pre id="log">-</pre> &nbsp; &nbsp; 
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

