"use strict";
/*******************************************************************************
 * R00-Effects
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.effects = risa.effects || {};

(function(effects){
    effects.resize_img = (img, width, height, msec) => {
        msec = msec || 1000;
        const limit = msec / effects.frame_rate;
        const init_width = parseInt(img.getAttribute("width"));
        const init_height = parseInt(img.getAttribute("height"));
        var count = 0;
        const step = () => {
            count += 1;
            if (count < limit) {
                img.setAttribute("width", init_width + Math.floor((width - init_width) * Math.sin(count / limit * (Math.PI/2))));
                img.setAttribute("height", init_height + Math.floor((height - init_height) * Math.sin(count / limit * (Math.PI/2))));
                setTimeout(step, 1000 / effects.frame_rate);
            } else {
                img.setAttribute("width", width);
                img.setAttribute("height", height);
            }
        };
        step();
    }
})(risa.effects);

