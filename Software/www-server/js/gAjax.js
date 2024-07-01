//$Id: gAjax.js 193 2011-10-29 18:52:18Z gaul1 $
//load content via js
//include with <script src="gAjax.js" type="text/javascript"></script>

function cFileContent(rxHandler) {
    var xmlHttpObject = false;
    this.file ="";
    var rText ="";
    var locRxHandler =0;
    
   if(rxHandler) locRxHandler = rxHandler;
   
    //init
    if (typeof XMLHttpRequest != 'undefined') {
        xmlHttpObject = new XMLHttpRequest();
    }

    if (!xmlHttpObject) {
        try     {
            xmlHttpObject = new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch(e)     {
            try         {
                xmlHttpObject = new ActiveXObject("Microsoft.XMLHTTP");
            }
            catch(e) {
                xmlHttpObject = null;
            }
        }
    }

 
    this.handleRx = function() {
        if (xmlHttpObject.readyState == 4) {
            rText = xmlHttpObject.responseText;
            if(locRxHandler != 0) locRxHandler(xmlHttpObject.responseText);
        }
    }    
    
    this.load = function(fileName) {
        if(fileName) this.file = fileName;
        xmlHttpObject.open('get', this.file);
        xmlHttpObject.onreadystatechange = this.handleRx;
        xmlHttpObject.send(null);
        return false;
    }    
    
    this.getText = function(){ return rText;}
}


//--- eof ---
