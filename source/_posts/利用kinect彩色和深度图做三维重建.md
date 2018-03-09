---
title: 利用kinect的彩色图像和深度图做三维重建
date: 2018-03-07 19:21:52
tags: 三维重建
mathjax: true
---

*有时候，多咬牙坚持一会，就可能避免改弦易辙的大费周章...*

<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=298 height=52 src="//music.163.com/outchain/player?type=2&id=541511280&auto=0&height=32"></iframe>



目前看来，openMVG+pmvs2可以仅仅通过彩色图像完成三维点云的建模，而且不存在回环漂移，可见global sfm的全局优化效果很好，更可喜的是，sfm过程的用时较短，不过pmvs2的耗时很长。在宿舍环绕一圈拍摄，共157张图片，sfm在30s以内，而pmvs2约15分钟。实验过程中，我手持kinect缓慢移动和转动，但是获取到的彩色图像有很多都带有运动模糊，且幅度很大，因此要尽量保证kinect在拍照时的静止状态，第二次稍加改进了程序后，得到的图像清晰了许多,最后重建出的彩色点云如下图。

<img src="/img/room_demo.png">

虽然pmvs2生成的彩色点云质量还算及格，但是有如下缺点：
1.	耗时过长，图像数目继续增加将使其成为更大的短板
2.	自动剔除背景色，较深颜色的像素被舍弃，导致点云部分缺失
3.	噪点过多，由于光照等因素导致的不可避免的错误点云

既然如此，那么就利用sfm得到的位姿，将深度图中的深度像素映射到三维空间中重建点云。global sfm得到了相机的位姿，存储在sfm_data.bin(robust.bin)中，但是并不清楚openMVG的相机坐标系如何定义，而kinect相机坐标系也并不明确。想了很久也想不通，我的空间想象能力确实不够。

下面的代码是freenect2提供的深度图映射到三维坐标的部分，我只用这一步得出了一张图像的点云，在meshlab中显示得出了kinect的相机坐标系如下图

```C++
	float depth_val = img_float.at<float>(j,k)/1000.0f; //scaling factor, so that value of 1 is one meter.
	if (isnan(depth_val) || depth_val <= 0.001)
	{
		//depth value is not valid
		continue;
	}
	else
	{
		x = (j + 0.5 - cx) * fx * depth_val;
		y = (k + 0.5 - cy) * fy * depth_val;
		z = depth_val;
	}
```

<img src="/img/kinect_coordinate.png" width=300>

但是，把这些点云不做任何变换，直接用sfm得到的位姿进行变换，却不能无缝衔接。由于从彩色图像到点云完全利用的相机参数，得到的平移向量不一定是真实的长度，但是无论是深度图还是彩色图，同样两幅图像的旋转矩阵一定是相同的，通过不断的观察和尝试，我发现只需将利用freenect2生成的点云的(x,y,z)转换为(y,x,z)，再做旋转变换就能使点云之间只通过位移就可以衔接。下一步要做的，就是计算出两幅点云之间的平移向量，利用深度图建出点云，再找到深度图中invalid的数据，利用彩色图像的立体视觉补全该位置的点云。

未完待续...

