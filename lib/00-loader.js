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

            /* Constrct loader display. */
            (() => {
                const loader = document.getElementById("loader");
                if (!loader) return ;

                loader.style.fontFamily = "sans-serif";
                
                /* Page Title */
                const title = document.createElement("div");
                title.style.position = "absolute";
                title.style.top = "5%";
                title.style.left = "5%";
                title.style.fontSize = "28pt";
                title.append(document.createTextNode(document.title));
                loader.append(title);
                
                /* Progress bar */
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
                loader_status.append(progress);

                const progressbar = document.createElement("div");
                progressbar.style.width = "0%";
                progressbar.style.height = "100%";
                progressbar.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
                progress.append(progressbar);
                this.progressbar = progressbar;

                const message = document.createElement("div");
                message.style.fontVariants = "small-caps";
                message.style.fontSize = "16pt";
                message.style.textAlign = "right";
                message.append(document.createTextNode("Now Loading"));
                loader_status.append(message);

                const animated_dots = [];
                for (var i = 0; i < 3; ++i) {
                    const dot = document.createElement("span");
                    dot.style.visibility = "hidden";
                    dot.append(document.createTextNode("."));
                    message.append(dot);
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
                
                loader.append(loader_status);
                this.add_loaded_handler(() => {
                    delete this.progressbar;
                    clearInterval(animated_dots_timer);
                    const blackOut = document.createElement("div");
                    blackOut.style.backgroundColor = "#000000";
                    blackOut.style.position = "fixed";
                    blackOut.style.top = "0px";
                    blackOut.style.left = "0px";
                    blackOut.style.right = "0px";
                    blackOut.style.bottom = "0px";
                    blackOut.style.zIndex = 65535;
                    document.getElementsByTagName("body")[0].append(blackOut);
                    risa.effects.remove(loader);
                    risa.effects.fadeOut(blackOut, 500);
                });
            })();
        }

        add_loaded_handler(p) {
            if (this.loaded) {
                p();
            } else {
                this.ldqueue.push(p);
            }
        }

        refresh() {
            if (this.loaded) return ;

            if (this.progressbar) {
                var score = 0;
                if (this.total === 0) {
                    if (this.processed <= 0) {
                        score = 0;
                    } else {
                        score = 1;
                    }
                } else {
                    score = this.processed / this.total;
                }
                if (score < 0.) score = 0.;
                if (score > 1.) score = 1.;
                this.progressbar.style.width = (score * 100) + "%";
            }
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
            cache.setAttribute("async", "false");
            cache.setAttribute("type", "text/javascript");
            cache.setAttribute("src", BASEURI + name);
            document.getElementsByTagName("body")[0].append(cache);
        }
        
        load_css(name) {
            const cache = document.createElement("link");
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
    }();

    /* Find all img tags and turn them over to the Loader. */
    (function(){
        const elts = document.getElementsByTagName("img");
        for (var i = 0; i < elts.length; ++i) {
            risa.Loader.load_image(elts[i].src);
        }
    })();

    /* Load resources required for constructing this page. */
    risa.Loader.load_css("10-basestyle.css");
    risa.Loader.load_css("20-gallery.css");
    risa.Loader.load_script("20-gallery.js");
    
})(risa);
