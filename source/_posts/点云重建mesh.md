---
title: 点云重建mesh
date: 2018-01-04 20:51:35
tags:
categories: 编程学习
---

点云重建mesh是个很头疼的过程，就meshlab中的方法说说.

**[Screened Poisson Surface](http://hhoppe.com/proj/screenedpoisson/)**：有向点集生成封闭曲面，简单地从二维来看，就是四叉树确定边界，三维空间中，就是八叉树确定表面，其中八叉树深度（octree depth）决定了重建得到曲面的分辨率，重建mesh的face数目随depth指数增长，重建时间也是如此。我理解的不够深入，还是贴上别人写的分析吧 -> [泊松曲面重建](http://blog.csdn.net/jennychenhit/article/details/52126156?locationNum=8).此方法的弊端是要形成封闭的曲面，这就不可避免地产生了一些奇怪的凸包，以及周围噪点带来的曲面的过度延伸，进一步增加了face的数目，从例程得到的点云包含241717个有向点，按默认depth=8重建得到的mesh含有123479个face，把mesh导入blender，密集恐惧症都快有了。如果用在大规模场景中，简直是灾难；而把depth降低到7则损失大量细节，完全是天壤之别！！


<img src="/img/mesh0 (1).png" width=500>
<img src="/img/mesh0 (2).png" width=500>

困扰我的问题是，以mesh描述物体的表面本不需要如此多的face，有些本该是棱角分明的地方，重建出来的反而是弧状的细细密密的face拼接而成的，浪费了很多计算时间，而且丧失了准确度。估计一下，如果手动建模的话例程的城堡正面连一万个face都用不上。

----

**1月5日更新**

例程重建出的点云利用泊松曲面重建得到的结果

<img src="/img/castle.bmp">

**PCL开源点云库**：看了几个用pcl处理点云重建mesh的例子，原来，用深度图建出来的点云并不是那末稠密，分布很是均匀，建出来的mesh也比较漂亮，只靠RGB还是不够的。


**[Kinect Fusion](https://msdn.microsoft.com/zh-cn/library/dn188670.aspx)** 利用kinect for windows 扫描物体建模，这不就是那个infinTAM的官方升级版嘛！而且原生支持C++ AMP DirectX11,A 卡N卡等软硬件，为什么我没有早发现！这两篇博文[1](http://blog.csdn.net/xiaohu50/article/details/51592503) [2](https://www.cnblogs.com/yangecnu/p/3428647.html) 里根据官方文档介绍了kinect fusion的pipeline。重建生成的是体素（volume），可以导出obj，stl等mesh格式。

On GPUs the maximum contiguous memory block that can typically be allocated is around 1GB, which limits the reconstruction resolution to approximately 640^3 (262144000 voxels). Similarly, although CPUs typically have more total memory available than a GPU, heap memory fragmentation may prevent very large GB-sized contiguous memory block allocations.. If you need very high resolution also with a large real world volume size, multiple volumes or multiple devices may be a possible solution.

GPU 一般能分配的最大连续存储单元大约1GB，这就限制了重建的分辨率大约在640^3的体素数目。相似地，尽管CPU一般比GPU有更大的可用内存，堆内存的碎片可能会阻止过大GB量级的连续内存分配。如果你既需要非常高的分辨率，真实世界尺寸又很大，多场景或多设备可能是个可能的解决方案。总的来说，意思就是要不多弄几台kinect，要不把场景分为几个部分分别进行重建(还tm说的这么委婉...)


