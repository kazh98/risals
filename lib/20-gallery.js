/*******************************************************************************
 * Photo Gallery Scripts
 *  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
 ******************************************************************************/

(function(){
    const originals = [];
    const thumbnails = [];
    
    const find = (lis, name) => {
        for (var i = 0; i < lis.length; ++i) {
            const elt = lis[i];
            if (elt.tagName && elt.tagName.toLowerCase() === name) {
                return elt;
            }
        }
        return null;
    };

    const preview_screen = document.createElement("div");
    preview_screen.id = "gallery-preview-screen";
    const close_thumbnail = () => {
        preview_screen.style.display = "none";
        window.onkeydown = null;
    };
    preview_screen.onclick = close_thumbnail;
    document.getElementsByTagName("body")[0].append(preview_screen);
    
    const show_thumbnail = (id, purge) => {
        const do_purge = () => {
            while (preview_screen.hasChildNodes()) {
                preview_screen.removeChild(preview_screen.lastChild);
            }
        };

        const do_previous = () => {
            show_thumbnail((id + thumbnails.length - 1) % thumbnails.length);
        };
        const do_next = () => {
            show_thumbnail((id + 1) % thumbnails.length);
        };
        
        const build_menu = (downloadable) => {
            const menu = document.createElement("div");
            menu.classList.add("gallery-preview-menu");
            menu.onclick = e => {
                if (!e) e = window.event;
                e.stopPropagation();
                return false;
            };
            const previousButton = document.createElement("button");
            previousButton.append(document.createTextNode("Previous"));
            previousButton.onclick = do_previous;
            menu.append(previousButton);
            const downloadButton = document.createElement("button");
            downloadButton.append(document.createTextNode("Download"));
            if (downloadable) {
                downloadButton.onclick = () => {
                    location.href = originals[id];
                };
            } else {
                downloadButton.disabled = "disabled";
            }
            menu.append(downloadButton);
            const nextButton = document.createElement("button");
            nextButton.append(document.createTextNode("Next"));
            nextButton.onclick = do_next;
            menu.append(nextButton);
            const closeButton = document.createElement("button");
            closeButton.append(document.createTextNode("Close"));
            closeButton.onclick = close_thumbnail;
            menu.append(closeButton);
            return menu;
        };

        if (purge) {
            do_purge();
            preview_screen.append(build_menu());
        }
        preview_screen.style.display = "block";
        window.onkeydown = e => {
            if (!e) e = window.event;
            switch (e.keyCode) {
            case 27:
                close_thumbnail();
                break;
            case 37:
                do_previous();
                break;
            case 39:
                do_next();
                break;
            }
        };

        const img = new Image();
        img.onload = () => {
            const dflag = document.createDocumentFragment();
            img.style.display = "block";
            img.style.position = "absolute";
            img.style.top = "0px";
            img.style.left = "0px";
            img.style.right = "0px";
            img.style.bottom = "0px";
            img.style.maxWidth = "90%";
            img.style.maxHeight = "90%";
            img.style.margin = "auto";
            img.style.cursor = "pointer";
            img.onclick = () => {
                location.href = originals[id];
            }
            dflag.append(img);
            dflag.append(build_menu(true));
            while (preview_screen.hasChildNodes()) {
                preview_screen.removeChild(preview_screen.lastChild);
            }
            preview_screen.append(dflag);
        };
        img.src = thumbnails[id];
    };
    
    /* Add event handlers to each images in gallery. */
    const galleries = document.getElementsByClassName("gallery");
    for (var i = 0; i < galleries.length; ++i) {
        const gallery = galleries[i];
        if (gallery.tagName.toLowerCase() !== "ul") continue ;
        for (var j = 0; j < gallery.children.length; ++j) {
            const li = gallery.children[j];
            if (li.tagName.toLowerCase() !== 'li') continue ;
            const a = find(li.children, 'a');
            if (!a) continue ;
            const id = originals.length;
            originals.push(a.getAttribute("href"));
            thumbnails.push(a.dataset.thumbnail || originals[id]);
            a.onclick = () => {
                show_thumbnail(id, true);
                return false;
            }
            const img = find(a.children, 'img');
            if (img) {
                const max_width  = parseInt(img.getAttribute("width"));
                const max_height = parseInt(img.getAttribute("height"));
                const min_width  = Math.floor(max_width * 9 / 10);
                const min_height = Math.floor(max_height * 9 / 10);
                img.setAttribute("width", min_width);
                img.setAttribute("height", min_height);
                if (document.getElementsByTagName("body")[0].classList.contains("rich")) {
                    const period = img.src.lastIndexOf('.');
                    const prefix = img.src.substring(0, period);
                    const suffix = img.src.substring(period);
                    a.onmouseenter = () => {
                        img.src = prefix + "_rich" + suffix;
                        risa.effects.resize_img(img, max_width, max_height, 200);
                    };
                    a.onmouseleave = () => {
                        img.src = prefix + suffix;
                        risa.effects.resize_img(img, min_width, min_height, 200);
                    }
                } else {
                    a.onmouseenter = () => {
                        risa.effects.resize_img(img, max_width, max_height, 200);
                    };
                    a.onmouseleave = () => {
                        risa.effects.resize_img(img, min_width, min_height, 200);
                    }
                }
            }
        }
    }
})();
