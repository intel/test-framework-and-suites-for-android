#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?

SPDX-License-Identifier: Apache-2.0
'''
import os
import time
from PIL import Image
from testlib.util.common import g_common_obj
from testlib.multimedia.base import getTmpDir


class OTCImage():

    def __init__(self):
        self.d = g_common_obj.get_device()

    def __make_regalur_image(self, img, size=(256, 256)):
        return img.resize(size).convert('RGB')

    def __split_image(self, img, part_size=(64, 64)):
        w, h = img.size
        pw, ph = part_size

        assert w % pw == h % ph == 0

        return [img.crop((i, j, i + pw, j + ph)).copy()
                for i in xrange(0, w, pw)
                for j in xrange(0, h, ph)]

    def __hist_similar(self, lh, rh):
        assert len(lh) == len(rh)
        return sum(1 - (0 if l1 == r else float(abs(l1 - r)) / max(l1, r)) for l1, r in zip(lh, rh)) / len(lh)

    def __calc_similar(self, li, ri):
        return sum(self.__hist_similar(l.histogram(),
                   r.histogram()) for l, r in zip(self.__split_image(li), self.__split_image(ri))) / 16.0

    # git ssim between picA and picB
    def calc_similar_by_path(self, lf, rf, median=4):
        li, ri = self.__make_regalur_image(Image.open(lf)), self.__make_regalur_image(Image.open(rf))
        return ("%." + str(median) + "f") % self.__calc_similar(li, ri)

    # git ssim between picA and picB
    def calc_similar_by_path_box(self, lf, rf, box, median=4):
        im1 = Image.open(lf).crop(box)
        im2 = Image.open(rf).crop(box)
        li, ri = self.__make_regalur_image(im1), self.__make_regalur_image(im2)
        return ("%." + str(median) + "f") % self.__calc_similar(li, ri)

    # git ssim between picA and picB
    def calc_similar(self, im1, im2, median=4):
        if im1 is None or im2 is None:
            return 0
        li, ri = self.__make_regalur_image(im1), self.__make_regalur_image(im2)
        return ("%." + str(median) + "f") % self.__calc_similar(li, ri)

    # git ssim DATA between picA and picB
    def make_doc_data(self, lf, rf):
        li, ri = self.__make_regalur_image(Image.open(lf)), self.__make_regalur_image(Image.open(rf))
        li.save(lf + '_regalur.png')
        ri.save(rf + '_regalur.png')
        fd = open('stat.csv', 'w')
        fd.write('\n'.join(l + ',' + r for l, r in zip(map(str, li.histogram()), map(str, ri.histogram()))))
        fd.close()
        import ImageDraw
        li = li.convert('RGB')
        draw = ImageDraw.Draw(li)
        for i in xrange(0, 256, 64):
            draw.line((0, i, 256, i), fill='#ff0000')
            draw.line((i, 0, i, 256), fill='#ff0000')
        li.save(lf + '_lines.png')

    def screenshot(self, filename="screenshot.png"):
        return self.d.screenshot(filename)

    def saveImage(self, device, fileName=os.path.join(getTmpDir(), "savescreen.png")):
        print "saveImage"
        path = self.screenshot(fileName)
        print "screenshot,path is [%s]" % path
        return path

    def getWidgetImage(self, device, widget, imageName='widgetImage.png', save=False):
        imageName = str(time.time()) + "_" + imageName
        path = self.saveImage(device)
        img = Image.open(path)
        box = widget.bounds
        box = (box.get('left'), box.get('top'), box.get('right'), box.get('bottom'))
        img = img.crop(box)
        if save:
            img.save(imageName)
        os.system("rm -rf " + path)
        return img

    def getPicByCoor(self, device, x, y, w, h, imageName="savescreen.png", save=False):
        path = self.saveImage(device)
        print path
        img = Image.open(path)
        box = (x, y, x + w, y + h)
        img = img.crop(box)
        if save:
            path = img.save(imageName)
            print "screenshot, path is [%s]" % path
        return img

    def cropScreenShot(self, device, box, imageName="savescreen.png", save=False):
        if box is not None:
            return self.getPicByCoor(device, box[0], box[1], box[2], box[3], imageName, save)

    def openBoxImage(self, path):
        if path is not None:
            return Image.open(path)


otcImage = OTCImage()
