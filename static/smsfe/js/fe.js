// Contatore caratteri.
function textCounter(field,cntfield,maxlimit){
    if(field.value.length > maxlimit)
        field.value = field.value.substring(0,maxlimit);
    else
        cntfield.value = maxlimit - field.value.length;
}

// Post via AJAX.
jQuery(function() {
  var form = jQuery("#sndsmsform");
  form.submit(function(e) {
      //jQuery("#sendbutton").attr('disabled',true)
      jQuery("#sendbutton").hide()
      jQuery("#sendwrapper").append('<span><img src="/static/images/throbber.gif"></img>&nbsp;&nbsp;&nbsp;&nbsp;Sendig message, please wait ... </span>')
      jQuery("#ajaxwrapper").load(
          form.attr('action') + ' #ajaxwrapper',
          form.serializeArray(),
          function(responseText,responseStatus) {
              //jQuery("#sendbutton").attr('disabled',false);
              jQuery("#sendbutton").show()
              alert(responseStatus);
          }
      );
      e.preventDefault(); 
  });
});

//Gestione lista destinatari.
function addSelectedItemsToParent() {
    self.opener.addToParentList(window.document.forms[0].dstList);
    window.close();
}

function fillInitialDestList(){
    var dstList = window.document.forms[0].dstList;
    var srcList = self.opener.window.document.forms[0].parentList;
    for(var count = dstList.options.length - 1; count >= 0; count--){
        dstList.options[count] = null;
    }
    for(var i = 0; i < srcList.options.length; i++){
        if(srcList.options[i] != null)
            dstList.options[i] = new Option(srcList.options[i].text);
    }
}


function addSrcToDestList(src, dst){
    dstList = document.getElementById(dst);
    srcList = document.getElementById(src);
    var len = dstList.length;
    for(var i = 0; i < srcList.length; i++){
        if ((srcList.options[i] != null) && (srcList.options[i].selected)) {
            // Verifica presenza del destinatario;
            // se non presente lo aggiungo.
            var found = false;
            for(var count = 0; count < len; count++){
                if(dstList.options[count] != null){
                    if(srcList.options[i].text == dstList.options[count].text){
                        found = true;
                        break;
                    }
                }
            }

            if (found != true){
                dstList.options[len] = new Option(srcList.options[i].text,srcList.options[i].value);
                //deleteFromList(src);
                len++;
            }
        }
   }
}

// Elimina elemento da una lista.
function deleteFromList(lst){
    var list = document.getElementById(lst);
    var len = list.options.length;
    for(var i = (len-1); i >= 0; i--){
        if ((list.options[i] != null) && (list.options[i].selected == true)){
            list.options[i] = null;
        }
   }
}

// Elimina elemento.
function deleteFromDestList(dst){
    var dstList  = document.getElementById(dst);
    var len = dstList.options.length;
    for(var i = (len-1); i >= 0; i--){
        if ((dstList.options[i] != null) && (dstList.options[i].selected == true)){
            dstList.options[i] = null;
        }
   }
}

// Seleziona tutto.
function selectAll(selectBox,selectAll){
    var selectBox  = document.getElementById(selectBox);
    for(var i=0; i<selectBox.length; i++){
        selectBox.options[i].selected = selectAll;
    }
}

//function selectAll(selectBox,selectAll) {
    //// have we been passed an ID
    //if (typeof selectBox == "string") {
        //selectBox = document.getElementById(selectBox);
    //}
    //// is the select box a multiple select box?
    //if (selectBox.type == "select-multiple") {
        //for (var i = 0; i < selectBox.options.length; i++) {
            //selectBox.options[i].selected = selectAll;
        //}
    //}
//}

// FINE - Gestione lista destinatari.
