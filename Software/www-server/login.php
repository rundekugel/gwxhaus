<?php 
session_start();
?>
<h1>login</h1>
hi<br>

<?php
require("table.php");

if(isset($_SESSION["user"])) {
 echo("hi user!".$_SESSION["user"]);
 echo("<br><a href='main.php'>continue here</a>");
    echo "<script>window.location = 'gwxhaus.php'</script>";
 exit("dd");
}

if (!empty($_POST["user"]))
    {
        if (empty($_POST["ps"]))
          exit("no pwd!");
        echo("login...");
        $_username = $_POST["user"];
        $_passwort = $_POST["ps"];
        //if($_passwort == "ok"){
        if( checkuser($_username, $_passwort)) {
          echo("login ok");
          echo implode(";",$_SESSION);
          //$_SESSION["user"]=$_username;
          //$_SESSION["rights"]="w,m";
            echo("hi user!".$_SESSION["user"]);
            echo("<br><a href='main.php'>continue here</a>");
            echo "<script>window.location = 'gwxhaus.php'</script>";
            exit("dd");
        }
    }
 
?>

<form method="POST" action="login.php">
Ihr Username: <input name="user"><br>
Ihr Passwort: <input name="ps" type=password><br>
<input type=submit name=submit value="Einloggen">
</form>
<hr>
