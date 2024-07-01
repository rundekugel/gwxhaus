//<script type="text/javascript">
var c=0;
var t;
var timer_is_on=0;

// function timedCount()
// {
// document.getElementById('txt').value=c;
// c=c+1;
// alert("I am an alert box"+str(c));
// t=setTimeout("timedCount()",1000);
// }

function doTimer()
{
if (!timer_is_on)
  {
  timer_is_on=1;
  timedCount();
  }
}

//</script> 
