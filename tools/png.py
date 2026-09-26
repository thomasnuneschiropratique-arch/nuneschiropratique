"""Minimal dependency-free PNG read/write (8-bit RGB/RGBA, non-interlaced)."""
import zlib, struct

def read(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    pos, idat, pal, trns = 8, b'', None, None
    w = h = depth = ctype = None
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos+4])[0]; typ = d[pos+4:pos+8]
        data = d[pos+8:pos+8+ln]; pos += 12 + ln
        if typ == b'IHDR':
            w, h, depth, ctype, _, _, inter = struct.unpack('>IIBBBBB', data)
            assert depth == 8 and inter == 0, (depth, inter)
        elif typ == b'IDAT': idat += data
        elif typ == b'PLTE': pal = data
        elif typ == b'tRNS': trns = data
        elif typ == b'IEND': break
    raw = zlib.decompress(idat)
    nch = {0:1, 2:3, 3:1, 4:2, 6:4}[ctype]
    stride = w * nch
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if f == 1:
            for i in range(nch, stride): line[i] = (line[i] + line[i-nch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-nch] if i >= nch else 0
                b = prev[i]; c = prev[i-nch] if i >= nch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y*stride:(y+1)*stride] = line
        prev = line
    # normalise to RGBA
    px = bytearray(w*h*4)
    for i in range(w*h):
        if ctype == 6: px[i*4:i*4+4] = out[i*4:i*4+4]
        elif ctype == 2: px[i*4:i*4+3] = out[i*3:i*3+3]; px[i*4+3] = 255
        elif ctype == 0: v = out[i]; px[i*4:i*4+3] = bytes([v,v,v]); px[i*4+3] = 255
        elif ctype == 4: v = out[i*2]; px[i*4:i*4+3] = bytes([v,v,v]); px[i*4+3] = out[i*2+1]
        elif ctype == 3:
            idx = out[i]; px[i*4:i*4+3] = pal[idx*3:idx*3+3]
            px[i*4+3] = trns[idx] if trns and idx < len(trns) else 255
    return w, h, px

def write(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0); raw += px[y*w*4:(y+1)*w*4]
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)
    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    out += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    out += chunk(b'IEND', b'')
    open(path, 'wb').write(out)

def crop(w, h, px, x0, y0, x1, y1):
    nw, nh = x1-x0, y1-y0
    o = bytearray(nw*nh*4)
    for y in range(nh):
        s = ((y0+y)*w + x0)*4
        o[y*nw*4:(y+1)*nw*4] = px[s:s+nw*4]
    return nw, nh, o

def bbox(w, h, px, athr=8):
    x0, y0, x1, y1 = w, h, 0, 0
    for y in range(h):
        row = px[y*w*4:(y+1)*w*4]
        for x in range(w):
            if row[x*4+3] > athr:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    return x0, y0, x1+1, y1+1

def resize(w, h, px, nw, nh):
    """Box-filter downscale / bilinear upscale, premultiplied alpha."""
    o = bytearray(nw*nh*4)
    for yy in range(nh):
        sy0, sy1 = yy*h//nh, max(yy*h//nh+1, (yy+1)*h//nh)
        for xx in range(nw):
            sx0, sx1 = xx*w//nw, max(xx*w//nw+1, (xx+1)*w//nw)
            r=g=b=a=n=0
            for sy in range(sy0, sy1):
                base = sy*w*4
                for sx in range(sx0, sx1):
                    i = base+sx*4; al = px[i+3]
                    r += px[i]*al; g += px[i+1]*al; b += px[i+2]*al; a += al; n += 1
            i = (yy*nw+xx)*4
            if a: o[i]=r//a; o[i+1]=g//a; o[i+2]=b//a
            o[i+3] = a//n if n else 0
    return o
