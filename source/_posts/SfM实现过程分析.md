---
title: SfM实现过程分析
date: 2018-01-03 17:46:44
tags: SfM
categories: 机器视觉
---

昨天立了flag，今天要学SfM过程，大概看了看SfM的各个文件目录，build&make出来的linux-release-x86大概叫这个名字的文件夹里面有很多可执行文件，直接根据文档里给的参数跑就可以，要搞源码的话实在是搞不起，太复杂，太庞大了。下面的代码是从他给出的easy to use的python脚本中截取的核心代码，注释的也很赞，清晰明确。

# SfM global pipeline代码

```python
	print ("1. Intrinsics analysis")
	pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params] )
	pIntrisics.wait()

	print ("2. Compute features")
	pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
	pFeatures.wait()

	print ("3. Compute matches")
	pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-g", "e"] )
	pMatches.wait()

	# Create the reconstruction if not present
	if not os.path.exists(reconstruction_dir):
    	os.mkdir(reconstruction_dir)

	print ("4. Do Global reconstruction")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_GlobalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
	pRecons.wait()

	print ("5. Colorize Structure")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
	pRecons.wait()

	# optional, compute final valid structure from the known camera poses
	print ("6. Structure from Known Poses (robust triangulation)")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-f", os.path.join(matches_dir, "matches.e.bin"), "-o", os.path.join(reconstruction_dir,"robust.bin")] )
	pRecons.wait()

	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/robust.bin", "-o", os.path.join(reconstruction_dir,"robust_colorized.ply")] )
	pRecons.wait()
```

# 过程分析

SfM_GlobalPipeline.py的核心代码清楚地展示了Multi-view structure from motion(SfM)的实现步骤：


## 读取并存储输入图像的信息于sfm_data.json中

views中的每个子集都代表存储图像信息，包括文件名，图像尺寸，相机内参数（optional），如果已知相机内参数，可以在图像文件夹中增加txt写出内参数矩阵

sfm_data.json文件格式
	
```javascript
{
    "sfm_data_version": "0.3",
    "root_path": "/home/jf/openMVG_Build/software/SfM/ImageDataset_SceauxCastle/images",
    "views": [
        {
            "key": 0,
            "value": {
                "polymorphic_id": 1073741824,
                "ptr_wrapper": {
                    "id": 2147483649,
                    "data": {
                        "local_path": "",
                        "filename": "100_7100.JPG",
                        "width": 2832,
                        "height": 2128,
                        "id_view": 0,
                        "id_intrinsic": 0,
                        "id_pose": 0
                    }
                }
            }
        },
	...
	],
	"intrinsics": [
        {
            "key": 0,
            "value": {
                "polymorphic_id": 2147483649,
                "polymorphic_name": "pinhole_radial_k3",
                "ptr_wrapper": {
                    "id": 2147483660,
                    "data": {
                        "width": 2832,
                        "height": 2128,
                        "focal_length": 2881.25212694251,
                        "principal_point": [
                            1416.0,
                            1064.0
                        ],
                        "disto_k3": [
                            0.0,
                            0.0,
                            0.0
                        ]
                    }
                }
            }
        }
    ],
    "extrinsics": [],
    "structure": [],
    "control_points": []
}
```

*这个代码高亮丑丑的，差评*

## 根据输入的sfm_data.json文件计算并储存每个图像的描述子

这里默认的是SIFT特征描述子，还有其他可选方法，但是我不认识，就不管了。[http://tombraiderjf.com/2017/10/22/SIFT%E7%89%B9%E5%BE%81%E6%A3%80%E6%B5%8B/](http://tombraiderjf.com/2017/10/22/SIFT%E7%89%B9%E5%BE%81%E6%A3%80%E6%B5%8B/ "SIFT特征提取")

## 利用上一步的描述子进行特征点匹配

前提是图像之间存在overlap.建立相应的推测光度匹配，并使用一些鲁棒的几何滤波器来过滤所得的对应关系，还给出svg图像来描述这个关系，在程序中得到matches文件夹

<img src="/img/Free-Converter.com-geometric_matches-22732642.png" width=300>

## GlobalSfM

这个方法是基于在2013年发表于ICCV的论文 “Global Fusion of Relative Motions for Robust, Accurate and Scalable Structure from Motion.”来自运动的多视图结构（SfM）估计图像在公共3D坐标系中的位置和方向。 当逐步（Incrementally）处理视图时，与外部均匀分布残差的全局方法相反，此外部校准可能会发生漂移。 这里该方法提出了一种基于图像对之间的相对运动的融合的新的全局校准方法。（以上谷歌翻译...）所以这种方法听上去比IncrementalSfM更好些，就用它了。

该算法：
-	输入：相机内参数；具有几何一致性的匹配点
-	输出：三维点云；相机位姿
	
##	计算sfm_data场景的颜色

##（optional）构建已知位姿（鲁棒的三角测量），再构建颜色


# GlobalSfMpipeline测试

11张图像（valid），尺寸2128x2832，耗时18 seconds

最后，利用PMVS工具得到稠密点云，这个最耗时...保守估计1分钟吧，毕竟我只会在脚本里加时间函数。

点云是不够的，噪点不少，而且疏密不定，Quan Long 的ppt里对比了Mesh和Volumetric的优劣，表示三角面片形式的mesh更适合作为点云重建的输出，不过转换的方法不好选择，meshlab自带了几种，都不太好用，有闪退的，还有没变化的，还有细节缺失较多的...或许是参数调的不好，只能再搜罗搜罗现成的方法。

（题外话）*前天在github上comment openMVG文档的小错误，今天早上居然收到了邮件回复（一位叫Pierre Moulon的开发人员），我也明白了他的原意，不过在指出了ambiguous之处后，他把相关的几处都改了*

---

**1月4日更新：**

图像集仍是例程克隆下来的Castle的11张照片
耗时：
-	特征提取 14seconds
-	特征匹配 4seconds
-	点云重建 86seconds，共240,000左右个点

为了检测普适性，我用手机（iPhone SE）拍了五张宿舍一角的照片，分辨率为4K，结果尝试多次都出Invalid data的错误，后来查看文档发现*The chain will only consider images with known approximate focal length. Image with invalid intrinsic id will be ignored.* 又去找sensor_width_camera_database.txt，结果里面根本木有SE的参数（mmp）。

其实最主要的参数是focal length in pixel，畸变系数之类的直接可以忽略掉，然而就这一个参数EXIF里都没有，如果手动算的话还要已知CCD width，公式：focal length in pixels = (image width in pixels) x (focal length in mm) / (CCD width in mm)。最后无奈只得切回windows下了个修改EXIF 的软件，把型号改成iPhone 6s Plus，美滋滋。



参考:
[1] openMVG-SfM文档 [http://openmvg.readthedocs.io/en/latest/software/SfM/SfM/](http://openmvg.readthedocs.io/en/latest/software/SfM/SfM/ "openMVG-SfM文档")
[2] EXIF在线解析地址 [https://exif.tuchong.com/](https://exif.tuchong.com/)


