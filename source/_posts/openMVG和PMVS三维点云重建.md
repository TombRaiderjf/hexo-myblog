---
title: 利用openMVG和PMVS实现三维场景的点云重建
date: 2018-01-02 16:59:54
tags: 三维重建
categories: 编程学习
---

# openMVG与PMVS简介

## openMVG 

openMVG (Open Multiple View Geometry)：开源多视角立体几何库，这是一个cv界处理多视角立体几何的著名开源库，信奉“简单，可维护”，提供了一套强大的接口，每个模块都被测试过，尽力提供一致可靠的体验。

openMVG能够：
-	解决多视角立体几何的精准匹配问题；
-	提供一系列SfM需要用到的特征提取和匹配方法；
-	完整的SfM工具链（校正，参估，重建，表面处理等）；
-	openMVG尽力提供可读性性强的代码，方便开发者二次开发，核心功能是尽量精简的，所以你可能需要其它库来完善你的系统。openMVG分成了几个大的模块：

核心库：
-	各个功能的核心算法实现；
-	样例：教你怎么用；
-	工具链：也就是连起来用咯（乱序图像集的特征匹配，SfM，处理色彩和纹理）；

github地址：https://github.com/openMVG/openMVG 
使用文档：http://openmvg.readthedocs.io/en/latest/ 
## CMVS-PMVS

CMVS-PMVS（a modified version）：将运动结构（SfM）软件的输出作为输入，然后将输入图像分解成一组可管理大小的图像簇。 MVS软件可以用来独立和并行地处理每个簇，其中来自所有簇的重建不错过任何细节。

Github地址：https://github.com/pmoulon/CMVS-PMVS 

# Linux下配置环境：

*题外话：本来想在window上试一下，还暗自庆幸vs没卸，然而编译不过,win32,x64,release,debug...其实是我瞎了*

<img src="/img/openMVG.bmp" width=400>

## 安装openMVG：

从github克隆到本地（以及三个子模块）：

	$ git clone --recursive https://github.com/openMVG/openMVG.git

安装依赖：

	$ sudo apt-get install libpng-dev libjpeg-dev libtiff-dev libxxf86vm1 libxxf86vm-dev libxi-dev libxrandr-dev
编译：

	$ mkdir openMVG_Build
	$ cd openMVG_Build
	$ cmake -DCMAKE_BUILD_TYPE=RELEASE -DOpenMVG_BUILD_TESTS=ON -DOpenMVG_BUILD_EXAMPLES=ON . ../openMVG/src/
	$ make
	$ make test

## 安装PMVS/CMVS

从github克隆到本地：

	$ git clone https://github.com/pmoulon/CMVS-PMVS.git

安装依赖：

	$ sudo apt-get install libgtk2.0-dev libdevil-dev libboost-all-dev libatlas-cpp-0.6-dev libatlas-dev libcminpack-dev libgfortran3 libmetis-edf-dev libparmetis-dev freeglut3-dev libgsl0-dev

编译(cd到CMVS-PMVS/program/下)：

	$ mkdir build && cd build
	$ cmake ..
	$ make

会在build/main文件夹中生成三个可执行文件 cmvs、genOption、pmvs2

# 利用openMVG例程进行三维重建：

首先cd到openMVG_Build/software/SfM/文件夹中，在终端运行

	$ python tutorial_demo.py

它是封装了SfM pipeline的脚本，它先克隆文件夹ImageDataset_SceauxCastle到SfM文件夹中，作为图像输入
再生成一个tutorial_out文件夹保存输出结果
由于openMVG生成的是稀疏的点云，只含有它在图像中提取到的特征点的点云映射，所以需要用PMVS处理图像和位置的关系来得到稠密的点云。

SfM_Data是一个数据容器，储存在**sfm_data.bin**中，它包括（大概也就是二进制编码的结构）：

-	Views - 图像
-	Intrinsics – 相机内参数
-	Poses – 相机外参数
-	Landmarks – 三维点和它们的二维图像对应点

把SfM_Data转化为适用于PMVS输入格式的文件

	$ openMVG_main_openMVG2PMVS -i tutorial_out/reconstruction_global/sfm_data.bin -o tutorial_out/reconstruction_global

（官方文档写错了，害的我蒙圈好久）
在reconstruction_global文件夹中会生成PMVS文件夹
包含 models, txt, visualize 三个文件夹，models为空，txt包含11个对应图像的txt文档，每个里面都是一个3x4的矩阵，大概是相机位姿，visualize包含11张图像，不确定是原图像还是校正过的图像。
然后把CMPVS-PMVS编译后生成的pmvs2复制到SfM文件夹，运行

	$ pmvs2 tutorial_out/reconstruction_global /PMVS/pmvs_options.txt

PMVS/models文件夹中生成一个大小为15.2MB的pmvs_options.txt.ply点云文件，用meshlab打开即可看到重建出来的彩色稠密点云，还是很不错的效果。

例程用的是SfM标准的pipeline：
-	openMVG_Build/software/SfM/SfM_SequentialPipeline.py
-	openMVG_Build/software/SfM/SfM_GlobalPipeline.py

这两个脚本可以简单地通过下面的语句实现sfm（二选一）：

	$ python SfM_SequentialPipeline.py [full path image directory] [resulting directory]
	$ python SfM_GlobalPipeline.py [full path image directory] [resulting directory]

明天仔细研究一下SfM pipeline的各个步骤的接口，今天整理这个只是以防将来ubuntu崩掉还要重新装而走弯路

以及，昨天还尝试了Bundler+PMVS，效果不太好，而且对图片大小有限制，算是轻量级的吧，重建物体之类的比较合适，openMVG体量较大，二次封装了很多库，代码量让人望尘莫及...

参考：
[1] linux下使用Bundler + CMVS-PMVS进行三维重建 [http://blog.csdn.net/u013358387/article/details/7157666](http://blog.csdn.net/u013358387/article/details/7157666) 
[2] learn openMVG-安装和简介 [https://segmentfault.com/a/1190000007632252 ](https://segmentfault.com/a/1190000007632252 )
