---
title: Cuda编程学习一
date: 2016-09-06 14:50:45
categories: 计算机图形学
tags:
- 显卡编程
---

<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=298 height=52 src="http://music.163.com/outchain/player?type=2&id=2918954&auto=0&height=32"></iframe>

*大部分内容翻译自CUDA C Programming Guide*

# 介绍

## 从图形处理到通用并行计算

受市场对实时高清3D图像的高要求，可编程图形处理单元GPU进化为了高度并行，多线程，多核心，有着强大的计算能力和极高的显存带宽。与CPU相比，GPU更适合处理数据并行的计算问题，即同时对大量数据做相同的处理。

在3D渲染中，大规模的像素和顶点被映射到并行的线程，同样地，图像和视频处理的各个应用如渲染图像，视频编码解码，图像放缩，立体视觉等都可以把图像块映射到并行处理的线程中。实际上，许多非图像处理的算法也在利用并行处理数据的方法，从信号处理，物体仿真到金融计算和生物计算。

## CUDA

CUDA的软件环境允许开发者使用C作为高级程序语言，它也支持FORTRAN，DirectCompute，OpenACC等语言。

# 编程规范

## 核函数（kernels）

CUDA允许自定义C函数，称为核函数，于普通的C函数不同的是，它一旦被调用就会在N个不同的CUDA线程执行N次。

核函数的定义以__global__为前缀，线程数由<<<...>>>来表示，每一个执行该核函数的线程有一个唯一的ID，它可以在核函数内通过内置变量threadIdx来获取。下面的例子把两个数组A，B相加的结果存于C中：

```C++
	// 核函数定义
	__global__ void VecAdd(float* A, float* B, float* C) {
		int i = threadIdx.x; 
		C[i] = A[i] + B[i];
	}
	int main() {
		...
		// 核函数调用N个线程
		VecAdd<<<1, N>>>(A, B, C); ...
	}
```

## 线程分级

方便起见，threadIdx是一个三变量vector，因此线程可以被分为为一维，二维或三维的线程块，分别使用一维，二维和三维索引。这方便了为vector，matrix，volume里的元素进行计算。

线程的索引和它的线程ID很直观地联系在一起：对于一维的线程块，线程索引=线程ID；对于二维的大小为(Dx,Dy)的线程块，线程索引（x,y）对应的ID是(x+y*Dx)；对三维的大小为(Dx,Dy,Dz)的线程块，线程所有(x,y,z)对应的ID是(x+y*Dx+z*Dx*Dy).

下面的例子把矩阵A和B相加并存储与C

```C++
	// 核函数定义
	__global__ void MatAdd(float A[N][N], float B[N][N], float C[N][N])
	{
		int i = threadIdx.x; 
		int j = threadIdx.y; 
		C[i][j] = A[i][j] + B[i][j];
	}
	int main() {
	...
		// 核函数以  N * N * 1 的线程块被调用
		int numBlocks = 1; 
		dim3 threadsPerBlock(N, N); 
		MatAdd<<<numBlocks, threadsPerBlock>>>(A, B, C); ...
	}
```

每个线程块是有一定限制的，因为一个块的所有线程都要在同一个处理核心上且必须共享有限的内存资源，目前的GPU上一个线程块最多包含1024个线程。但是，核函数可以在多个相同大小的线程块中运行，因此总线程数=线程块数*每块的线程数

与线程类似，线程块被组织为一维，二维和三维的grid（网格）。一个网格中线程块的数目通常由被处理数据的大小或处理单元的数目决定。

线程块的线程数和网格的线程块数载<<<...>>>语法中可以是int或dim3类型，网格内的每个线程块由一维，二维或三维的索引在核函数内置变量blockIdx表征。线程块的维度在核函数内的blockDim变量获取。下面的例子将上一个例子变成处理多个线程块：

```C++
	// 核函数定义
	__global__ void MatAdd(float A[N][N], float B[N][N], float C[N][N]) {
		int i = blockIdx.x * blockDim.x + threadIdx.x; 
		int j = blockIdx.y * blockDim.y + threadIdx.y; 
		if (i < N && j < N)
			C[i][j] = A[i][j] + B[i][j]; 
	}
	int main() {
	...
		// Kernel invocation 
		dim3 threadsPerBlock(16, 16); 
		dim3 numBlocks(N / threadsPerBlock.x, N / threadsPerBlock.y); MatAdd<<<numBlocks, threadsPerBlock>>>(A, B, C); ...
	}
```

线程块的尺寸是16*16，共256个线程，网格由足够的线程块构成使得对每个矩阵元素都有一个线程，简便起见，把网格的每一维度的线程数设为相等。

一个线程块里有共享内存，块内线程可以从共享内存中获取数据，也可以把计算结果同步到共享内存中去。线程可以在核函数中通过调用__syncthreads()确定同步点，这个内置函数作为一个屏障，一旦被调用则该线程块内的所有线程必须等待同步完毕。共享内存是一个低延迟的内存，它在每个处理核的附近（很像一级缓存），但是空间有限。

## 内存分级

CUDA线程可以在运行时获取多个内存空间的数据。每个线程有私有的本地内存，每个线程块有共享内存，每个线程都可以获取相同的全局内存。还有两个对所有线程可用的只读内存空间：常量内存和纹理内存。全局，常量和纹理内存是对不同内存应用的优化。

## 异步编程

CUDA程序的C程序部分在host上运行，CUDA线程在device下运行，在CUDA程序中，内存和显存保持它们各自的存储空间，分别称为host memory & device memory.两者之间会有数据交换。

# 编程接口

## CUDA C Runtime


<li>初始化：<br/>没有显示的初始化函数，它在第一次被调用时初始化。在初始化的过程中，运行时为每个device创建了一个CUDA上下文，这个上下文是原始的并且由应用程序在host上的所有线程共享。</li>
<li>设备内存：<br/>核函数在设备内存上运行，因此运行时提供了分配，销毁和拷贝设备内存以及在主机和设备内粗之间传送数据的函数。设备内存可以被分配为线性内存或CUDA数组。
<br/>线性内存存储与设备上的40位地址空间，因此独立分配的数据可以通过指针来获取比如二叉树。分配函数是cudaMalloc()，销毁函数是cudaFree()，数据在host和device之间交换的函数是cudaMemcpy()下面的例子中，vector需要从host拷贝到device中</li>
	
```C++
	// Device code
	__global__ void VecAdd(float* A, float* B, float* C, int N) {
		int i = blockDim.x * blockIdx.x + threadIdx.x; 
		if (i < N)
			C[i] = A[i] + B[i]; 
	}
	// Host code 
	int main() {
		int N = ...; 
		size_t size = N * sizeof(float);
	// Allocate input vectors h_A and h_B in host memory 
		float* h_A = (float*)malloc(size);
		float* h_B = (float*)malloc(size);
	// Initialize input vectors ...
	// Allocate vectors in device memory 
		float* d_A;
		cudaMalloc(&d_A, size); 
		float* d_B;
		cudaMalloc(&d_B, size); 
		float* d_C;
		cudaMalloc(&d_C, size);
		// Copy vectors from host memory to device memory 
		cudaMemcpy(d_A, h_A, size, cudaMemcpyHostToDevice); cudaMemcpy(d_B, h_B, size, cudaMemcpyHostToDevice);
		// Invoke kernel int threadsPerBlock = 256; 
		int blocksPerGrid =(N + threadsPerBlock - 1) / threadsPerBlock;
		 VecAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);
		// Copy result from device memory to host memory 
		// h_C contains the result in host memory 
		cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);
		// Free device memory cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
		// Free host memory ...
	}
```

线性内存也可以用cudaMallocPitch()&cudaMalloc3D()来分配，他们更适合于分配2D或3D的数组

下面的代码展示了获取全局变量的不同方法：

```C++
	__constant__ float constData[256]; float data[256];
	cudaMemcpyToSymbol(constData, data, sizeof(data)); 
	cudaMemcpyFromSymbol(data, constData, sizeof(data));

	__device__ float devData; 
	float value = 3.14f;
	cudaMemcpyToSymbol(devData, &value, sizeof(float));
	
	__device__ float* devPointer; 
	float* ptr;
	cudaMalloc(&ptr, 256 * sizeof(float)); 
	cudaMemcpyToSymbol(devPointer, &ptr, sizeof(ptr));
```

<li>共享内存：<br/>共享内存由前缀shared（双下划线前后）声明，共享内存速度比全局内存快很多，因此要尽可能地以共享内存代替全局内存</li>

<li>锁页内存：<br/>使用锁页内存的好处：1.锁页内存与显存的拷贝可以在执行核函数的时候并发进行。2.锁页内存可以被映射到显存地址空间，避免了从显存拷贝到内存的时间消耗。3.On systems with a front-side bus，内存和显存之间的带宽更高
</li>

<li>同步并发执行：<br/>1.流：按顺序执行的指令序列<br/>2.事件：Runtime提供了一种密切管理设备进度，也可以精确计算运行时间的方式，通过在程序中某一点同步地设置一个event和得到这个event何时完成</li>

<li>多设备系统：下面的代码展示了如何在不同的设备上分配变量和运行核函数<br/>

</li>

```C++
	size_t size = 1024 * sizeof(float); 
	cudaSetDevice(0);
	float* p0; 
	cudaMalloc(&p0, size); 
	float* p1; 
	cudaMalloc(&p1, size);
	MyKernel<<<1000, 128>>>(p0); // Launch kernel on device 0 cudaSetDevice(1);
	MyKernel<<<1000, 128>>>(p1); // Launch kernel on device 1
```

<li>纹理内存:<br/>读取纹理内存的过程被称为texture fetch，每一个texture fetch有一个参量叫做texture object或者texture reference，纹理对象的结构如下。通过纹理引用在核函数中访问纹理内存，需先将该纹理引用绑定到一个纹理，使用cudaBindTexture()或者 cudaBindTexture2D()绑定到线性数据，使用cudaBindTextureToArray()绑定到CUDA数组。可以使用cudaUnbindTexture()来解除绑定，一旦解除，纹理引用就可以绑定到其他纹理，即使使用原来绑定的纹理的核函数没有执行结束</li>

```C++
	struct cudaTextureDesc {
		enum cudaTextureAddressMode addressMode[3]; 
		enum cudaTextureFilterMode filterMode; 
		enum cudaTextureReadMode readMode;
		int intnormalizedCoords; ;
		enum cudaTextureFilterMode mipmapFilterMode; 
		float mipmapLevelBias;
		float minMipmapLevelClamp; 
		float maxMipmapLevelClamp;
		int sRGB;
		unsigned intmaxAnisotropy
	};
```