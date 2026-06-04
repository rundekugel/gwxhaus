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
function add2Log(text){
    var cb = document.getElementById("cb_log");
    if(cb && cb.checked){
        add2Id("log", text);
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

    add2Id("log","setRTC: "+rtc);
}

function toggle(id){
    var old = document.getElementById(id).innerHTML;

    if(old=="."){
        write2Id(id, "x");
    }else{
        write2Id(id, ".");
    }
}

function makeTable(id, x,y){
    var xtable = "<table><tr><td>h\\m</td>";

    for (var x1 = 0; x1 < x; x1++) {
        xtable += "<td>"+(x1*5)+"</td>";
    }

    xtable += "</tr>";

    for (var y1 = 0; y1 < y; y1++) {
        xtable += '<tr><td>'+y1+'</td>';

        for (var x1 = 0; x1 < x; x1++) {
            var cid = id+"_"+x1+"_"+y1;

            xtable += '<td id="' + cid +
                      '" onclick="toggle(\'' + cid +
                      '\')">.</td>';
        }

        xtable += '</tr>';
    }

    xtable += "</table>";
    write2Id(id, xtable);
}

function readTable(id){
    var x=12;
    var y=24;
    var data = "";

    for (var y1 = 0; y1 < y; y1++) {
        for (var x1 = 0; x1 < x; x1++) {
            var cid = id+"_"+x1+"_"+y1;
            var v = document.getElementById(cid).textContent;

            if(v != "x") v=".";
            data += v;
        }
        data +=";";
    }

    data += "<br>";
    add2Id("log", id+":"+data);
}

function getTable(id){

    var test = document.getElementById(id + "_0_0");

    if(!test){
        return "";
    }

    var x=12;
    var y=24;
    var data = "";

    for (var y1 = 0; y1 < y; y1++) {
        for (var x1 = 0; x1 < x; x1++) {
            var cid = id+"_"+x1+"_"+y1;
            var cell = document.getElementById(cid);
            if(cell && cell.textContent=="x"){
                data += "x";
            }else{
                data += ".";
            }
        }
        data += ";";
    }

    return data;
}

function download(filename, text) {
    var element = document.createElement('a');

    element.setAttribute(
        'href',
        'data:text/plain;charset=utf-8,' + encodeURIComponent(text)
    );

    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function downloadConfig_1u2(){
    var currentdate = new Date();

    var timetext =
        currentdate.getFullYear() +
        ("0"+(currentdate.getMonth()+1)).slice(-2) +
        ("0"+currentdate.getDate()).slice(-2) + "_" +
        ("0"+currentdate.getHours()).slice(-2) +
        ("0"+currentdate.getMinutes()).slice(-2) +
        ("0"+currentdate.getSeconds()).slice(-2);

    var data = "Gewaechshaus Wasserzeiten Konfiguration\r\n";
    data += timetext + "\r\n";
    data += "w1:" + getTable("table1") + "\r\n";
    data += "w2:" + getTable("table2") + "\r\n";

    download('gwxHausWasserKonfig_' + timetext + '.txt', data);
}

function setTable(id, data){
    var rows = data.split(";");

    for(var y=0; y<24; y++){

        if(!rows[y]) continue;

        for(var x=0; x<12; x++){

            var cid = id + "_" + x + "_" + y;
            var cell = document.getElementById(cid);

            if(!cell) continue;

            if(rows[y][x] == "x"){
                cell.textContent = "x";
            }else{
                cell.textContent = ".";
            }
        }
    }
}

function exportConfigJSON(){

    var cfg = {

        version : 2,
        created : new Date().toISOString(),

        water : {
            w1 : getTable("table1"),
            w2 : getTable("table2"),
            w3 : getTable("table3"),
            w4 : getTable("table4")
        },

        haus1 : {
            tmax     : getValue("h1tmax"),
            tmin     : getValue("h1tmin"),
            hmax     : getValue("h1hmax"),
            frost    : getValue("h1frost"),
            hmin1    : getValue("h1hmin1"),
            hmin2    : getValue("h1hmin2"),
            heizung  : getValue("h1heizung"),

            reverse1 : getChecked("h1R"),
            reverse2 : getChecked("h1R2")
        },

        haus2 : {
            tmax     : getValue("h2tmax"),
            tmin     : getValue("h2tmin"),
            hmax     : getValue("h2hmax"),
            frost    : getValue("h2frost"),
            hmin1    : getValue("h2hmin1"),
            hmin2    : getValue("h2hmin2"),
            heizung  : getValue("h2heizung"),

            reverse1 : getChecked("h2R"),
            reverse2 : getChecked("h2R2")
        }
    };

    var currentdate = new Date();

    var filename =
        "gwxHausKonfig_" +
        currentdate.getFullYear() +
        ("0"+(currentdate.getMonth()+1)).slice(-2) +
        ("0"+currentdate.getDate()).slice(-2) + "_" +
        ("0"+currentdate.getHours()).slice(-2) +
        ("0"+currentdate.getMinutes()).slice(-2) +
        ("0"+currentdate.getSeconds()).slice(-2) +
        ".json";

    download(filename, JSON.stringify(cfg,null,2));
}

function importConfigJSON(){

    var input = document.createElement("input");

    input.type = "file";
    //input.accept = ".json,application/json";

    input.onchange = function(event){

        var file = event.target.files[0];

        if(!file){
            return;
        }

        var reader = new FileReader();

        reader.onload = function(e){

            try{

                var cfg = JSON.parse(e.target.result);

                console.log(cfg);

                if(cfg.water){

                    if(cfg.water.w1) setTable("table1", cfg.water.w1);
                    if(cfg.water.w2) setTable("table2", cfg.water.w2);
                    if(cfg.water.w3) setTable("table3", cfg.water.w3);
                    if(cfg.water.w4) setTable("table4", cfg.water.w4);

                }else{

                    // altes Format

                    if(cfg.w1) setTable("table1", cfg.w1);
                    if(cfg.w2) setTable("table2", cfg.w2);
                    if(cfg.w3) setTable("table3", cfg.w3);
                    if(cfg.w4) setTable("table4", cfg.w4);
                }

                if(cfg.haus1){

                    setValue("h1tmax", cfg.haus1.tmax);
                    setValue("h1tmin", cfg.haus1.tmin);
                    setValue("h1hmax", cfg.haus1.hmax);
                    setValue("h1frost", cfg.haus1.frost);
                    setValue("h1hmin1", cfg.haus1.hmin1);
                    setValue("h1hmin2", cfg.haus1.hmin2);
                    setValue("h1heizung", cfg.haus1.heizung);

                    setChecked("h1R", cfg.haus1.reverse1);
                    setChecked("h1R2", cfg.haus1.reverse2);
                }

                if(cfg.haus2){

                    setValue("h2tmax", cfg.haus2.tmax);
                    setValue("h2tmin", cfg.haus2.tmin);
                    setValue("h2hmax", cfg.haus2.hmax);
                    setValue("h2frost", cfg.haus2.frost);
                    setValue("h2hmin1", cfg.haus2.hmin1);
                    setValue("h2hmin2", cfg.haus2.hmin2);
                    setValue("h2heizung", cfg.haus2.heizung);

                    setChecked("h2R", cfg.haus2.reverse1);
                    setChecked("h2R2", cfg.haus2.reverse2);
                }

                alert("Konfiguration geladen.");

            }catch(ex){

                console.error(ex);
                alert("Ungültige JSON-Datei.");
            }
        };

        reader.readAsText(file);
    };

    input.click();
}

function getValue(id){
    var e = document.getElementById(id);
    return e ? e.value : "";
}

function setValue(id,value){
    var e = document.getElementById(id);
    if(e) e.value = value;
}

function getChecked(id){
    var e = document.getElementById(id);
    return e ? e.checked : false;
}

function setChecked(id,value){
    var e = document.getElementById(id);
    if(e) e.checked = value;
}

</script>
</head>

<body onload='makeTable("table1",12,24);makeTable("table2",12,24);'>

<h1>Konfiguration Gew&auml;chshaus Unter&ouml;d</h1>
<hr>
Test Version 0.0.4
<hr>

<a href="gwxhaus.php">Zurück</a>

<?php
if(isset($_SESSION["user"])) {

    echo "<hr>Angemeldet als: "
        . htmlspecialchars($_SESSION["user"], ENT_QUOTES, 'UTF-8');

    // echo " &nbsp;&nbsp;<a href='logout.php'><button>Logout</button></a>";

    if(isset($_SESSION['rights'])) {
		// echo $_SESSION['rights'];
        $rights = array_map('trim', explode(',', $_SESSION['rights']));

        if (!in_array('-c', $rights, true)) {
            die(" &nbsp;&nbsp;Du hast leider keine Rechte, Einstellungen zu &auml;ndern.<hr>");
        }

        echo htmlspecialchars($_SESSION['rights'], ENT_QUOTES, 'UTF-8');
    }else{
		die(" &nbsp;&nbsp; Datenbankfehler.");
	}
}
?>

<hr>
<button onclick=makeTable("table3",12,24);makeTable("table4",12,24);>test 3 + 4</button>&nbsp;&nbsp;&nbsp;
<button onclick=settime()>Setze Uhrzeit auf aktuelle Zeit</button>
<h3>Gew&auml;chshaus Wasser Zeiten</h3>
. = Aus / x = An<br>
<table><tr><td>
<h4>Wasserventil1</h4><div id="table1">-</div></td><td></td><td>
<h4>Wasserventil2</h4><div id="table2">-</div></td></tr></table>
<br>
<table><tr><td>
<h4>Wasserventil3</h4><div id="table3">-</div></td><td></td><td>
<h4>Wasserventil4</h4><div id="table4">-</div></td></tr></table>
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
<hr>

<button onclick='readTable("table1");readTable("table2");'>config to text</button>
<!--a href="data:application/octet-stream,field1%2Cfield2%0Afoo%2Cbar%0Agoo%2Cgai%0A">test</a-->
<br>
<button onclick='downloadConfig_1u2();'>Download Wasserzeiten</button><br>

<form onsubmit="download(this['name'].value, this['text'].value)">
  <input type="hidden" name="name" value="gwxHausWasserKonfig.txt">
  <textarea name="text" hidden="true">leer</textarea>
  <input type="submit" value="Download" hidden="true">
</form>

<hr>

<h3>JSON Import / Export</h3>


<button onclick="importConfigJSON()">
Konfiguration laden
</button>

<button onclick="exportConfigJSON()">
Konfiguration speichern
</button>

<br><br>

<div id="log">-</div>
<hr>
Daten werden bei der Übertragung verschlüsselt. Aktionen können nur nach Login durchgeführt werden.<br>
Datenschutz: <a href="/Datenschutz.html">Hier klicken.</a><br>
20260604-2
</body>

