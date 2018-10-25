from sanic import Sanic
from sanic import response

from urllib.request import urlopen
from cooltools import memcached_bin

from wand.image import Image

proxy_app = Sanic()


def _get_image(res,url):
    if res != '0x0':
       w,h = map(lambda x: int(x), res.split('x'))
    req = urlopen(url)
    retval = None
    fmt_str = 'jpeg'
    try:
       with Image(file=req) as img:
            if res != '0x0':
               if (w != img.width) or (h != img.height):
                  img.resize(w,h) 
            retval = img.make_blob()
            fmt_str = img.format
    finally:
       req.close()
    return retval,req.getheader('content-type','image/%s' % fmt_str)

get_image = memcached_bin(_get_image)

@proxy_app.middleware('request')
async def image(request):
      res = request.path.split('/')[1]
      url = request.path[len(res)+2:]
      img_data,img_type = get_image(res,url)
      return response.raw(img_data,content_type=img_type)

if __name__ == "__main__":

   proxy_app.run(host="0.0.0.0", port=8020)
