from flask import Flask, request
import os
import importlib
import json
import re
import sys
sys.path.append( "./eval_methods" )

def listEvalMethods():
    try:
        eval_methods_dir = "eval_methods"
        dir_contents = os.listdir( eval_methods_dir )
        methods_arr = []
        for file_name in dir_contents:
            if( os.path.isfile( os.path.join( eval_methods_dir, file_name ) ) and re.search( r"^eval_.*\.py$", file_name ) ):
                module_name = re.sub( r"\.py$",  "", file_name )
                method_name = re.sub( r"^eval_", "", module_name )
                method_json = { "name" : method_name, "description" : "No description found" }
                module = importlib.import_module( module_name )
                desc_func = getattr( module, "description", None )
                if desc_func:
                    model_description = desc_func()
                    method_json["description"] = model_description
                methods_arr.append( method_json );
        return { "methods_arr" : methods_arr }
    except Exception as e:
        return { "error_str" : "Listing methods failed: " + str( e ) }
        

def runEvals( method_names_arr, txt_stt, txt_cor, specified_names_arr ):
    results_arr = []
    for method_name in method_names_arr:
        try:
            if( ( 0 == len( specified_names_arr ) ) or ( method_name in specified_names_arr ) ):
                module_name = "eval_" + method_name;
                module = __import__( module_name )
                func = getattr( module, "evaluate", None )
                if func:
                    print( "Running: " + method_name + " ..." )
                    eval_results = func( txt_stt, txt_cor )
                    results_arr.append( { "eval_method" : method_name, "eval_results" : eval_results } )
        except Exception as e:
            results_arr.append( { "eval_method" : method_name, "error_str" : "Running evaluation failed: " + str( e ) } )
    return { "results_arr" : results_arr }


app = Flask( __name__, static_url_path="" )


port = int( os.getenv( 'PORT', 8080 ) )


@app.route("/")
def root():
    return app.send_static_file( "index.html" )


@app.route("/listmethods", methods = ["GET"])
def listmethods():
    list_modules_result = listEvalMethods()
    return list_modules_result, 200


@app.route("/evaluate", methods = ["POST"])
def evaluate():
    if "POST" == request.method:
        
        # Get parms..
        print( "request.values:\n" + json.dumps( request.values, indent=3 ) )
        if not request.values.get( "txt_stt" ):
            return { "error_str" : "Missing parameter: txt_stt" }, 400
        if not request.values.get( "txt_correct" ):
            return { "error_str" : "Missing parameter: txt_cor" }, 400
        txt_stt = request.values.get( "txt_stt" )
        txt_cor = request.values.get( "txt_correct" )
        print( "txt_stt: " + txt_stt[0:50] + "..." )
        print( "txt_cor: " + txt_cor[0:50] + "..." )
        specified_method_names_arr = []
        if request.values.get( "method_names" ):
            specified_method_names_txt = request.values.get( "method_names" )
            specified_method_names_arr = re.sub( r"\s+", "", specified_method_names_txt ).split( "," )
            print( "specified_method_names_txt: " + specified_method_names_txt )
        print( "specified_method_names_arr:\n" + json.dumps( specified_method_names_arr, indent=3 ) )
        
        # List evaluation modules..
        list_modules_result = listEvalMethods()
        print( "list_modules_result:\n" + json.dumps( list_modules_result, indent=3 ) )
        if( "error_str" in list_modules_result ):
            return list_modules_result, 500
        method_names_arr = []
        for method_json in list_modules_result["methods_arr"]:
            method_names_arr.append( method_json["name"] )
        if( len( method_names_arr ) < 1 ):
            return { "error_str" : "No evaluation modules found" }, 500

        # Evaluate..
        eval_result = runEvals( method_names_arr, txt_stt, txt_cor, specified_method_names_arr )
        return eval_result, 200


if __name__ == '__main__':
    app.run( host='0.0.0.0', port=port, debug=True)
