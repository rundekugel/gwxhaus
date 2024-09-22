<?php 
session_start();
?>
<h1>switcher</h1>
hi<br>

<?php
if(isset($_SESSION["user"])) {
 echo("hi user!".$_SESSION["user"]."<br>");
}

function tcptx($msg){
    $fp = fsockopen("localhost", 18891, $errn,$errs, 5);
    if (!$fp) {
    echo "$errstr ($errno)<br />\n";
    } else {
        fwrite($fp, $msg);
        fclose($fp);
    }
}    

function logit($text){
    //    
    return;
    $fp=fopen("sw.log","a");
    fwrite($fp,$text);
    fclose($fp);
}

if(isset($_SESSION["rights"])){
     $rights = $_SESSION["rights"];
     echo $rights."<br>";
    $keys = array("w1","w2","w3","w4","m1","m2",
                "cfg","rem","manually","globs","globs?","cfg?",
                "d1","d2","li1","li2");
    foreach($keys as $k) {
        if(isset($_GET[$k])) {
            $v = $_GET[$k];
            echo $k."=".$v."<br>";
            $user= $_SESSION["user"];
            tcptx($k."=".$v.";u:".$user.";r:".$rights);
            //mqtttx($k."=".$v.";u:".$user.";r:".$rights);
            logit($k."=".$v."\r\n");
            // send via mqtt
        }
    }
}

echo "<br>done.";
?>
<hr>
