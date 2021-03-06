"use strict";
/*******************************************************************************
 * R00-Loader
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.events = risa.events || {};

(function(risa){
    var head = document.getElementsByTagName("head");
    if (head && head.length > 0) {
        head = head[0];
    } else {
        head = null;
    }
    var body = document.getElementsByTagName("body");
    if (body && body.length > 0) {
        body = body[0];
    } else {
        body = null;
    }

    if (body && body.removeChild) {
        var loader = document.createElement("div");
        loader.id = "loader";
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
    
    (function(proc){
        if (window.addEventListener) {
            window.addEventListener('load', proc, false);
        } else if (window.attachEvent) {
            window.attachEvent('onload', proc);
        } else if (window.onload) {
            const original = window.onload;
            window.onload = (function(){original(); proc();});
        } else {
            window.onload = proc;
        }
    })(function(){
        risa.events.onload();
    });

    var BASEURL;
    if (document.currentScript) {
        BASEURL = document.currentScript.src;
    } else {
        var candidates = document.getElementsByTagName("script");
        if (!candidates || candidates.length === 0) {
            BASEURL = ".//";
        } else {
            BASEURL = candidates[candidates.length - 1].src;
        }
    }
    BASEURL = BASEURL.substring(0, BASEURL.lastIndexOf('/')) + '/';
    
    var load_status = 0;
    var load_total = 0;
    risa.events.onloadprogressed = (function(status, total){ });
    var progress_status = (function(){
        if (load_status < load_total) {
            load_status += 1;
        }
        risa.events.onloadprogressed(load_status, load_total);
    });
    var load_css = (function(name){
        const cache = document.createElement("link");
        cache.onload = progress_status;
        load_total += 1;
        cache.setAttribute("rel", "stylesheet");
        cache.setAttribute("type", "text/css");
        cache.setAttribute("href", BASEURL + name);
        head.appendChild(cache);
    });
    var load_script = (function(name){
        const cache = document.createElement("script");
        cache.onload = progress_status;
        load_total += 1;
        cache.setAttribute("async", "false");
        cache.setAttribute("type", "text/javascript");
        cache.setAttribute("src", BASEURL + name);
        body.appendChild(cache);
    });
    var load_image = (function(url){
        const cache = new Image();
        cache.onload = progress_status;
        load_total += 1;
        cache.src = url;
    });

    /* Load resources required for constructing this page. */
    load_script("01-loaderview.js");
    load_css("10-basestyle.css");
    load_script("11-effects.js");
    load_css("20-gallery.css");
    load_script("20-gallery.js");
    
    /* Find all img tags and turn them over to the Loader. */
    (function(){
        var elts = document.getElementsByTagName("img");
        for (var i = 0; i < elts.length; ++i) {
            var elt = elts[i];
            load_image(elt.src);
        }
    })();

    /* Collect all <link rel="preload" /> tags for showing progress on the loader view. */
    (function(){
        var elts = document.getElementsByTagName("link");
        for (var i = 0; i < elts.length; ++i) {
            var elt = elts[i];
            if (elt.getAttribute("rel") !== "preload") continue ;
            if (elt.getAttribute("as") === "image") {
                load_image(elt.getAttribute("href"));
            }
        }
    })();
    
})(risa);
