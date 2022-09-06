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
    domTree = parse("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\OtherDetection.xml")
    # 文档根元素
    rootNode = domTree.documentElement
    #print(rootNode.nodeName)

    # 所有顾客
    items = rootNode.getElementsByTagName("item")
    #print("**** all Detections' information ****")
    curId=-1
    for item in items:
        if item.hasAttribute("ID"):
            curId=int(item.getAttribute("ID"))
            #print("ID:", item.getAttribute("ID"))
            # animalcategory element
            CompName = item.getElementsByTagName("CompName")[0]
            #print(CompName.nodeName, ":", CompName.childNodes[0].data)
            # detectionpos element
            detectionpos = item.getElementsByTagName("DetectionPos")[0]
            #print(detectionpos.nodeName, ":", detectionpos.childNodes[0].data)
        else:
            print("**** No animals****")
    return curId

def writeXML(id, CompName, detectionpos, index ,im_size, fence_width=0):
    domTree = parse("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\OtherDetection.xml")
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

    # 创建im_size节点,并设置textValue
    imageSize_node = domTree.createElement("ImageSize")
    imageSize_node.appendChild(domTree.createTextNode(im_size))  # 把文本节点挂到name_node节点
    comp_node.appendChild(imageSize_node)

    if(fence_width!= 0):
        # 创建im_size节点,并设置textValue
        FenceWidth_node = domTree.createElement("FenceWidth")
        FenceWidth_node.appendChild(domTree.createTextNode(str(fence_width)))  # 把文本节点挂到name_node节点
        comp_node.appendChild(FenceWidth_node)

    rootNode.appendChild(comp_node)

    with open("E:\\unity_libary\\Farm\\Farm\\Assets\\Resources\\Cfg\\OtherDetection.xml", 'w', encoding='utf-8') as f:
        domTree.writexml(f, addindent='\t', newl='\n', encoding='utf-8')

def Detection(img , index, im_size):
    nccomps = cv2.connectedComponentsWithStats(img)
    _ = nccomps[0]
    # 标记图，图中不同连通域使用不同的标记（当前像素是第几个轮廓），和原图宽高一致；
    labels = nccomps[1]
    # (x, y, width, height, area)，即每个区域的每个区域的左上角坐标,宽和高，面积
    status = nccomps[2]
    #记录联通区域的宽度
    width = (status[:,2])
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
        if status[single, :][4] <= 10000 and index == 2:
            continue
        else:
            curId = curId + 1
            position = tuple(map(int, centroids[single]))
            cv2.circle(h, position, 5, (128, 0, 128), thickness=0, lineType=8)
            compname = "tree"
            if index == 0:
                writeXML(curId, compname, str(centroids[single]), index, str(im_size))
            if index == 1:
                compname="house"
                writeXML(curId, compname, str(centroids[single]), index, str(im_size))
            if index == 2:
                compname="fence"
                writeXML(curId, compname, str(centroids[single]), index, str(im_size), (status[single, :][2]))

        readXML()
    # cv2.imshow('h', h)
    # cv2.waitKey(0)


def detectColor(img_name):
    img_path="E:\\Pycharm\\Py_workspace\\Faste_rcnn3\\PaddleSeg\\output2\\result\pseudo_color_prediction\\"+img_name+".png"
    print(img_path)
    im = cv2.imread(img_path)
    im_size = im.shape[0:2]
    # im_gray = cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    # cv2.imshow('gray',im_gray)
    # _,thresh = cv2.threshold(im_gray,90,255,cv2.THRESH_BINARY)
    destpath = "E:\\Pycharm\\Py_workspace\\Faste_rcnn3\\PaddleSeg\\output2\\result\\pseudo_color_prediction\\"
    savename = destpath + "detectAnimal.jpg"

    im_tree = cv2.inRange(im, treeLower, treeUpper)  # lower20===>0,upper200==>0,
    cv2.imwrite(destpath+"tree.jpg", im_tree)
    im_house = cv2.inRange(im, houseLower, houseUpper)
    cv2.imwrite(destpath + "house.jpg", im_house)
    im_fence = cv2.inRange(im, fenceLower, fenceUpper)
    cv2.imwrite(destpath + "fence.jpg", im_fence)

    # 调用函数
    index = 0
    while (index < 3):
        if index == 0:
            Detection(im_tree, index, im_size)
        if index == 1:
            Detection(im_house, index, im_size)
        if index == 2:
            Detection(im_fence, index, im_size)
        index = index + 1




