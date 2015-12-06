from StringIO import StringIO

def serve_pil_image(pil_img, format="jpeg"):
    img_io = StringIO()
    pil_img.save(img_io, format.upper())
    img_io.seek(0)
    return send_file(img_io, mimetype='image/%s' % (format.lower()))
