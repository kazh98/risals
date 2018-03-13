#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
### risals: Photo Album Maker
###  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
################################################################################
import os, sys, itertools
from datetime import datetime
from argparse import ArgumentParser
from glob import glob
from tqdm import tqdm
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from typing import Tuple
__version__ = '1.19-dev'


###
### Set constant values for configuring the behavior of this program.
###
DEFAULT_TITLE = 'Index of /'

THUMBNAIL_DIR = './cache'

THUMBNAIL1_RATIO  = 90
THUMBNAIL1_WIDTH  = 200
THUMBNAIL1_HEIGHT = 150
THUMBNAIL1_SUFFIX = '_small'

THUMBNAIL2_WIDTH  = 1024
THUMBNAIL2_HEIGHT = 768
THUMBNAIL2_SUFFIX = '_large'

BASETIME = 0
if '__file__' in globals() and os.path.isfile(__file__):
    BASETIME = os.stat(__file__).st_mtime


###
### 
###
def lock_s(filename: str, rich: bool=False, purge: bool=False) -> dict:
    img = Image.open(filename, 'r')
    if rich == True:
        thumb1 = __make_thumbnail(
            img, THUMBNAIL1_SUFFIX,
            THUMBNAIL1_WIDTH  * THUMBNAIL1_RATIO // 100,
            THUMBNAIL1_HEIGHT * THUMBNAIL1_RATIO // 100, colored=False)[0]
        thumb1_rich, thumb1_w, thumb1_h = __make_thumbnail(
            img, THUMBNAIL1_SUFFIX + '_rich', THUMBNAIL1_WIDTH, THUMBNAIL1_HEIGHT, purge=purge)
    else:
        thumb1, thumb1_w, thumb1_h = __make_thumbnail(
            img, THUMBNAIL1_SUFFIX, THUMBNAIL1_WIDTH, THUMBNAIL1_HEIGHT, purge=purge, colored=False)
        thumb1_rich = thumb1
    thumb2, thumb2_w, thumb2_h = __make_thumbnail(
        img, THUMBNAIL2_SUFFIX, THUMBNAIL2_WIDTH, THUMBNAIL2_HEIGHT, purge=purge)
    return {
        "filename": filename,
        "thumbnail1": thumb1,
        "thumbnail1_width": thumb1_w,
        "thumbnail1_height": thumb1_h,
        "thumbnail1_rich": thumb1_rich,
        "thumbnail2": thumb2,
        "thumbnail2_width": thumb2_w,
        "thumbnail2_height": thumb2_h,
        }

def __make_thumbnail(img: Image, suffix: str, width: int, height: int, purge: bool=False, colored=True) -> Tuple[str, int, int]:
    assert img.filename != ""
    if img.size[0] <= width and img.size[0] <= height:
        return img.filename, img.size[0], img.size[1]
    if not os.path.isdir(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)
    prefix = os.path.splitext(img.filename)[0]
    target = os.path.join(THUMBNAIL_DIR, os.path.basename(prefix + suffix + ".jpg"))
    if not purge and os.path.isfile(target) and max(BASETIME, os.stat(img.filename).st_mtime) < os.stat(target).st_mtime:
        thumb = Image.open(target, 'r')
        return target, thumb.size[0], thumb.size[1]
    thumb_width  = img.size[0] * height // img.size[1]
    thumb_height = height
    if thumb_width > width:
        thumb_width  = width
        thumb_height = img.size[1] * width // img.size[0]
    if colored:
        thumb = img.copy()
    else:
        thumb = img.convert('L')
    thumb.thumbnail((thumb_width, thumb_height))
    thumb.save(target, 'JPEG', optimize=True)
    return target, thumb_width, thumb_height


###
###
###
if __name__ == '__main__':
    argparse = ArgumentParser(description='A web photo album generator')
    argparse.add_argument('-r', '--rich', action='store_true',
                          help='generate supplementary files for improving user experiences')
    argparse.add_argument('-p', '--purge', action='store_true',
                          help='regenerates all objects and caches')
    argparse.add_argument('-d', '--debug', action='store_true',
                          help='enable debug mode')
    argparse.add_argument('title', action='store', nargs='?', default=DEFAULT_TITLE,
                          help='a message shown as a title of generated album')
    args = argparse.parse_args()
    
    images = []
    for pattern in ['./*.jpg', './*.JPG', './*.jpeg', './*.JPEG']:
        images.extend(glob(pattern))
    images = list(map(lambda fn: lock_s(fn, rich=args.rich, purge=args.purge), tqdm(sorted(images))))
    env = Environment(
        loader=FileSystemLoader('.', 'utf-8')
        )
    tpl = env.get_template('index.tpl');
    with open('index.html', 'wt') as fp:
        fp.write(tpl.render({
            "rich": args.rich,
            "debug": args.debug,
            "title": args.title,
            "images": images,
            "creation_time": datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            "generator_url": 'https://github.com/kazh98/risals',
            "generator_name": 'risals',
            "generator_version": __version__,
            }))
