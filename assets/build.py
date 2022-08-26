#!/usr/bin/env python3

import argparse
import sys
import os
import shutil
import base64
import json
from PIL import Image
from PIL import UnidentifiedImageError



SRC = "/book"
DST = "/data"



if __name__ == '__main__':

    # Copy the "page" files
    files = os.listdir(SRC)
    images = []
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')): # todo better filtering
            images.append(file)
    if len(images) != 0:

        options = dict();
        data = []

        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        for i in range(len(images)):  
            srcImage = os.path.join(SRC, images[i])
            urlSafeEncodedBytes = base64.urlsafe_b64encode(images[i].encode("utf-8"))
            urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8")
            dstImage = os.path.join(DST, "pages", urlSafeEncodedStr)
            dstImage = os.path.splitext(dstImage)[0] + ".webp"

            try:
                print("Processing {} => {}".format(images[i], dstImage), flush=True)
                # Save the images
                img = Image.open(srcImage).convert("RGB")
                img.save(dstImage, format="WEBP", quality=50)
                images[i] = dstImage
                # Build page description
                page = dict()
                page["width"] = int(img.width)
                page["height"] = int(img.height)
                page["uri"] = "pages/" + os.path.basename(dstImage)
                data.append([page])

            except Exception as e:
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
