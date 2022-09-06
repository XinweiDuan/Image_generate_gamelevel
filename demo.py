#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from lib.config import config as cfg
from lib.utils.nms_wrapper import nms
from lib.utils.test import im_detect
# from nets.resnet_v1 import resnetv1
from lib.nets.vgg16 import vgg16
from lib.utils.timer import Timer
# coding=utf-8
import cv2
import os
import glob
import numpy as np
import re
import paddlehub as hub
from xml.dom.minidom import parse

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')

NETS = {'vgg16': ('vgg16.ckpt',), 'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',), 'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}

test_img_path = []


def vis_detections(im, class_name, dets, im_file, im_size, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    #ax.imshow(im, aspect='equal')

    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
        )

        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

        destpath = "E:\\Pycharm\\Py_workspace\\Faste_rcnn3\\PaddleSeg\\output2\\result\\pseudo_color_prediction\\"

        cropped = im_file[int(bbox[1]): int(bbox[3]), int(bbox[0]):int(bbox[2])]
        cropname = destpath + "detectAnimal" + str(i) + ".jpg"
        cv2.imwrite(cropname, cropped)  # cropname是新的路径与文件名
        test_img_path.append(cropname)
        results = printFinalRes()
        curid = readXML(results[0], bbox)
        if (curid == -2):
            return

        nextid = curid + 1
        if '非动物' in results:
            print("已经剔除该物体")
            return
        writeXML(str(nextid), str(results[0]), str(bbox), str(im_size))




def demo(sess, net, image_path):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    #im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', image_name)
    im = cv2.imread(image_path)
    im_size = im.shape[0:2]
    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    ##调用im_detect函数对图片1进行分类和定位，即返回scores和boxes;预处理时把（375，500，3）reshape（600，800，3）
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.1
    NMS_THRESH = 0.1
    ##将4列box和1列类合并成5列，命名为dets;
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        ##对每一个类进行nms（非极大值抑制）操作，nms的阈值为0.3，返回keep（内含26个数据的list），即26个框;
        dets = dets[keep, :]
        ##dets取这26个框，然后调用vis_detections函数来画图;
        vis_detections(im, cls, dets, im, im_size, thresh=CONF_THRESH)


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='vgg16')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voc_0712')
    args = parser.parse_args()

    return args


def CutImg(imgpath, destpath):
    img = glob.glob(imgpath)
    img_len = int(len(img))
    # get all the images

    for i in range(img_len):
        temp = img[i].rstrip(".jpg")  # get image name to find its' annotation file.

        ori_img = cv2.imread(str(img[i]))
        sp = ori_img.shape  # obtain the image shape
        sz1 = sp[0]  # height(rows) of image
        sz2 = sp[1]  # width(colums) of image

        np.set_printoptions(suppress=True)
        txt = np.loadtxt(str(temp) + ".txt")  # load the pic's annotation, which is voc-style.
        if txt.shape[0] == 0:  # if the annotation is null, drop it.
            continue
        if np.ndim(txt) == 1:
            txt = txt.reshape(1, 5)

        txt_len = len(txt)
        # print(txt)
        # print(txt_len)
        for n in range(txt_len):  # get every object's coordinates in this image
            x1 = txt[n][0]
            y1 = txt[n][1]
            x2 = txt[n][2]
            y2 = txt[n][3]
            a = int(x1)  # x start
            b = int(x2)  # x end
            c = int(y1)  # y start
            d = int(y2)  # y end
            # print(a,b,c,d)
            res = ori_img[c:d, a:b]  # use opencv's function to cut the image.
            cv2.imwrite(destpath + str(i) + str(n) + '-29-6.jpg', res)


#检测动物的具体名称
def printFinalRes():
    module = hub.Module(name='resnet50_vd_animals')
    np_images = [cv2.imread(image_path) for image_path in test_img_path]
    results = module.classification(images=np_images)
    key_list = results[0].keys()
    print(list(results[0]))
    return list(results[0])

#比较两个框体是否检测同一目标
def calSameRec(bbox1,posStr):
    bbox2 = posStr.split()
    if bbox2[0] == '[':
        if abs(bbox1[0] - float(bbox2[1])) > 6.0:
            return False
        if abs(bbox1[1] - float(bbox2[2])) > 6.0:
            return False
        if abs(bbox1[2] - float(bbox2[3])) > 6.0:
            return False
        if abs(bbox1[3] - float(bbox2[4])) > 6.0:
            return False
    else:
        if abs(bbox1[0]-float(bbox2[0][1:])) > 6.0:
            return False
        if abs(bbox1[1]-float(bbox2[1])) > 6.0:
            return False
        if abs(bbox1[2]-float(bbox2[2])) > 6.0:
            return False
        if abs(bbox1[3]-float(bbox2[3])) > 6.0:
            return False

    return True

#读取文件信息
def readXML(result, bbox):
    domTree = parse("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\AnimalDetection.xml")
    # 文档根元素
    rootNode = domTree.documentElement
    #print(rootNode.nodeName)

    # 所有顾客
    animals = rootNode.getElementsByTagName("animal")
    #print("**** all Animals' information ****")
    curId=-1
    for animal in animals:
        if animal.hasAttribute("ID"):
            curId=int(animal.getAttribute("ID"))
            #print("ID:", animal.getAttribute("ID"))
            # animalcategory element
            animalcategory = animal.getElementsByTagName("AnimalCategory")[0]
            #print(animalcategory.nodeName, ":", animalcategory.childNodes[0].data)
            # detectionpos element
            detectionpos = animal.getElementsByTagName("DetectionPos")[0]
            # detectionpos = detectionpos.childNodes[0].data.strip('[]')
            #print(detectionpos.nodeName, ":", detectionpos.childNodes[0].data)

            #detectionpos已经为一整个字符串了
            #print(detectionpos.nodeName, ":", detectionpos.childNodes[0].data[0])
            if result == animalcategory.childNodes[0].data and calSameRec(bbox, detectionpos.childNodes[0].data):
                print("******检测到相同动物******")
                return -2

        else:
            print("**** No animals****")
    return curId

#写入文件信息
def writeXML(id, animalcategory, detectionpos, im_size):
    domTree = parse("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\AnimalDetection.xml")
    # 文档根元素
    rootNode = domTree.documentElement

    # 新建一个customer节点
    animal_node = domTree.createElement("animal")
    animal_node.setAttribute("ID", id)

    # 创建name节点,并设置textValue
    animalcategory_node = domTree.createElement("AnimalCategory")
    animalcategory_node.appendChild(domTree.createTextNode(animalcategory))  # 把文本节点挂到name_node节点
    animal_node.appendChild(animalcategory_node)

    # 创建phone节点,并设置textValue
    detectionpos_node = domTree.createElement("DetectionPos")
    detectionpos_node.appendChild(domTree.createTextNode(detectionpos))  # 把文本节点挂到name_node节点
    animal_node.appendChild(detectionpos_node)

    # 创建im_size节点,并设置textValue
    imageSize_node = domTree.createElement("ImageSize")
    imageSize_node.appendChild(domTree.createTextNode(im_size))  # 把文本节点挂到name_node节点
    animal_node.appendChild(imageSize_node)

    rootNode.appendChild(animal_node)

    with open("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\AnimalDetection.xml", 'w', encoding='utf-8') as f:
        domTree.writexml(f, addindent='\t', newl='\n', encoding='utf-8')



def detect_anmial(img_path):
    args = parse_args()

    # model path
    demonet = args.demo_net
    dataset = args.dataset
    tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', NETS[demonet][0])

    if not os.path.isfile(tfmodel + '.meta'):
        print(tfmodel)
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = False

    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    if demonet == 'vgg16':
        net = vgg16(batch_size=1)
    # elif demonet == 'res101':
    # net = resnetv1(batch_size=1, num_layers=101)
    else:
        raise NotImplementedError

    n_classes = len(CLASSES)
    # create the structure of the net having a certain shape (which depends on the number of classes)
    net.create_architecture(sess, "TEST", n_classes,
                            tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))

    # im_names = [img_path,]
    # for im_name in im_names:
    #     print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    #     print('Demo for data/demo/{}'.format(im_name))
    #     demo(sess, net, im_name)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Demo for data/demo/{}'.format(img_path))
    demo(sess, net, img_path)

