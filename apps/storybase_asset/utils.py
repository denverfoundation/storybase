def img_el(attrs):
    chunks = ["<img "]
    for attr, value in attrs.iteritems():
        chunks.append(' %s="%s"' % (attr, value))
    chunks.append(" />")
    return "".join(chunks)
