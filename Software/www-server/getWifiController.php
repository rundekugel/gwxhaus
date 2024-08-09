<?php
//<!-- gwxhaus sensor data collector -->
//todo: get data from sessionid

$u="gwxs2";
$t="slw/gwx/2/tele/SENSOR";
sleep(1);
$r=exec("mosquitto_sub -h mq.qc9.de -p 18883 --tls-use-os-certs -u ".$u." -P pwdpwd -t ".$t." -C 1");

echo $r;
?>
