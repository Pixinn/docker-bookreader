FROM node:latest AS bookreader

# Prepare repository
RUN git clone https://github.com/internetarchive/bookreader.git /bookreader
RUN ["/bin/bash", "-c", "cd /bookreader && git checkout v5.0.0-45"]
RUN export NODE_OPTIONS=--openssl-legacy-provider

# Build bookreader
WORKDIR /bookreader
ENV NODE_OPTIONS="--openssl-legacy-provider"
RUN ["/bin/bash", "-c", "cd /bookreader && npm install"]
RUN ["/bin/bash", "-c", "cd /bookreader && npm run build --verbose"]

# Copy files to be served
#RUN cp -r BookReader ../data/
#RUN cp -r BookReaderDemo/assets ../data/
#RUN cp BookReaderDemo/demo-vendor-fullscreen.html ../data/index.html
#RUN cp BookReaderDemo/BookReaderJSSimple.js ../data

# Tune script to serve from /data
RUN sed -i "s|npx http-server . --port 8000|npx http-server ../data --port 8000|g" package.json
RUN sed -i "s|../BookReader/|BookReader/|g" BookReaderDemo/demo-vendor-fullscreen.html


# Install the Python script to build the book
RUN apt update
RUN apt install -y python3-pip
RUN pip3 install pillow
ADD assets/build.py /build.py
