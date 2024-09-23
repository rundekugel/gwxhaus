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

<body onload=makeTable("table1",12,24)>
    
<h1>Konfiguration Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.0.1
<hr>
 &nbsp; &nbsp; 
<a href="gwxhaus.php">Zurück</a> &nbsp; &nbsp; 

<?php
if(isset($_SESSION["user"])) {
  echo "<hr>Angemeldet als: ".$_SESSION["user"];
  echo " &nbsp;&nbsp;<a href='logout.php'><button>Logout</button></a>";

  if(isset($_SESSION['rights']) && !strpos($_SESSION['rights'], "c")){
    die(" &nbsp;&nbsp;Du hast leider eine Rechte, Einstellungen zu &auml;ndern.<hr>");
  }
}
?>
<hr>
<button onclick=makeTable("table1",60,24)>test 60x24</button>&nbsp;&nbsp;&nbsp;
<button onclick=settime()>Setzte Uhrzeit auf aktuelle Zeit</button>
<h3>Gew&auml;chshaus Wasser Zeiten</h3>
<div id="table1">-</div>
<br>
<hr>
<div id="log">-</div>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20240118-2
</body>

