"use strict";
/*******************************************************************************
 * R01-Loader View
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.effects = risa.effects || {};


(function(effects){
    effects.frame_rate = 50;
    
    effects.remove = (elt) => {
        elt.style.display = "none";
        if (elt.remove) {
            elt.remove();
        } else if (elt.parentNode) {
            elt.parentNode.removeChild(elt);
        }
    }
    
    effects.fadeOut = (elt, msec) => {
        msec = msec || 1000;
        const limit = msec / effects.frame_rate;
        var count = 0;
        const step = () => {
            count += 1;
            elt.style.opacity = (limit - count) / limit;
            if (count < limit) {
                setTimeout(step, 1000 / effects.frame_rate);
            } else {
                effects.remove(elt);
            }
        };
        step();
    }
})(risa.effects);


(function(risa){
    const loader = document.getElementById("loader");
    if (!loader) return ;

    loader.style.backgroundColor = "#000060";
    loader.style.color = "#FFFFFF";
    loader.style.fontFamily = "sans-serif";

    const body = document.getElementsByTagName("body")[0];
    
    while (loader.hasChildNodes()) {
        const elt = loader.lastChild;
        if (elt.tagName && elt.tagName.toLowerCase() === "img") {
            backgroundCandidates.push(elt.src);
        }
        loader.removeChild(elt);
    }
    const loaderContainer = document.createElement("div");
    loaderContainer.style.position = "absolute";
    loaderContainer.style.top = "0px";
    loaderContainer.style.left = "0px";
    loaderContainer.style.right = "0px";
    loaderContainer.style.bottom = "0px";
    loader.appendChild(loaderContainer);

    const title = document.createElement("div");
    title.style.position = "absolute";
    title.style.top = "5%";
    title.style.left = "5%";
    title.style.fontSize = "28pt";
    title.appendChild(document.createTextNode(document.title));
    loaderContainer.appendChild(title);
    
    const loader_status = document.createElement("div");
    loader_status.style.position = "absolute";
    loader_status.style.width = "45%";
    loader_status.style.height = "16pt";
    loader_status.style.top = "0px";
    loader_status.style.left = "0px";
    loader_status.style.right = "0px";
    loader_status.style.bottom = "0px";
    loader_status.style.margin = "auto";
    loader_status.style.backgroundColor = "#C0C0C0";
    loader_status.style.border = "1px outset";

    const progress = document.createElement("div");
    progress.style.height = "100%";
    loader_status.appendChild(progress);

    const progressbar = document.createElement("div");
    progressbar.style.width = "0%";
    progressbar.style.height = "100%";
    progressbar.style.backgroundColor = "#0000C0";
    progress.appendChild(progressbar);

    loaderContainer.appendChild(loader_status);

    risa.mode = body.dataset.mode || "release";
    
    if (risa.mode === "debug" && risa.events) {
        const status_format = " objects have been copied.";
        const debug_screen = document.createElement("div");
        debug_screen.style.position = "absolute";
        debug_screen.style.right = "5%";
        debug_screen.style.bottom = "5%";
        debug_screen.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
        debug_screen.style.color = "#000000";
        debug_screen.style.fontFamily = "sans-serif";
        debug_screen.style.fontSize = "9pt";
        const status_message = document.createTextNode(0 + status_format);
        debug_screen.appendChild(status_message);
        risa.events.onloadprogressed = (status, total) => {
            status_message.nodeValue = status + status_format;
        };
        loaderContainer.appendChild(debug_screen);
    }
    
    if (risa.events) {
        risa.events.onload = () => {
            risa.events.onloadprogressed = (function(){ });
            const blackOut = document.createElement("div");
            blackOut.style.backgroundColor = "#000000";
            blackOut.style.position = "fixed";
            blackOut.style.top = "0px";
            blackOut.style.left = "0px";
            blackOut.style.right = "0px";
            blackOut.style.bottom = "0px";
            blackOut.style.zIndex = 65535;
            body.appendChild(blackOut);
            risa.effects.remove(loader);
            risa.effects.fadeOut(blackOut, 500);
        };
        const onloadprogressed_super = risa.events.onloadprogressed;
        risa.events.onloadprogressed = (status, total) => {
            onloadprogressed_super(status, total);
            progressbar.style.width = (status * 100 / total) + "%";
        }
    }
    
})(risa);
