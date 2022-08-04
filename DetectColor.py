import cv2
import numpy as np
from xml.dom.minidom import parse

from export import parse_args

treeLower = np.array([0, 0, 191]) #设定红色阈值，HSV空间
treeUpper = np.array([0,0,193])

houseLower = np.array([0, 127, 127]) #设定红色阈值，HSV空间
houseUpper = np.array([0,129,129])

fenceLower = np.array([127, 0, 127]) #设定红色阈值，HSV空间
fenceUpper = np.array([129,0,129])

def readXML():
    domTree = parse("./OtherDetection.xml")
    # 文档根元素
    rootNode = domTree.documentElement
    print(rootNode.nodeName)

    # 所有顾客
    items = rootNode.getElementsByTagName("item")
    print("**** all Detections' information ****")
    curId=-1
    for item in items:
        if item.hasAttribute("ID"):
            curId=int(item.getAttribute("ID"))
            print("ID:", item.getAttribute("ID"))
            # animalcategory element
            CompName = item.getElementsByTagName("CompName")[0]
            print(CompName.nodeName, ":", CompName.childNodes[0].data)
            # detectionpos element
            detectionpos = item.getElementsByTagName("DetectionPos")[0]
            print(detectionpos.nodeName, ":", detectionpos.childNodes[0].data)
        else:
            print("**** No animals****")
    return curId


def writeXML(id, CompName, detectionpos,index):
    domTree = parse("./OtherDetection.xml")
    # 文档根元素
    rootNode = domTree.documentElement

    # 新建一个customer节点
    comp_node = domTree.createElement("item")
    comp_node.setAttribute("ID", str(id))

    # 创建name节点,并设置textValue
    CompName_node = domTree.createElement("CompName")
    # 把文本节点挂到name_node节点
    CompName_node.appendChild(domTree.createTextNode(CompName))
    comp_node.appendChild(CompName_node)

    # 创建phone节点,并设置textValue
    detectionpos_node = domTree.createElement("DetectionPos")
    detectionpos_node.appendChild(domTree.createTextNode(detectionpos))  # 把文本节点挂到name_node节点
    comp_node.appendChild(detectionpos_node)

    rootNode.appendChild(comp_node)

    with open('OtherDetection.xml', 'w', encoding='utf-8') as f:
        domTree.writexml(f, addindent='\t', newl='\n', encoding='utf-8')

def Detection(img , index):
    nccomps = cv2.connectedComponentsWithStats(img)
    _ = nccomps[0]
    # 标记图，图中不同连通域使用不同的标记（当前像素是第几个轮廓），和原图宽高一致；
    labels = nccomps[1]
    # (x, y, width, height, area)，即每个区域的每个区域的左上角坐标,宽和高，面积
    status = nccomps[2]
    # 每个连通区域的中心点
    centroids = nccomps[3]

    for row in range(status.shape[0]):
        if status[row, :][0] == 0 and status[row, :][1] == 0:
            background = row
        else:
            continue
    status_no_background = np.delete(status, background, axis=0)

    # arr[:,4]代表取到每一个arr[][4]，并形成一个数组
    rec_value_max = np.asarray(status_no_background[:, 4].max())
    # 取到status_no_background[:,4]最大位置的索引
    re_value_max_position = np.asarray(status_no_background[:, 4].argmax())

    h = np.asarray(labels, 'uint8')
    h[h == (re_value_max_position + 1)] = 255
    curId = readXML()
    for single in range(centroids.shape[0]):
        # 去除背景
        if status[single, :][0] == 0 and status[single, :][1] == 0:
            continue
        # 检测房子
        if status[single, :][4] <= 10000 and index == 1:
            continue
        else:
            curId = curId + 1
            print(tuple(map(int, centroids[single])))
            position = tuple(map(int, centroids[single]))
            cv2.circle(h, position, 5, (128, 0, 128), thickness=0, lineType=8)
            compname = "tree"
            if index == 0:
                writeXML(curId, compname, str(centroids[single]), index)
            if index == 1:
                compname="house"
                writeXML(curId, compname, str(centroids[single]), index)
            if index == 2:
                compname="fence"
                writeXML(curId, compname, str(centroids[single]), index)

    readXML()
    cv2.imshow('h', h)
    # cv2.imshow('im_bw',thresh)
    # cv2.imshow('im_origin',im)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detectColor():
    im = cv2.imread("E:/Pycharm/Py_workspace/Faste_rcnn3/PaddleSeg/output2/result/pseudo_color_prediction/2.png")
    w, h, n = im.shape
    # im_gray = cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    # cv2.imshow('gray',im_gray)
    # _,thresh = cv2.threshold(im_gray,90,255,cv2.THRESH_BINARY)

    im_tree = cv2.inRange(im, treeLower, treeUpper)  # lower20===>0,upper200==>0,
    im_house = cv2.inRange(im, houseLower, houseUpper)
    im_fence = cv2.inRange(im, fenceLower, fenceUpper)

    # 调用函数
    index = 0
    while (index < 3):
        if index == 0:
            Detection(im_tree, index)
        if index == 1:
            Detection(im_house, index)
        if index == 2:
            Detection(im_fence, index)
        index = index + 1




