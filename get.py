from wx.core import *


def image(path) -> Bitmap:
    return wx.Image(path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()


def scaled(bitmap: Bitmap, scale=1) -> Bitmap:
    image = ImageFromBitmap(bitmap)
    w, h = image.GetSize()
    image = image.Scale(w * scale, h * scale, wx.IMAGE_QUALITY_HIGH)
    result = BitmapFromImage(image)
    return result
