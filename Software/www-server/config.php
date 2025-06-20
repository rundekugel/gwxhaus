<?php session_start(); ?>
<!DOCTYPE html>
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Konfiguration Unter&ouml;d Gew&auml;chshaus</title>

<link rel="stylesheet" href="styles.css">
 
<script type="text/javascript" src="js/tools.js"></script>
<script type="text/javascript" src="js/timer.js"></script>
<script type="text/javascript" src="js/gAjax.js"></script>

<script type="text/javascript">
  //defaults

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
    //add2Log("setRTC: "+rtc);
    add2Id("log","setRTC: "+rtc);
    //switcher(rtc);
  }  

  //-------------------------------------------- 
  
  function toggle(id){
      old = document.getElementById(id).innerHTML;
      if(old=="."){
          write2Id(id, "x");
      }else{
          write2Id(id, ".");
      }
  }
  function makeTable(id, x,y){
      //id,x,y
      var xtable = "<table><td>h\\m</td>";
      for (var x1 = 0; x1 < x; x1++) {
        xtable +="<td>"+x1*5+"</td>";
      }      
      for (var y1 = 0; y1 < y; y1++) {
            xtable +='<tr><td>'+y1+'</td>';
            for (var x1 = 0; x1 < x; x1++) {
                var cid = id+"_"+x1+"_"+y1;
                xtable +="<td id="+cid+' onclick=toggle("'+cid+'")>.</td>';
            }
            xtable +='</tr>';
      }
        
  
      xtable += "</table>";
      //add2Id("log","t:"+x+"/"+y);
      write2Id(id, xtable);
  }
  //--------------------
</script>
</head>    

<body onload='makeTable("table1",12,24);makeTable("table2",12,24);'>
    
<h1>Konfiguration Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.0.1a
<hr>
 &nbsp; &nbsp; 
<a href="gwxhaus.php">Zurück</a> &nbsp; &nbsp; 

<?php
if(isset($_SESSION["user"])) {
  echo "<hr>Angemeldet als: ".$_SESSION["user"];
  echo " &nbsp;&nbsp;<a href='logout.php'><button>Logout</button></a>";

  if(isset($_SESSION['rights']) && !strpos($_SESSION['rights'], "c")){
    die(" &nbsp;&nbsp;Du hast leider keine Rechte, Einstellungen zu &auml;ndern.<hr>");
  }
}
?>
<hr>
<button onclick=makeTable("table3",12,24);makeTable("table4",12,24);>test 3 + 4</button>&nbsp;&nbsp;&nbsp;
<button onclick=settime()>Setzte Uhrzeit auf aktuelle Zeit</button>
<h3>Gew&auml;chshaus Wasser Zeiten</h3>
. = Aus / x = An<br>
<table><td>
<h4>Wasserventil1</h4><div id="table1">-</div></td><td></td><td>
<h4>Wasserventil2</h4><div id="table2">-</div></td>
</table>
<br>
<table><td>
<h4>Wasserventil3</h4><div id="table3">-</div></td><td></td><td>
<h4>Wasserventil4</h4><div id="table4">-</div></td>
</table>
<br>
<hr>
<H1>Haus1</H1>
Fenster oeffnen ueber <input type="text" id="h1tmax" name="h1tmax" value="22" size="2"> °C ..  Umgekehrt, wenn draussen wärmer als drinnen: <input type="checkbox" id="h1R" name="h1R" checked /><br>
Fenster schliessen unter  <input type="text" id="h1tmin" name="h1tmax" value="22" size="2"> °C ..  Umgekehrt, wenn draussen wärmer als drinnen: <input type="checkbox" id="h1R2" name="h1R2"/><br>
Fenster oeffnen ueber <input type="text" id="h1hmax" name="h1hmax" value="97" size="2"> % Luftfeuchte. Frostgrenze: <input type="text" id="h1frost" name="h1frost" value="4" size="2"> °C<br>
Wasser 1a oeffnen unter <input type="text" id="h1hmin1" name="h1hmin1" value="15" size="2"> % Luftfeuchte<br>
Wasser 1b oeffnen unter <input type="text" id="h1hmin2" name="h1hmin2" value="15" size="2"> % Luftfeuchte<br>
Heizung1 unter <input type="text" id="h1heizung" name="h1heizung" value="8" size="2"> °C<br>

<H1>Haus2</H1>
Fenster oeffnen ueber <input type="text" id="h2tmax" name="h2tmax" value="22" size="2"> °C ..  Umgekehrt, wenn draussen wärmer als drinnen:<input type="checkbox" id="h2R" name="h2R" checked /> <br>
Fenster schliessen unter  <input type="text" id="h2tmin" name="h2tmax" value="22" size="2"> °C ..  Umgekehrt, wenn draussen wärmer als drinnen:<input type="checkbox" id="h2R2" name="h2R2"/> <br>
Fenster oeffnen ueber <input type="text" id="h2hmax" name="h2hmax" value="97" size="2"> % Luftfeuchte. Frostgrenze: <input type="text" id="h2frost" name="h2frost" value="4" size="2"> °C<br>
Wasser 2a oeffnen unter <input type="text" id="h2hmin1" name="h2hmin1" value="15" size="2"> % Luftfeuchte<br>
Wasser 2b oeffnen unter <input type="text" id="h2hmin2" name="h2hmin2" value="15" size="2"> % Luftfeuchte<br>
Heizung2 unter <input type="text" id="h2heizung" name="h2heizung" value="8" size="2"> °C<br>
<hr>
<button onclick='alert("Noch nicht moeglich!");'>Speichern</button>
<div id="log">-</div>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

