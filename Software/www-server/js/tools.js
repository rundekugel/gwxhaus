//$Id: tools.js 209 2012-02-19 23:44:30Z gaul1 $

function setBgColor (item, color) {
  if (document.getElementById)
    document.getElementById(item).style.background = color;
}
function setTitle (item, text) {
  if (document.getElementById)
    document.getElementById(item).title = text;
}

function setWidth (item, width) {
  if (document.getElementById)
    document.getElementById(item).width = width;
}

function write2Id(id, text){ document.getElementById(id).innerHTML = text;}
function add2Id(id, text){ document.getElementById(id).innerHTML += text;}

function trim (zeichenkette) {
    //zeichenkette = zeichenkette + "";
  return zeichenkette.replace (/^\s+/, '').replace (/\s+$/, '');
}

function zeitGmt(){
    var Jetzt = new Date();
    return Jetzt.toGMTString();
}

const sleep_ms = (milliseconds) => { //use careful! problems on android.
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}
