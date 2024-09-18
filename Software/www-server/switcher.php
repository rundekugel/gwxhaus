<?php 
session_start();
?>
<h1>switcher</h1>
hi<br>

<?php
if(isset($_SESSION["user"])) {
 echo("hi user!".$_SESSION["user"]."<br>");
}

function logit($text){
    return;
    $fp=fopen("sw.log","a");
    fwrite($fp,$text);
    fclose($fp);
}

if(isset($_SESSION["rights"])){
     $rights = $_SESSION["rights"];
     echo $rights."<br>";
     foreach ($_GET as $get) {
        echo strval($get)."<br>";
        
    }
    $keys = array("w1","w2","w3","w4","m1","m2");
    foreach($keys as $k) {
        if(isset($_GET[$k])) {
            $v = $_GET[$k];
            echo $k."=".$v."<br>";
            logit($k."=".$v."\r\n");
            // send via mqtt
        }
    }
}
echo "<br>done.";
?>
<hr>
