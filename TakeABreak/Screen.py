import urllib3
import cv2
import numpy as np
from io import BytesIO


class Screen:
    def __init__(self):
        self.url = 'https://uploadbeta.com/api/pictures/random/?key=BingEverydayWallpaperPicture'
        self.http = urllib3.PoolManager()
        self.window_name = 'Take A Break'

    def DownloadImage(self):
        res = self.http.request('GET', self.url)
        im = np.asarray(bytearray(res.data))
        image = cv2.imdecode(im, cv2.IMREAD_COLOR)
        return image

    def Show(self):
        image = self.DownloadImage()
        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        # cv2.moveWindow(self.window_name, -1, -1)
        cv2.imshow(self.window_name, image)
        cv2.waitKey()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    screen = Screen()
    screen.Show()
