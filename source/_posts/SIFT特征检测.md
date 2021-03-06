---
title: SIFT特征检测
date: 2017-10-22 22:25:43
tags: SIFT特征
categories: 机器视觉
mathjax: true
---

*SIFT（Scale-invariant Feature Transform）*
# SIFT特征检测的特点

* 对旋转，尺度缩放，亮度变化保持不变性，对视角变化，仿射变换，噪声也保持一定程度的稳定性
* 信息量丰富，适用于在海量特征数据库中进行匹配
* 多量性，少数物体也可以产生大量SIFT特征
* 高速性，经优化的SIFT匹配算法甚至可以达到实时性

# SIFT特征检测的步骤

1.	检测尺度空间的极值点
2.	精确定位特征点
3.	设定特征点的方向参数
4.	生成特征点的描述子（128维向量）

## 检测尺度空间的极值点

### 什么是尺度（Scale）？

直观地来说，对于一张4K分辨率的照片而言，如果它的像素数目被不断压缩（或者观察者距离照片越来越远），它将逐渐变得模糊，而这个导致照片的呈现内容发生变化的连续的自变量就可以称为尺度。人类知觉中的一种现象可以作为一个例子——整体优先效应。观察距离远的时候，看到的是小字母组成的大字母，而距离近的时候，看到的则是小字母们。因此，对物体观察的尺度不同，物体呈现的方式也不同。对计算机视觉而言，无法预知某种尺度的物体结构是否有意义，因此有必要将所有尺度的结构表示出来。
<img src="/img/整体优先效应.png" width="300">

### 尺度空间

通过尺度空间理论模拟图像数据的多尺度特征，做特征检测的目的是找到图像中稳定而又明确的一些特征量（类似矩阵特征值的感觉），那么从对图像直观的理解来看，它的确有这样一些特征，尤其是让人判断两幅图片拍摄的是否为同一个场景时，他绝不是挨个像素做比较的
高斯函数是实现尺度变换的唯一线性核（其他核会对图像造成模糊之外的其他影响），xy是尺度坐标，$\sigma$决定图像的平滑程度，越大越平滑
$$L(x,y,\sigma)=I(x,y)*g(x,y,\sigma), \quad g(x,y,\sigma)=\frac{1}{2\pi \sigma^2} e^{-\frac{x^2+y^2}{2 \sigma^2}}$$
**高斯差分（DoG）尺度空间**——用于在尺度空间中检测稳定的关键点，下图左是高斯尺度空间，从下到上按照$\sigma$递减的顺序排列，右侧是将相邻尺度的图像做差得到的差分尺度空间
$$D(x,y,\sigma)=(g(x,y,k \sigma)-g(x,y,\sigma))*I(x,y)=L(x,y,k \sigma)-L(x,y,\sigma)$$
<img src="/img/差分尺度空间.png" width="500">


### 步骤

**构建图像金字塔**，金字塔的数目和每个塔的层数（一般3-5层）由图像的尺寸决定，图像像素越多自然可以分更多个塔。左侧分别为三组按尺度顺序排列的高斯尺度空间，塔每增加一个，图像尺寸缩减为1/4，第二塔的第一层由第一塔的第四层将采样得到，以此类推得到每一个塔的第一层，右侧是相邻尺度的图像的差分结果，即为所需的尺度空间
<img src="/img/图像金字塔.png" width="500">

**极值点检测**——在构造的差分尺度空间中检测局部极大值/极小值点
如下图所示检测尺度空间中的每个像素点，与其同尺度的八个相邻点，上下相邻尺度对应的18个点，共26个点进行比较，以确保在尺度空间和二维图像空间都是极值点
<img src="/img/检测极值点.png" width="300">
描述极值点：$(x,y,\sigma)$二维图像坐标和尺度空间坐标

## 精确定位特征点

### 精确定位极值点

$D(x,y,\sigma)$表示高斯差分尺度空间的值，设$X=\begin{bmatrix} x&y& \sigma \end{bmatrix} ^T$，从原点泰勒展开，取三项，得到$D(X)=D+\frac{\partial	D}{\partial X} X+\frac{1}{2} X^T \frac{\partial^2 D}{\partial X^2}X$
令D(X)的一阶导数为0，获取精确的极值点 $\hat{X}=-\frac{\partial D}{\partial X} (\frac{\partial^2 D}{\partial X^2})^{-1}$
即为求解线性方程组(用差分近似偏导数，因此金字塔要再多两层以计算二阶差分)
$$\begin{bmatrix} \frac{\partial^2 D}{\partial x^2}& \frac{\partial^2 D}{\partial xy}&\frac{\partial^2 D}{\partial x\sigma}\\ \frac{\partial^2 D}{\partial yx}&\frac{\partial^2 D}{\partial y^2}&\frac{\partial^2 D}{\partial y\sigma}\\ \frac{\partial^2 D}{\partial \sigma x}&\frac{\partial^2 D}{partial \sigma y}&\frac{\partial^2 D}{\partial \sigma^2}\\ \end{bmatrix} \begin{bmatrix} x\\y\\ \sigma \\ \end{bmatrix}=-\begin{bmatrix} \frac{\partial D}{\partial x}\\ \frac{\partial D}{\partial y}\\\frac{\partial D}{\partial \sigma}\\ \end{bmatrix}$$
如果X在任何维度上大于0.5，表示极值点更接近另一个采样点，在该点重复计算

### 去除不稳定的极值点

不稳定的点就是对比度低的点，可能光线或其他外部条件改变后，就无法检测到该极值点，就转换为去除D(X)上值较小的极值点，将$\hat{X}$带入D(X)得到下式
$$D(\hat{X})=D+\frac{1}{2} \frac{\partial D^T}{\partial X}\hat{X}$$
若$|D(\hat{X})|\geq 0.03$，则保留该点，否则去除

### 去除边缘响应过大的极值点

在SIFT中，DOG算子近似拉普拉斯算子，对边缘都有很强的检测效果，那当然需要从这些特征点中删除哪些是具有强边缘效应的点，以保证SIFT特征的旋转不变性。
方法：通过主曲率分析除去边缘响应过大的极值点，计算差分图像D的Hessian矩阵$H=\begin{bmatrix} D_{xx}&D_{xy}\\D_{xy}&D_{yy}\\ \end{bmatrix}$
保留满足以下条件的极值点：$\frac{trace(H)^2}{det(H)}<\frac{(r+1)^2}{r}$(取r=10)，直观理解就是H的两个特征值不能相差过大

## 设定特征点的方向参数

确定特征点X后，选取特征点所在尺度的图像，**计算其邻域像素的梯度**
模值：$m(x,y)=\sqrt{(L(x+1,y)-L(x-1,y))^2+(L(x,y+1)-L(x,y-1))^2}$
方向角：$\theta(x,y)=\arctan \frac{L(x,y+1)-L(x,y-1)}{L(x+1,y)-L(x-1,y)}$
然后通过**邻域的梯度方向直方图**确定特征点的方向参数
<img src="/img/特征点方向.png" width="300">
梯度直方图的范围是[0,360)，可以按照36°一个柱形来划分10个范围，特征点的主方向是取其中的峰值所对应的角度，特征点的辅助方向是直方图中超过主方向峰值80%的次峰值
方向参数确保了SIFT特征的旋转不变性，因为特征点的主方向相对于像素的梯度方向不变。

## 生成特征点的描述子

在4x4的小块上计算梯度方向直方图（取八个方向），形成累计值的种子点，下图详细示意了2x2个小块的形成过程
<img src="/img/特征点描述子.png" width="400">
下图是最终生成的128维特征向量，一共需要特征点邻域为16x16的范围计算，同时使用高斯下降函数降低远离中心的小块的权重，最后将特征向量作归一化以去除光照影响
<img src="/img/128维特征向量.jpg" width="600">
*得到了两张图像的所有描述子，就可以直接将它们进行匹配，匹配上就说明特征点相互match*

参考文献：
http://blog.csdn.net/tanxinwhu/article/details/7048370
http://blog.csdn.net/abcjennifer/article/details/7639681/