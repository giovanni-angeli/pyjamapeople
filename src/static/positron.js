
var __ws_instance;  
var __exposed_callables = {};  

var __on_ws_error = function (evt) {
    console.log("error: " + evt.data);
    alert("error: " + JSON.stringify(evt.data));
}

var __on_ws_open = function (evt) {
    console.log("* ws connection open *");
    document.getElementById("open_btn").disabled = true; 
    document.getElementById("close_btn").disabled = false; 
}

var __on_ws_close = function (evt) {
    console.log("* ws connection closed *");
    document.getElementById("open_btn").disabled = false; 
    document.getElementById("close_btn").disabled = true; 
}

var __on_ws_message = function (evt) {
    try {
        var data = JSON.parse(evt.data);  
        callable = data.callable; 
        args = data.args; 
        __exposed_callables[callable](data.args);
    } catch(err) {
        console.log("err:" + err);
    }
}

var Positron = {}

Positron.open_ws = function (host, port, uri) {
    try {
        if (__ws_instance) {
            __ws_instance.close();
        }
        var resource = "ws://" + host + ":" + port + uri;
        console.log("connecting to: " + resource);
        __ws_instance = new WebSocket(resource);
        __ws_instance.onerror   = __on_ws_error  ; 
        __ws_instance.onopen    = __on_ws_open   ;  
        __ws_instance.onclose   = __on_ws_close  ;
        __ws_instance.onmessage = __on_ws_message;
    } catch(err) {
        console.log("err:" + err);
    }
}

Positron.expose_callables_to_py = function (items) {
    for (var k in items) {
        __exposed_callables[k] = items[k];
    }
}

Positron.call_on_backend = function (callable, args) {
    var data = {'callable': callable, 'args': args};
    var data_s = JSON.stringify(data);
    try {
        __ws_instance.send(data_s);
    } catch(err) {
        console.log("err:" + err);
    }
}

Positron.close_ws = function (host, port, uri) {
    try {
        if (__ws_instance) {
            __ws_instance.close();
        }
    } catch(err) {
        console.log("err:" + err);
    }
}

