"use strict";
/*******************************************************************************
 * R00-Preloader
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.events = risa.events || {};

(function(risa){
    var body, loader, onload_handler;

    if (!window) return ;
    if (!document) return ;
    if (!document.getElementsByTagName) return ;
    if (!document.createElement) return ;
    
    body = document.getElementsByTagName("body");
    if (body && body.length > 0) {
        body = body[0];
    } else {
        return ;
    }

    if (!loader && body.appendChild && body.removeChild) {
        loader = document.createElement("div");
        loader.id = "loader";
        loader.style = loader.style || {};
        loader.style.position = "fixed";
        loader.style.top = "0px";
        loader.style.left = "0px";
        loader.style.right = "0px";
        loader.style.bottom = "0px";
        loader.style.zIndex = 65535;
        loader.style.backgroundColor = "#000000";
        body.appendChild(loader);
        risa.events.onload = (function(){
            body.removeChild(loader);
        });
    } else {
        risa.events.onload = (function(){ });
    }

    onload_handler = (function(){
        risa.events.onload();
    });
    if (window.addEventListener) {
        window.addEventListener('load', onload_handler, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', onload_handler);
    } else if (window.onload) {
        var original = window.onload;
        window.onload = (function(){original(); onload_handler();});
    } else {
        window.onload = onload_handler;
    }
})(risa);
