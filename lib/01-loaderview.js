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

    loader.style.backgroundColor = "#202020";
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
    if (body.dataset.loaderBackground) {
        loader.style.backgroundSize = "cover";
        loader.style.backgroundImage = "url(" + body.dataset.loaderBackground + ")";
        loaderContainer.style.backgroundColor = "rgba(0, 0, 0, 0.45)";
    }

    const title = document.createElement("div");
    title.style.position = "absolute";
    title.style.top = "5%";
    title.style.left = "5%";
    title.style.fontSize = "28pt";
    title.appendChild(document.createTextNode(document.title));
    loaderContainer.appendChild(title);
    
    const loader_status = document.createElement("div");
    loader_status.style.position = "absolute";
    loader_status.style.right = "5%";
    loader_status.style.bottom = loader_status.style.right;
    loader_status.style.width = "45%";

    const progress = document.createElement("div");
    progress.style.background = "rgba(0, 0, 0, 0.2)"
    progress.style.borderLeft = "3px solid rgba(255, 255, 255, 0.8)";
    progress.style.borderRight = progress.style.borderLeft;
    progress.style.padding = "1pt 2pt";
    progress.style.height = "9pt";
    loader_status.appendChild(progress);

    const progressbar = document.createElement("div");
    progressbar.style.width = "0%";
    progressbar.style.height = "100%";
    progressbar.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
    progress.appendChild(progressbar);

    const message = document.createElement("div");
    message.style.fontVariants = "small-caps";
    message.style.fontSize = "16pt";
    message.style.textAlign = "right";
    message.appendChild(document.createTextNode("Now Loading"));
    loader_status.appendChild(message);

    const animated_dots = [];
    for (var i = 0; i < 3; ++i) {
        const dot = document.createElement("span");
        dot.style.visibility = "hidden";
        dot.appendChild(document.createTextNode("."));
        message.appendChild(dot);
        animated_dots.push(dot);
    }
    var animated_dots_status = 0;
    const animated_dots_timer = setInterval(() => {
        if (animated_dots_status < animated_dots.length) {
            animated_dots[animated_dots_status].style.visibility = "visible";
            animated_dots_status += 1;
        } else {
            for (var i = 0; i < animated_dots.length; ++i) {
                animated_dots[i].style.visibility = "hidden";
            }
            animated_dots_status = 0;
        }
    }, 250);
    
    loaderContainer.appendChild(loader_status);

    if (risa.events) {
        risa.events.onload = () => {
            risa.events.onloadprogressed = (function(){ });
            // clearInterval(animated_dots_timer);
            // const blackOut = document.createElement("div");
            // blackOut.style.backgroundColor = "#000000";
            // blackOut.style.position = "fixed";
            // blackOut.style.top = "0px";
            // blackOut.style.left = "0px";
            // blackOut.style.right = "0px";
            // blackOut.style.bottom = "0px";
            // blackOut.style.zIndex = 65535;
            // body.appendChild(blackOut);
            // risa.effects.remove(loader);
            // risa.effects.fadeOut(blackOut, 500);
        };
        const onloadprogressed_super = risa.events.onloadprogressed;
        risa.events.onloadprogressed = (status, total) => {
            onloadprogressed_super(status, total);
            progressbar.style.width = (status * 100 / total) + "%";
        }
    }
    
})(risa);
