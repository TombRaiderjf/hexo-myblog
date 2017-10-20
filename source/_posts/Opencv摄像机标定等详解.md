---
title: Opencv摄像机标定等函数详解
date: 2016-7-28 16:04:40
categories: 机器视觉
tags: 
- Opencv
- 摄像机标定
---

*原创文章，转载请留言*

机器视觉留的大作业之一用到了摄像机标定以及双目视觉三维位置重建的内容,正巧我将要被安排去做opencv相关的东西，只能硬着头皮去学了。

*基于 vs 2012-- opencv2.4.8 平台*

<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=260 height=52 src="http://music.163.com/outchain/player?
type=2&id=3163120&auto=0&height=32"></iframe> 

safe and sound 好听到爆（Enjoy）

---

**下面结合opencv 官方文档（英文硬伤）来总结一些函数的用法**

## 匹配点检测

```C++

	bool findChessboardCorners( InputArray image, Size patternSize,
                                OutputArray corners,
                                int flags=CALIB_CB_ADAPTIVE_THRESH+CALIB_CB_NORMALIZE_IMAGE );
```

功能：找到棋盘格图像中的角点，返回值为1则成功，0则失败

参数详解：

- image--easy，输入图像Mat
- patternSize--是角点的“尺寸”，按照你规定的坐标系，Size(x方向角点数，y方向角点数),若x=4,y=5,那么共检测20个角点
- corners--（输出）角点向量，类型是vector<\Point2f\>(没有反斜杠，全文都是这样...)
- flag--标志位，默认是处理图像时利用自适应阈值以及图像标准化，感觉CALIB_CB_FAST_CHECK还算有用，快速检测是否有角点，应该用于很可能没有的情况下

```C++
		void cornerSubPix( InputArray image, InputOutputArray corners,
    						Size winSize, Size zeroZone, TermCriteria criteria );
```

功能：亚像素角点定位，比较推荐先用findChessboardCorners()其中flag=CALIB_CB_FAST_CHECK，返回值为1后再用cornerSubPix()

参数详解：

- image--同上
- corners--同上
- winSize--Half of the side length of the search window 不能理解
- zeroZone--Half of the size of the dead region in the middle of the search zone over which the summation in the formula below is not done. 不理解，反正我取Size(-1,-1)
- criteria--终止条件

```C++
		void drawChessboardCorners( InputOutputArray image, Size patternSize, 
									InputArray corners, bool patternWasFound );
```

功能：在图像中画出角点（还是五颜六色的，注意点是有先后顺序的，按彩虹颜色排列）

参数不再详述，bool参数取1就好（如果找到了角点）

## 单摄像机标定

```C++
	double calibrateCamera( InputArrayOfArrays objectPoints, InputArrayOfArrays imagePoints,
							Size imageSize, InputOutputArray cameraMatrix, InputOutputArray distCoeffs, 
							OutputArrayOfArrays rvecs, OutputArrayOfArrays tvecs, 
							int flags=0, TermCriteria criteria=TermCriteria( TermCriteria::
							COUNT+TermCriteria::EPS, 30, DBL_EPSILON) )
```

Tips: opencv里面弄清楚函数的参数类型是最关键的地方，因为每个库函数入口处都要执行一系列的很严格的assert()


功能：标定摄像机参数，包括内参数、畸变系数，外参数旋转矩阵和平移向量

摄像机标定需要多张图像中的多个对应点与世界坐标系中的相应点坐标

参数详解：

- objectPoints—所有图像中的点在世界坐标系中的坐标，这一参数的维度是3，我在遇到assert麻烦的时候曾经杀入assert源代码里面发现函数入口处检验objectPoints.CheckVector(…,…)第一个参数是3。根据官方文档上的例程，这一参数保准的类型是vector\<\vector\<\Point3f\>\>
- imagePoints—所有图像中的点的位置，维度是3，保准类型vector\<\vector\<\Point2f\>\>
- imageSize—图像尺寸，类型Size
- cameraMatrix—（输出）摄像机内参数矩阵3*3，函数用的是引用传参，因此要先声明该矩阵，最好是Mat cameraMatrix(3, 3, CV_64FC1);
- distCoeffs--（输出）畸变系数向量，长度可能是4，5，8，取决于flag参数
- tvecs--所有图像中的点从图像坐标系变换到世界坐标系的旋转矩阵的向量，就是一个与图像数目等大的向量，每个元素是一个旋转矩阵（每张图像拍摄角度不同，世界坐标系和摄像机坐标系的相对旋转也不同）类型vector\<\Mat\>
- rvecs--与tvecs类似，只不过是平移向量的向量，类型vector\<\Mat\>
- flag--默认值是0，下面的我只能理解K1,K2那几个意思是优化参数的时候某个K固定不变
```C++
	#define CV_CALIB_USE_INTRINSIC_GUESS  1
    	#define CV_CALIB_FIX_ASPECT_RATIO 2
    	#define CV_CALIB_FIX_PRINCIPAL_POINT  4
    	#define CV_CALIB_ZERO_TANGENT_DIST8
    	#define CV_CALIB_FIX_FOCAL_LENGTH 16
    	#define CV_CALIB_FIX_K1  32
    	#define CV_CALIB_FIX_K2  64
    	#define CV_CALIB_FIX_K3  128
    	#define CV_CALIB_FIX_K4  2048
    	#define CV_CALIB_FIX_K5  4096
    	#define CV_CALIB_FIX_K6  8192
    	#define CV_CALIB_RATIONAL_MODEL 16384
```
- criteria--迭代算法终止实例 默认为达到迭代次数或迭代到终止阈值，迭代最大次数为30，终止阈值是一个宏定义（反正特别小）

## 立体摄像机标定
```C++
	double stereoCalibrate( InputArrayOfArrays objectPoints,
                            InputArrayOfArrays imagePoints1,
                            InputArrayOfArrays imagePoints2,
                            CV_OUT InputOutputArray cameraMatrix1,
                            CV_OUT InputOutputArray distCoeffs1,
                            CV_OUT InputOutputArray cameraMatrix2,
                            CV_OUT InputOutputArray distCoeffs2,
                            Size imageSize, OutputArray R,
                            OutputArray T, OutputArray E, OutputArray F,
                            TermCriteria criteria = TermCriteria(TermCriteria::COUNT+TermCriteria::EPS, 30, 1e-6),
                            int flags=CALIB_FIX_INTRINSIC );
```
功能：同时标定两个摄像机，获取她们的内参数矩阵和相对旋转平移矩阵，基础矩阵...

参数详解：

- objectPoints--同上
- imagePoints1--所有图像中的标定点序列在第一个摄像机下的图像坐标，类型vector\<\vector\<\Point2f\>\>
- imagePoints2--所有图像中的标定点序列在第二个摄像机下的图像坐标，类型vector\<\vector\<\Point2f\>\>
- cameraMatrix1--第一个摄像机的内参数矩阵3*3（cameraMatrix2同理)
- distCoeffs1--第一个摄像机的畸变系数矩阵(distCoeffs2同理)
- imageSize--图像尺寸
- R--第一个摄像机坐标系到第二个摄像机坐标系的旋转矩阵
- T--第一个摄像机坐标系到第二个摄像机坐标系的平移向量
- E--本质矩阵
- F--基础矩阵
- 最后两个有默认参数，前面已经说过了

**Attention**：cameraMatrix和distCoeffs参数前的宏是InputOutputArray，为什么后面四个RTEF不是呢？因为cameraMatrix和distCoeffs既可以是输出也可以是输入，函数会检测这四个参数是否已经被赋了合法的值，从而采取不同的方法处理。


我有一处不明确，就是旋转矩阵和平移向量是基于哪一个坐标系的，坐标系三个轴的方向是如何规定的，感觉好像和ppt里讲的不太一致

## 校正

既然有了畸变系数，那一定可以利用这些系数来校正，然而这个函数效果真的是不敢恭维（还不如不校正）
```C++
	void stereoRectify( InputArray cameraMatrix1, InputArray distCoeffs1,
                        InputArray cameraMatrix2, InputArray distCoeffs2,
                        Size imageSize, InputArray R, InputArray T,
                        OutputArray R1, OutputArray R2,
                        OutputArray P1, OutputArray P2,
                        OutputArray Q, int flags=CALIB_ZERO_DISPARITY,
                        double alpha=-1, Size newImageSize=Size(),
                        CV_OUT Rect* validPixROI1=0, CV_OUT Rect* validPixROI2=0 );
```
前七个参数都在stereoCalibrate中求过了，这个函数输出了五个矩阵，我懒得管他们是什么了
```C++
	void initUndistortRectifyMap(InputArray cameraMatrix, InputArray distCoeffs, InputArray R,
								InputArray newCameraMatrix, Size size, int m1type, OutputArray map1, OutputArray map2);
```
上面的函数看名称就知道了，功能是初始化去畸变的校正映射（对单摄像机）

参数：

- R--stereoRecify求出的R1或R2
- newCameraMatrix--（输出）去畸变后的新摄像机内参数矩阵
- m1type--可取CV_32FC1 或 CV_16SC2
- map1, map2 不知道是几行几列的矩阵，直接在调用函数前声明两个Mat就好

```C++
		void remap( InputArray src, OutputArray dst, InputArray map1, 
			   		InputArray map2, int interpolation, int borderMode=BORDER_CONSTANT, 
			   		const Scalar& borderValue=Scalar())
```

一切就绪后，才是真正的对图像进行校正（单摄像机）

interpolation是选择插值方法，毕竟几何变化会需要非整数像素位置的值嘛，INTER_LINEAR（线性插值），INTER_NEAREST（最近邻插值），还有三个看起来就很复杂还是省省计算量吧

# 如果觉得有用就点个赞或者转发下吧 #

