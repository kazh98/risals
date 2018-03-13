"use strict";
/*******************************************************************************
 * R03-XSLT
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/
var risa = risa || {};
risa.domutil = risa.domutil || {};
risa.events = risa.events || {};
risa.events.gallery = risa.events.gallery || {};

(function(domutil){
    domutil.getTagName = (node) => {
        if (!node || !node.tagName) return "<UNK>";
        return node.tagName.toLowerCase();
    };

    domutil.getDescendantById = (target, id) => {
        const elt = document.getElementById(id);
        let p = elt;
        for (let p = elt; p; p = p.parentNode) {
            if (p === target) {
                return elt;
            }
        }
        return false;
    };
    
    domutil.checkChild = (target, tagName, index=-1) => {
        if (!target) return false;
        if (index < 0) {
            for (let i = 0; i < target.childNodes.length; ++i) {
                const elt = target.childNodes[i];
                if (!(elt instanceof HTMLElement)) continue ;
                return domutil.getTagName(elt) === tagName ? elt : false;
            }
        } else {
            if (target.childNodes.length <= index) return false;
            if (domutil.getTagName(target.childNodes[index]) !== tagName) return false;
            return target.childNodes[index];
        }
    };
    
    domutil.removeAllChildren = (target) => {
        if (!target || !(target instanceof HTMLElement)) return [];
        const items = [];
        while (target.hasChildNodes()) {
            const elt = target.lastChild;
            items.push(elt);
            target.removeChild(elt);
        }
        for (let i = 0, j = items.length - 1; i < j; ++i, --j) {
            const temp = items[i];
            items[i] = items[j];
            items[j] = temp;
        }
        return items;
    };

    domutil.dom0 = (target, attr, ...children) => {
        if (!target || !(target instanceof HTMLElement)) return false;
        if (attr) {
            for (let key in attr) {
                target.setAttribute(key, attr[key]);
            }
        }
        for (let i = 0; i < children.length; ++i) {
            if (typeof children[i] === "string" || children[i] instanceof String) {
                target.appendChild(document.createTextNode(children[i]));
            } else {
                target.appendChild(children[i]);
            }
        }
        return target;
    }
    
    domutil.dom1 = (name, attr, ...children) => {
        return domutil.dom0(document.createElement(name), attr, ...children);
    };
})(risa.domutil);

(function(risa){
    const domutil = risa.domutil;
    const events = risa.events;
    const dom1 = domutil.dom1;
    
    const target = document.getElementById("contents");
    if (!target) return ;

    const title = (function(){
        const h1 = target.getElementsByTagName("h1");
        if (h1.length <= 0) return "";
        return h1[0].innerText;
    })();
    const footer = domutil.removeAllChildren(
        domutil.getDescendantById(target, "footer"));

    const gallery = (function(){
        const gallery = domutil.getDescendantById(target, "gallery");
        if (!gallery) return [];
        const result = [];
        for (let i = 0; i < gallery.childNodes.length; ++i) {
            const li  = domutil.checkChild(gallery, "li", i);
            const a   = domutil.checkChild(li, "a");
            const img = domutil.checkChild(a, "img");
            if (!img) continue ;
            const image = {};
            image.url = a.getAttribute("href");
            image.thumbnail = img.getAttribute("src");
            image.thumbnail_width = img.getAttribute("width");
            image.thumbnail_height = img.getAttribute("height");
            image.thumbnail_large = a.dataset.thumbnail || image.url;
            result.push(image);
        }
        return result;
    })();

    domutil.removeAllChildren(target);
    target.appendChild(
        dom1("h1", null, title));
    target.appendChild(
        dom1("div", {"class": "container"},
             dom1("p", null,
                  dom1("a", {"class": "button", "href": "../"},
                       "Parent Directory")),
             dom1("ul", {"class": "gallery"},
                  ...gallery.map(elt => dom1("li", null,
                                             dom1("a", {"href": elt.url,
                                                        "data-thumbnail": elt.thumbnail_large},
                                                  dom1("img", {"src": elt.thumbnail,
                                                               "width": elt.thumbnail_width,
                                                               "height": elt.thumbnail_height})))))));
    target.appendChild(
        dom1("div", {"class": "footer"}, ...footer));
})(risa);
