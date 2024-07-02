<?php
//<!-- gwxhaus sensor data collector -->
//todo: get data from sessionid

$u="gwxs2";
$t="slw/gwx/2/tele/RESULT";
sleep(1);
$r=exec("mosquitto_sub -h mq.qc9.de -p 18883 --tls-use-os-certs -u ".$u." -P msowAsq1! -t ".$t." -C 1");
$j=json_decode($r);
$r=$j->{"SSerialReceived"};

echo $r;
?>

