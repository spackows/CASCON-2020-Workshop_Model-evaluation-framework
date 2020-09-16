

function _loadEvalMethods()
{
    document.getElementById( "methods_spinner" ).style.display = "block";
    
    $.ajax( { url      : "./listmethods",
              type     : "GET",
              complete : function( result )
                         {
                             document.getElementById( "methods_spinner" ).style.display = "none";
                             
                             var result_json = result["responseJSON"];
                             if( !result_json )
                             {
                                 alert( "Unexpected result returned from /listmethods" );
                                 return;
                             }
                             
                             var error_str  = result_json["error_str"];
                             if( error_str )
                             {
                                 alert( "Listing methods failed:\n\n" + error_str );
                                 return;
                             }
                                 
                             var methods_arr = result_json["methods_arr"];
                             if( !methods_arr )
                             {
                                 alert( "No methods were returned from /listmethods" );
                                 return;
                             }

                             populateMethodsTable( methods_arr );
                             
                         }
                         
            } );
                
}


function populateMethodsTable( methods_arr )
{
    methods_arr.sort( function( a, b )
    {
        if( a["name"].toLowerCase() < b["name"].toLowerCase() )
        {
            return -1;
        }
        
        if( a["name"].toLowerCase() > b["name"].toLowerCase() )
        {
            return 1;
        }
        
        return 0;
        
    } );
    
    var table = document.getElementById( "methods_table" );
    table.innerHTML = "";
    
    var name = "";
    var description = "";
    for( var i = 0; i < methods_arr.length; i++ )
    {
        method_name = methods_arr[i]["name"];
        method_description = methods_arr[i]["description"];
        
        tr = document.createElement( "tr" );
        tr.innerHTML = "<td><input id='" + method_name + "' type='checkbox' class='method_checkbox'></td>" +
                       "<td><p><b>" + method_name + "</b></p><p>" + method_description + "</p></td>";
        
        table.appendChild( tr );
    }
}


function _evaluate()
{
    var txt_stt = document.getElementById( "stt_textarea" ).value;
    var txt_cor = document.getElementById( "cor_textarea" ).value;
    var specified_methods_arr = getSelectedMethods();
    
    if( !txt_stt || !txt_stt.match( /\S/ ) )
    {
        alert( "No valid generated transcript specified" );
        return;
    }
    
    if( !txt_cor || !txt_cor.match( /\S/ ) )
    {
        alert( "No valid corrected transcript specified" );
        return;
    }
    
    if( !specified_methods_arr || ( specified_methods_arr.length < 1 ) )
    {
        alert( "No methods were selected" );
        return;
    }
    
    document.getElementById( "results_pre" ).innerHTML = "";
    
    document.getElementById( "results_spinner" ).style.display = "block";
    
    $.ajax( { url      : "./evaluate",
              type     : "POST",
              data     : { "txt_stt"      : txt_stt,
                           "txt_correct"  : txt_cor,
                           "method_names" : specified_methods_arr.join( "," ) },
              dataType : "json",
              complete : function( result )
                         {
                             document.getElementById( "results_spinner" ).style.display = "none";
                             
                             var result_json = result["responseJSON"];
                             if( !result_json )
                             {
                                 alert( "Unexpected result returned from /evaluate" );
                                 return;
                             }
                             
                             document.getElementById( "results_pre" ).innerHTML = JSON.stringify( result_json, null, 3 );
                             
                         }
                         
            } );
                
}


function getSelectedMethods()
{
    var checkbox_arr = document.getElementsByClassName( "method_checkbox" );
    
    var selected_method_names_arr = [];
    for( var i = 0; i < checkbox_arr.length; i++ )
    {
        if( checkbox_arr[i].checked )
        {
            selected_method_names_arr.push( checkbox_arr[i].id );
        }
    }
    
    return selected_method_names_arr;
}






