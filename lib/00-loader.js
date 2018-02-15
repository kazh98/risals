"use strict";
/*******************************************************************************
 * R00-Loader
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.effects = risa.effects || {};


(function(effects){
    effects.frame_rate = 50;
    
    effects.remove = (elt) => {
        elt.style.display = "none";
        elt.remove();
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
    const get_parent = path => {
        if (path.endsWith("/"))
            path = path.substring(0, path.length - 1);
        return path.substring(0, path.lastIndexOf('/')) + '/';
    }
    const BASEURI = get_parent(document.currentScript.src);
    
    risa.Loader = new class {
        constructor() {
            this.total = 0;
            this.processed = 0;
            this.loaded = false;

            /* Hook myself to the onload event. */
            this.ldqueue = [];
            this.add_loaded_handler(() => {
                risa.effects.fadeOut(document.getElementById("loader"), 200);
            });
            const e = () => {
                this.loaded = true;
                while(this.ldqueue.length > 0) {
                    (this.ldqueue.shift())();
                }
            };
            if (window.addEventListener) {
                window.addEventListener('load', e, false);
            } else if (window.attachEvent) {
                window.attachEvent('onload', e);
            } else if (window.onload) {
                const e0 = window.onload;
                window.onload = () => {e0(); e();};
            } else {
                window.onload = e;
            }
        }

        add_loaded_handler(p) {
            if (this.loaded) {
                p();
            } else {
                this.ldqueue.push(p);
            }
        }

        refresh() {
            if (this.loaded)
                return ;
        }
        
        load_image(url) {
            const cache = new Image();
            cache.onload = () => {
                this.processed += 1;
                this.refresh();
            };
            this.total += 1;
            cache.src = url;
        }

        load_script(name) {
            const cache = document.createElement("script");
            cache.onload = () => {
                this.processed += 1;
                this.refresh();
            };
            this.total += 1;
            cache.setAttribute("rel", "stylesheet");
            cache.setAttribute("type", "text/css");
            cache.setAttribute("href", BASEURI + name);
            document.getElementsByTagName("head")[0].append(cache);
        }
        
        load_css(name) {
            const cache = document.createElement("link");
            cache.onload = () => {
                this.processed += 1;
                this.refresh();
            };
            this.total += 1;
            cache.setAttribute("async", "false");
            cache.setAttribute("type", "text/javascript");
            cache.setAttribute("src", BASEURI + name);
            document.getElementsByTagName("body")[0].append(cache);
        }
    }();

    /* Find all img tags and turn them over to the Loader. */
    (function(){
        const elts = document.getElementsByTagName("img");
        for (var i = 0; i < elts.length; ++i) {
            risa.Loader.load_image(elts.src);
        }
    })();
})(risa);
