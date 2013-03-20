def img_el(attrs):
    chunks = ["<img"]
    for attr, value in attrs.iteritems():
        chunks.append(' %s="%s"' % (attr, value))
    chunks.append(" />")
    return "".join(chunks)

def image_type_supported(file_or_path, close=False):
    # Try to import PIL in either of the two ways it can end up installed.
    try:
        from PIL import ImageFile as PILImageFile
    except ImportError:
        import ImageFile as PILImageFile

    p = PILImageFile.Parser()
    if hasattr(file_or_path, 'read'):
        file = file_or_path
        file_pos = file.tell()
        file.seek(0)
    else:
        file = open(file_or_path, 'rb')
        close = True
    try:
        # Most of the time PIL only needs a small chunk to parse the image and
        # get the dimensions, but with some TIFF files PIL needs to parse the
        # whole file.
        chunk_size = 1024
        while 1:
            data = file.read(chunk_size)
            if not data:
                break
            p.feed(data)
            if p.image:
                return True
            chunk_size = chunk_size*2
        return False
    finally:
        if close:
            file.close()
        else:
            file.seek(file_pos)
