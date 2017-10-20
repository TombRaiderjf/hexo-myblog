---
title: blender源码学习一
date: 2016-08-09 14:53:11
categories: 计算机图形学
tags:
- blender
---

*最近一直在啃的CG书，里面的示例代码太简略，需要自己写很多函数，我懒得搞，主要是C++忘差不多了，找到blender 2.77a的源码来分析分析，可能大部分只是翻译，练练英语。*

下载地址：http://download.blender.org/source/blender-2.77a.tar.gz

不管是什么平台下的CG，基本的结构是不会有很大差别的，今天只研究下Mesh数据的结构，希望有所收获。

# bmesh_class.h

bmesh模块中的所有类声明。包括了构建一个mesh的所有要素，把数据组织起来。

## BMHeader

所有的网格元素都以BMHeader结构开始

```C++
	typedef struct BMHeader {
		void *data; /* customdata layers */
		int index; 
		char htype;    /* 几何元素类型 （顶点/边/环切/面）element geometric type (verts/edges/loops/faces) */
		char hflag;    /* this would be a CD layer, see below */
		char api_flag;
	} BMHeader;
```
其中char htype为枚举类型，包含如下类别
```C++
	enum {
		BM_VERT = 1,
		BM_EDGE = 2,
		BM_LOOP = 4,
		BM_FACE = 8
	};
```

## 顶点-边-环-面

顶点结构：Vertices store a coordinate and link to an edge in the disk cycle of the vertex 顶点结构存储了点的坐标值以及已该点为顶点之一的边的链接，以此可以找到所有包含该点的边

**Disk Cycle: A circle of edges around a vertex**

<img src="https://wiki.blender.org/uploads/0/0f/Bmesh-diskcycle.png" width=50%; height=50%>

```C++
	typedef struct BMVert {
		BMHeader head;
		struct BMFlagLayer *oflags; /* keep after header, an array of flags, mostly used by the operator stack */
		float co[3];  /*顶点坐标 vertex coordinates */
		float no[3];  /*顶点法向量 vertex normal */
		struct BMEdge *e; /*包含该顶点的边的指针，disk cicle*/
	} BMVert;
```

**The Radial Cycle: A circle of faces around an edge**

<img src="https://wiki.blender.org/uploads/6/6d/Bmesh-radialcycle.png" width=50%; height=50%>

绕同一个顶点的边组成了链表，对一条边而言

	typedef struct BMDiskLink {
		struct BMEdge *next, *prev;  //指向前一个和后一个环切的边的指针
	} BMDiskLink;

边结构：Edges represent a connection between two vertices, but also store a link to a loop in the radial cycle of the edge 	

```C++
	typedef struct BMEdge {
		BMHeader head;
		struct BMFlagLayer *oflags; 
		struct BMVert *v1, *v2;  /* 边的两个顶点（无序）vertices (unordered) */
		struct BMLoop *l;	//包含该边的面的环的头指针
		BMDiskLink v1_disk_link, v2_disk_link;  //边的两个顶点的disk circle
	} BMEdge;
```

**Loop&Face 共同描述面**

The Loop Cycle: A circle of face edges around a polygon.

<img src="https://wiki.blender.org/uploads/9/99/Bmesh-facestructure.png" width=50%; height=50%>

环结构：Loops define the boundary loop of a face. Each loop logically corresponds to an edge, though the loop is local to a single face so there will usually be more than one loop per edge (except at boundary edges of the surface). 定义了每一个面的边界环，每条边（除了...）会被包括在一个以上的环中。

```C++
	typedef struct BMLoop {
		BMHeader head;
		struct BMVert *v;
		struct BMEdge *e; /* edge, using verts (v, next->v) */
		struct BMFace *f;
		struct BMLoop *radial_next, *radial_prev;
		struct BMLoop *next, *prev; /* next/prev verts around the face */
	} BMLoop;
```

面结构：Faces link to a loop in the loop cycle, the circular linked list of loops defining the boundary of the face.

```C++
	typedef struct BMFace {
		BMHeader head;
		struct BMFlagLayer *oflags; 
	#ifdef USE_BMESH_HOLES  //如果mesh中有孔洞
		int totbounds; /*1+“面中的孔洞数量”*/
		ListBase loops;
	#else
		BMLoop *l_first;   //没有孔洞，环数量才为1
	#endif
		int   len;   /* 面中的顶点数 number of vertices in the face */
		float no[3];  /* 平面法向量 face normal */
		short mat_nr;  /* 材质索引 material index */	
	} BMFace;
```

完整的 Mesh 结构

```C++
	typedef struct BMesh {
		int totvert, totedge, totloop, totface; //顶点-边-环-面数量
		int totvertsel, totedgesel, totfacesel;	 
		char elem_index_dirty;/* valid flags are - BM_VERT | BM_EDGE | BM_FACE | BM_LOOP. */
	/* flag array table as being dirty so we know when its safe to use it,
	 * or when it needs to be re-created */
		char elem_table_dirty;
	/* element pools */
		struct BLI_mempool *vpool, *epool, *lpool, *fpool;
		BMVert **vtable;  //该mesh的顶点的二重指针，顶点索引表
		BMEdge **etable;
		BMFace **ftable;
	/* size of allocated tables */
		int vtable_tot;   //顶点表的长度
		int etable_tot;
		int ftable_tot;
		struct BLI_mempool *vtoolflagpool, *etoolflagpool, *ftoolflagpool;
		int toolflag_index;
		struct BMOperator *currentop;
		CustomData vdata, edata, ldata, pdata;
	#ifdef USE_BMESH_HOLES
		struct BLI_mempool *looplistpool;
	#endif
		short selectmode;
		int shapenr;/* 该mesh形状的类型ID。 ID of the shape key this bmesh came from */
		int walkers, totflags;
		ListBase selected;
		BMFace *act_face; //当前被选中的面
		ListBase errorstack;
		void *py_handle;
	} BMesh; 
```