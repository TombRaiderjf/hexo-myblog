---
title: 点云重建mesh
date: 2018-01-04 20:51:35
tags:
---

点云重建mesh是个很头疼的过程，就meshlab中的方法说说.

[Screened Poisson Surface](http://hhoppe.com/proj/screenedpoisson/)：有向点集生成封闭曲面，简单地从二维来看，就是四叉树确定边界，三维空间中，就是八叉树确定表面，其中八叉树深度（octree depth）决定了重建得到曲面的分辨率，重建mesh的face数目随depth指数增长，重建时间也是如此。我理解的不够深入，还是贴上别人写的分析吧 -> [泊松曲面重建](http://blog.csdn.net/jennychenhit/article/details/52126156?locationNum=8).此方法的弊端是要形成封闭的曲面，这就不可避免地产生了一些奇怪的凸包，以及周围噪点带来的曲面的过度延伸，进一步增加了face的数目，从例程得到的点云包含241717个有向点，按默认depth=8重建得到的mesh含有123479个face，把mesh导入blender，密集恐惧症都快有了。如果用在大规模场景中，简直是灾难；而把depth降低到7则损失大量细节，完全是天壤之别！！


<img src="/img/mesh0 (1).png" width=500>
<img src="/img/mesh0 (2).png" width=500>

困扰我的问题是，以mesh描述物体的表面本不需要如此多的face，有些本该是棱角分明的地方，重建出来的反而是弧状的细细密密的face拼接而成的，浪费了很多计算时间，而且丧失了准确度。估计一下，如果手动建模的话例程的城堡正面连一万个face都用不上。

