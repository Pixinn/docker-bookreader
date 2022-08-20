#!/usr/bin/env python3

import argparse
import sys
import os
import shutil
import json
from PIL import Image
from PIL import UnidentifiedImageError

if __name__ == '__main__':

    # Copy the "page" files
    SRC = "/book"
    DST = "/data"
    images = os.listdir(SRC)
    if len(images) != 0:
        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        for i in range(len(images)):        
            srcImage = os.path.join(SRC, images[i])
            dstImage = os.path.join(DST, "pages", images[i].replace(' ', '_'))
            shutil.copyfile(srcImage, dstImage)
            images[i] = dstImage

        # Build the page list in JSON ("data" field)
        options = dict();
        data = []
        for image in images:
            # Get image size
            try:
                img = Image.open(image)
                # Build page description
                page = dict()
                page["width"] = int(img.width)
                page["height"] = int(img.height)
                page["uri"] = "pages/" + os.path.basename(image)
                data.append([page])
            except UnidentifiedImageError as e:
                print("Warning: {}".format(e))
        options["data"] = data
        
        # Other fields
        options["bookUrl"] = "index.html"
        options["bookTitle"] = ""
        options["thumbnail"] =  "pages/" + os.path.basename(images[0])
        options["imagesBaseURL"] = "BookReader/images/"
        options["ui"] = "full"
        options["el"] = "#BookReader"
        
        # Build javascript
        jsPart1 = '''
    function instantiateBookReader(selector, extraOptions) {
        selector = selector || '#BookReader';
        extraOptions = extraOptions || {};
        var options = '''
        jsPart2 = ''';
        $.extend(options, extraOptions);
        var br = new BookReader(options);
        br.init();
    }
        '''
        javascript = jsPart1 + json.dumps(options) + jsPart2

        # Write js to file
        with open(os.path.join(DST, "BookReaderJSSimple.js"), 'w') as file:
            file.write(javascript)

        # copy bookreader files
        shutil.copytree("/bookreader/BookReader", os.path.join(DST, "BookReader"), dirs_exist_ok=True)
        shutil.copytree("/bookreader/BookReaderDemo/assets", os.path.join(DST, "assets"), dirs_exist_ok=True)
        shutil.copyfile("BookReaderDemo/demo-vendor-fullscreen.html", os.path.join(DST, "index.html"))

    else:
        print("No image in directory {}".format(SRC))

    sys.exit(0)
