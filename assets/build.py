#!/usr/bin/env python3

import argparse
import sys
import os
import json
from PIL import Image

if __name__ == '__main__':

    # Rename the "page" files
    # SRC = "/data/pages/"
    SRC = "/book"
    DST = "/data"
    images = os.listdir(SRC)
    if len(images) != 0:
        for i in range(len(images)):        
            oldName = os.path.join(SRC, images[i])
            newName = os.path.join(SRC, images[i].replace(' ', '_'))
            os.rename(oldName, newName)
            images[i] = newName

        # Build the page list in JSON ("data" field)
        options = dict();
        data = []
        for image in images:
            # Get image size
            img = Image.open(image)
            # Build page description
            page = dict()
            page["width"] = int(img.width)
            page["height"] = int(img.height)
            page["uri"] = "pages/" + os.path.basename(image)
            data.append([page])
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
    
    else:
        print("No image in directory {}".format(SRC))

    sys.exit(0)
