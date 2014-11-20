#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, io, urllib, re, time
from PIL import Image
from http.server import SimpleHTTPRequestHandler
import socketserver

PORT = 8000
IMAGE_FILE_REGEX = '^.+\.(png|jpg|jpeg|tif|tiff|gif|bmp)$'
IMAGES_PER_ROW = 3
IMAGES_PER_PAGE = 20
IMAGE_FILES = [] # Populated on startup.
THUMBNAIL_WIDTH = 400

class RequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        '''See parent (SimpleHTTPRequestHandler) for more info.'''
        # First thing we'll do is check whether
        # there is a query string. If page=N 
        # is in there, we serve a gallery (html) listing
        # several image thumbnails. Because there can be many images,
        # gallery is split into pages.
        #
        # If thumbnail=1 is in the query string, we generate a thumbnail
        # of the requested image file.
        query = self.parse_query(self.path)
        if 'page' in query:
            page = 1
            try:
                page = int(query['page'][0])
                page = min(page, 1 + (len(IMAGE_FILES) / IMAGES_PER_PAGE))
                page = max(page, 1)
            except:
                pass
            return self.list_files(page=page)
        if 'thumbnail' in query:
            return self.generate_thumbnail(self.path)
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return self.list_files(page=1)
        # At this point we know we need to serve the original
        # image file.
        f = None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None
        try:
            self.send_response(200)
            self.send_header("Content-type", self.guess_type(path))
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def list_files(self, page):
        enc = sys.getfilesystemencoding()
        # Inspired by https://github.com/unwitting/imageme
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '    <head>',
            '    <meta http-equiv="Content-Type" content="text/html; charset=%s">' % enc,
            '        <title>imageMee</title>'
            '        <style>',
            '            html, body {margin: 0; padding: 0;}',
            '            .header {text-align: left;}',
            '            .content {',
            '                padding: 3em;',
            '                padding-left: 4em;',
            '                padding-right: 4em;',
            '            }',
            '            .image {max-width: 100%; border-radius: 0.5em;}',
            '            td {width: ' + str(100.0 / IMAGES_PER_ROW) + '%;}',
            '        </style>',
            '    </head>',
            '    <body>',
            '    <div class="content">',
            '        <h2 class="header">Num images: ' + str(len(IMAGE_FILES)),
            '            <a href="/?page=' + str(page-1) + '">prev</a>',
            '            <a href="/?page=' + str(page+1) + '">next</a>',
            '        </h2>'
        ]
        table_row_count = 1
        html += ['<table>']
        for image_file in IMAGE_FILES[(page-1)*IMAGES_PER_PAGE : page*IMAGES_PER_PAGE]:
            if table_row_count == 1:
                html.append('<tr>')
            html += [
                '    <td>',
                '    <a href="' + image_file + '">',
                '        <img class="image" src="' + image_file + '?thumbnail=1">',
                '    </a>',
                '    </td>'
            ]
            if table_row_count == IMAGES_PER_ROW:
                table_row_count = 0
                html.append('</tr>')
            table_row_count += 1
        html += ['</tr>', '</table>']
        html += [
            '    </div>',
            '    </body>',
            '</html>'
        ]
        encoded = '\n'.join(html).encode(enc)
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def generate_thumbnail(self, path):
        path = self.translate_path(self.path)
        img = None
        try:
            img = Image.open(path)
        except IOError:
            self.send_error(404, "Error loading image file %s" % path)
            return None
        if img is None or img.format.lower() == 'gif':
            self.send_error(404, "Error generating thumbnail from %s" % path)
            return None
        img_width, img_height = img.size
        scale_ratio = THUMBNAIL_WIDTH / float(img_width)
        target_height = int(scale_ratio * img_height)
        try:
            img.thumbnail((THUMBNAIL_WIDTH, target_height), resample=Image.NEAREST)
        except IOError as exptn:
            self.send_error(404, "Error generating thumbnail from %s because %s" % (path, exptn))
            return None
        f = io.BytesIO()
        thumb_length = 0
        try:
            img.save(f, img.format)
            thumb_length = f.tell()
            f.seek(0)
        except:
            self.send_error(404, "Error using bytesio")
            return None
        self.send_response(200)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Content-Length", str(thumb_length))
        self.send_header("Last-Modified", self.date_time_string(time.time()))
        self.end_headers()
        return f

    def parse_query(self, path):
        parts = path.split('?', 1)
        if len(parts) == 1:
            return {}
        return urllib.parse.parse_qs(parts[1])

if __name__ == '__main__':
    print('Searching all image files in and below current directory...')
    for root, dirs, files in os.walk('.'):
        IMAGE_FILES.extend(os.path.join(root, f) for f in files if re.match(IMAGE_FILE_REGEX, f))
    print('Server up!')
    httpd = socketserver.TCPServer(("", PORT), RequestHandler)
    httpd.serve_forever()
