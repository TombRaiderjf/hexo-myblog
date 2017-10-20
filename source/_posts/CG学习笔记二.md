---
title: CG学习笔记二
date: 2016-08-11 12:16:14
categories: 计算机图形学
---

<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=298 height=52 src="http://music.163.com/outchain/player?type=2&id=27804336&auto=0&height=32"></iframe>

第15章是老师要求重点学习的，写篇总结

既然已经有了各种结构和类来表示一个场景，那么如何将这个三维的场景画面转换到特定视角下的二维图像显示出来呢？有两种方法可以实现，一是光线追踪，二是光栅化，下面分别介绍这两种方法。

首先，白手起家，定义一些简单的类和结构来表示三维场景中的东西，部分来自书，部分函数是我自己添加的。

# 一些基础类代码

Vector3：三维向量，重载了各个运算符

```C++
	class Vector3 
	{ 
	public: 
		float x, y, z;
		Vector3(){x = 0; y = 0; z = 0;}
		Vector3(float x1, float y1, float z1):x(x1),y(y1),z(z1){};
		Vector3(Vector3& v){
			x = v.x; y = v.y; z = v.z;
		}
		Vector3(const Vector3& v){
			x = v.x; y = v.y; z = v.z;
		}
		float dot(Vector3 v)const{
			return ( x * v.x + y * v.y + z* v.z);
		}
		Vector3 cross(Vector3 v)const{
			return Vector3( y * v.z - v.y * z, z * v.x-v.z * x, x * v.y -v.x * y );
		}
		Vector3 direction()const{
			float tmp = length();
			return Vector3( x/tmp, y/tmp, z/tmp );
		}	
		float length()const{
			return sqrt(x*x+y*y+z*z);
		}
		Vector3 operator*(float s) const { 
			return Vector3(s * x, s * y, s * z);
		}
		Vector3 operator/(float s) const { 
			return Vector3(x/s, y/s, z/s);
		}
		Vector3 operator+(Vector3 s) const { 
			return Vector3(x+s.x, y+s.y, z+s.z);
		}
		Vector3 operator-(Vector3 s) const { 
			return Vector3(x-s.x, y-s.y, z-s.z);
		}
		Vector3 operator-() const { 
			return Vector3(-x, -y, -z);
		}
		Vector3 operator=(Vector3 v){
			x = v.x; y = v.y; z = v.z;
			return *this;
		}
	}; 
```

Point3：三维点坐标

	typedef Vector3 Point3; 

Color3：表示颜色的类

```C++
	class Color3 
	{ 
	public: 
		float r, g, b;
		Color3() : r(0), g(0), b(0) {} 
		Color3(float r, float g, float b) : r(r), g(g), b(b){}
		Color3(Vector3& v){
			r = v.x; g = v.y; b = v.z;
		}
		Color3 operator*(Color3 c)const{
			return Color3(r * c.r, g * c.g, b * c.b);
		}
		Color3 operator*(float s) const { 
			return Color3(s * r, s * g, s * b);
		}
		Color3 operator/(float s) const { 
			return Color3(r/s, g/s, b/s);
		}	
		Color3 operator+(Color3 c) const {
			return Color3( c.r + r, c.g + g, c.b + b );
		}
	}; 
```

Ray：表示一条光线，包括一个点和向量

```C++
	class Ray 
	{ 
	private:
		Point3		m_origin; 
		Vector3		m_direction;
	public: 
		Ray(const Point3& org, const Vector3& dir) : m_origin(org), m_direction(dir) {}
		const Point3& origin() const { return m_origin; } 
		const Vector3& direction() const { return m_direction; }
	};
```

BSDF：描述一个面的散射

```C++
	class BSDF { 
	public:
		Color3 k_L;
		BSDF(){k_L = Color3(0.0,0.0,0.0);}
		BSDF(Color3& c):k_L(c){}
		Color3 evaluateFiniteScatteringDensity (const Vector3& w_i, const Vector3& w_o) const { 
		return k_L / PI;
		}
	};
```

Triangle：三角形

```C++
	class Triangle { 
	private:
		Point3		m_vertex[3];  
		Vector3		m_normal[3];
		BSDF		m_bsdf;
	public:
		Triangle( std::vector<Point3>& p, std::vector<Vector3>& n){
			for(int i = 0; i<3; i++){
				m_vertex[i] = p[i];
				m_normal[i] = n[i];
			}
		}
		const Point3& vertex(int i) const { return m_vertex[i]; } 
		const Vector3& normal(int i) const { return m_normal[i]; } 
		const BSDF& bsdf() const { return m_bsdf; } 
	};
```

Light：灯光

```C++
	class Light { 
	public:
		Point3 position; 
		Power3 power; 
		Light(Point3 p, Power3 pw):position(p),power(pw){}
	};
```

Camera：摄像机

```C++
	class Camera { 
	public:
		float zNear; 
		float zFar; 
		float fieldOfViewX;
		Camera() : zNear(-0.1f), zFar(-100.0f), fieldOfViewX(PI / 2.0f) {}
	};
```

Scene：三维场景

	class Scene { 
	public:
		std::vector<Triangle> triangleArray; 
		std::vector<Light> lightArray;
		Scene(std::vector<Triangle>& t, std::vector<Light>& l){
			triangleArray = t;
			lightArray = l;
		}
	};

Image：在某一摄像机位置和视角下显示的2D图像

	class Image 
	{ 
	private: 
		int m_width;
		int m_height;
		std::vector<Radiance3> m_data; 
		int PPMGammaEncode(float radiance, float displayConstant) const;
	public:
		Image(int width, int height) : m_width(width), m_height(height), m_data(width * height) {}
		int width() const { return m_width; } 
		int height() const { return m_height; }
		void set(int x, int y, const Radiance3& value) {
			m_data[x + y * m_width] = value;
		}
		const Radiance3& get(int x, int y) const { 
			return m_data[x + y * m_width];
		} 
		void save(const std::string& filename, float displayConstant=15.0f) const; 
	};

# Ray Casting--光线投射

翻译英文实在比较拗口，简单的来说，就是若目标图像为800*500，就分别对这40W个像素点的亮度值进行计算，方法就是对每一个点计算从摄像机原点到图像平面（其实是虚拟的，假设这个2D图像平面在z=-1）的射线（eye-ray），然后遍历所有的Triangle，通过Ray-Surface Intersection方法找到与这条射线相交的那些Triangle，并逐步确定最近的一个相交Triangle。

## A Test Scene

建立一个场景，包括一个三角形和一个灯光源

	vector<Point3> p(3);
	p[0] = Point3(0,1,-2);
	p[1] = Point3(-1.9,-1,-2);
	p[2] = Point3(1.6,-0.5,-2);
	vector<Vector3> v(3);
	v[0] = Vector3( 0.0f, 0.6f, 1.0f).direction();
	v[1] = Vector3(-0.4f,-0.4f, 1.0f).direction();
	v[2] = Vector3( 0.4f,-0.4f, 1.0f).direction();	
	Camera cam = Camera();
	Triangle triangle(p, v);	
	Image image(800, 500);
	Light light(Point3(1.0f,3.0f,1.0f), Power3(10, 10, 10));
	vector<Triangle> tg;
	tg.push_back(triangle);
	vector<Light> lt;
	lt.push_back(light);
	Scene scene(tg, lt);

## EyeRay 测试

下面是计算一条EyeRay射线的函数：

	Ray computeEyeRay(float x, float y, int width, int height, const Camera& camera) { 
		const float aspect = float(height) / width; //高宽比 
		//在z=-1平面上的
		const float s = -2.0f * tan(camera.fieldOfViewX * 0.5f);  
		Vector3& start = Vector3( (x / width - 0.5f) * s, -(y / height - 0.5f) * s * aspect, 1.0f) * camera.zNear;
		return Ray(start, start.direction()); 
	}

原理如图所示：

<img src="/img/16-1.png">

把得到的图像点对应的EyeRay射线的方向进行可视化

	for (int y = 0; y < image.height() ; ++y) { 
		for (int x = 0; x < image.width(); ++x) { 
			const Ray& R = computeEyeRay(x + 0.5f, y + 0.5f, image.width(), image.height(), cam);
			image.set(x, y, Color3(R.direction() + Vector3(1, 1, 1)) / 5);
		//可视化射线方向，先将方向向量变为非负，再除以5使得结果在可以以颜色表达的范围内调试
		}
	}

完善Image类的save函数保存图像为ppm格式：

	void Image::save(const std::string& filename, float d) const 
	{ 
		FILE* file = fopen(filename.c_str(), "wt"); 
		fprintf(file, "P3 %d %d 255\n", m_width, m_height); /ppm文件头
		for (int y = 0; y < m_height; ++y) { 
			fprintf(file, "\n# y = %d\n", y); 
			for (int x = 0; x < m_width; ++x) { 
				const Radiance3& c(get(x, y)); 
				fprintf(file, "%d %d %d\n", PPMGammaEncode(c.r, d), PPMGammaEncode(c.g, d), PPMGammaEncode(c.b, d));
			} 
		} 
		fclose(file); 
	}
	
	int Image::PPMGammaEncode(float radiance, float d) const { 
		//此函数用于伽马校正，因为显示设备通常是指数失真的模型
		return int(std::pow(std::min(1.0f, std::max(0.0f, radiance * d)), 1.0f / 2.2f) * 255.0f);
	}

得到ppm格式保存的图像如下，符合书中结果

<img src="/img/16.png">

## Intersection & Shade--相交与着色

**Intersection**

下面计算光线与三角形的交点在三角形重心坐标系下的坐标（权重），并计算摄像机原点与交点的距离,示意图如下：

<img src="/img/16-2.png">

代码如下，返回摄像机原点与交点的距离值：

	float intersect(const Ray&R, const Triangle&T, float weight[3]) { 
		const Vector3& e1 = T.vertex(1) - T.vertex(0); 
		const Vector3& e2 = T.vertex(2) - T.vertex(0); 
		const Vector3& q = R.direction().cross(e2);
		const float a = e1.dot(q);
		const Vector3& s = R.origin() - T.vertex(0); 
		const Vector3& r = s.cross(e1);
		// 顶点重心坐标系的权重 
		weight[1] = s.dot(q) / a; 
		weight[2] = R.direction().dot(r) / a; 
		weight[0] = 1.0f - (weight[1] + weight[2]);
		const float dist = e2.dot(r) / a;
		static const float epsilon = 1e-7f; 
		static const float epsilon2 = 1e-10;
		if ((a <= epsilon) || (weight[0] < -epsilon2) || (weight[1] < -epsilon2) || (weight[2] < -epsilon2) || (dist <= 0.0f)) { 
		//射线近乎平行于三角形, 或者交点在三角形外部或在射线反方向时，距离为无穷
			return INFINITY;
		} else { 
			return dist; 
		} 
	}

sampleRayTriangle函数用于判断当前交点是否是目前为止在这条EyeRay上距离原点最近的交点，是则返回true，否则false

	bool sampleRayTriangle(const Scene& scene, int x, int y, const Ray&R, const Triangle&T, Radiance3& radiance, float& distance) {
		float weight[3]; 
		const float d = intersect(R, T, weight);
		if (d >= distance) { 
			return false;
		}
		// 当前交点到摄像机原点的距离小于之前存储的最小距离
		distance = d;
		// Intersection point const 
		Point3& P = R.origin() + R.direction() * d;
		// Find the interpolated vertex normal at the intersection 
		const Vector3& n = (T.normal(0) * weight[0] + T.normal(1) * weight[1] + T.normal(2) * weight[2]).direction();
		const Vector3& w_o = -R.direction();
		shade(scene, T, P, n, w_o, radiance);
		// 调试是否相交，把下一个注释去掉，相交处为白色 //radiance = Radiance3(1, 1, 1);
		// 如果要调试交点的重心坐标系计算的值，去掉下一个注释 //radiance = Radiance3(weight[0], weight[1], weight[2]) / 15; 
		return true;
	}

调试是否相交（去掉shade函数）的结果如下：

<img src="/img/16-4.png">

调试重心坐标权值（去掉shade函数）的结果如下：

<img src="/img/16-3.png">

利用RayTrace函数（整合各项功能实现2D图像像素着色）处理：

	void rayTrace(Image& image, const Scene& scene, const Camera& camera, int x0, int x1, int y0, int y1) {
		// For each pixel 
		for (int y = y0; y < y1; ++y) { 
			for (int x = y0; x < x1; ++x) {
				const Ray& R = computeEyeRay(x + 0.5f, y + 0.5f, image.width(), image.height(), camera);			
				float distance = INFINITY;  // 初始化距离为无穷
				Radiance3 L_o;
				for (unsigned int t = 0; t < scene.triangleArray.size(); ++t){ 
				const Triangle& T = scene.triangleArray[t];
					if (sampleRayTriangle(scene, x, y, R, T, L_o, distance)) { 
						image.set(x, y, L_o);
					} 
				} 
			} 
		} 
	}

**Shade**

着色部分，首先要判断当前的射线-三角形交点是否是距离摄像机原点最近的，在尚未遍历三角形之前，这个距离值初始化为无穷，通过比较来选择最近的交点，也就是这个交点反射的光线投射到当前像素上，完成着色。

着色函数如下，其中visible函数用于判断三角形是否没有被离光源更近的平面遮挡住，要得到的结果在引用L_o中存储，只需将image的对应坐标像素进行set即可。

	void shade(const Scene& scene, const Triangle& T, const Point3& P, const Vector3& n, const Vector3& w_o, Radiance3& L_o) {
		L_o = Color3(0.0f, 0.0f, 0.0f);
		// 遍历所有的光源带来的光线
		for (unsigned int i = 0; i < scene.lightArray.size(); ++i) { 
			const Light& light = scene.lightArray[i];
			const Vector3& offset = light.position - P; 
			const float distanceToLight = offset.length(); 
			const Vector3& w_i = offset / distanceToLight;
			if (visible(P, w_i, distanceToLight, scene)) { 
				const Radiance3& L_i = light.power / (4 * PI * distanceToLight*distanceToLight);
				L_o = L_i * T.bsdf().evaluateFiniteScatteringDensity(w_i, w_o) * max(0.0, w_i.dot(n)) + L_o;
			} 
		} 
	}

测试shade函数，创建BSDF.k_L = Color3(0.0f, 0.8f, 0.0f) 绿色三角形面，跳过visible判断，得到如下结果：

<img src="/img/16-5.png">

**Shadow**

visible函数，用于生成阴影：

	bool visible(const Vector3& P, const Vector3& direction, float distance, const Scene& scene){ 
		static const float rayBumpEpsilon = 1e-4; 
		const Ray shadowRay(P + direction * rayBumpEpsilon, direction);
		distance -= rayBumpEpsilon;
	// Test each potential shadow caster to see if it lies between P and the light 
		float ignore[3]; 
		for (unsigned int s = 0; s < scene.triangleArray.size(); ++s) { 
			if (intersect(shadowRay, scene.triangleArray[s], ignore) < distance) { 
			//在交点指向光源的射线上，有一个三角形遮挡了光线，返回false
				return false;
			}
		} 
		return true; 
	}

在scene中加入一个平面来测试visible函数，注意平面可以用两个公用一条边的三角形表示，而原来的绿色三角形是一个单面，不能遮蔽从平面反射回来的光线，因此需要增加一个顶点完全重合的反面，反面的法向量与正面相反，可将光线一次反射，因此光线无法射入摄像机，产生阴影。结果如下：

<img src="/img/16-6.png">

# Rasterization--光栅化

Ray-Casting方法外层循环是遍历图像的像素点，内层循环是遍历三角形，rasterize是将循环顺序颠倒，外层遍历三角形，内层遍历像素点。但是这样导致不能连续对像素的最近交点进行比较和覆盖，因此需要一个新的结构来存储每一个像素点与最近交点的距离值，并在遍历过程中不断更新。

DepthBuffer类：

	class DepthBuffer
	{ 
	private: 
		int m_width;
		int m_height;
		std::vector<float> m_data; 
	public:
		DepthBuffer(int width, int height, float s) : m_width(width), m_height(height), m_data(width * height) {
			for(int i = 0; i < m_width; i++ )
				for(int j = 0; j< m_height; j++)
					set(i, j, s);
		}
		void set(int x, int y, const float& value) {
			m_data[x + y * m_width] = value;
		}
		const float& get(int x, int y) const { 
			return m_data[x + y * m_width];
		} 	
	};

rasterize函数：

	void rasterize(Image& image, const Scene& scene, const Camera& camera){
		const int w = image.width(), h = image.height(); 
		DepthBuffer depthBuffer(w, h, INFINITY);
		for (unsigned int t = 0; t < scene.triangleArray.size(); ++t) { //遍历三角形
			const Triangle& T = scene.triangleArray[t]; 
			const int x0=0; 
			const int x1=w;
			const int y0=0; 
			const int y1=h;
			for (int y = y0; y < y1; ++y) {  //遍历每个像素
				for (int x = x0; x < x1; ++x) { 
					const Ray& R = computeEyeRay(x, y, w, h, camera);
					Radiance3 L_o; 
					float distance = depthBuffer.get(x, y); 
					if (sampleRayTriangle(scene, x, y, R, T, L_o, distance)) { 
						image.set(x, y, L_o); 
						depthBuffer.set(x, y, distance);
					} 
				} 
			}
		}
	}	

结果如下图(与Ray-Casting结果几乎无差别)：

<img src="/img/16-7.png">





