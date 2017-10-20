---
title: 雅虎API获取股票数据--Python
date: 2016-07-04 11:02:04
categories: 编程学习
tags: 
- Python
- API应用实例
---

*好久不学Python，计划用Tkinter写一个利用雅虎免费股票查询API的可视化程序*

# Yahoo股票报价API

## 获取实时数据

请求url：http://finance.yahoo.com/d/quotes.csv?s=<股票名称>&f=<数据列选项> ， 其中数据列选项由各个请求参数连接而成，详细报价服务器参数请见Yahoo官网。

	from urllib import urlopen
	import csv 			#用于解析csv格式，将字符串分割
	u = urlopen('http://quote.yahoo.com/d/quotes.csv?s=GOOG&f=sl1d1t1c1ohgvn')
	for row in csv.reader(u):
    	print row

运行以上代码可以活得股票名称为GOOG的股票的实时数据，包括订单号，最后的价格，日期，时间，变化量，开盘价，当日最高，最低和成交量。参数可以任意添加。报价服务器也支持多支股票一起查询，如 s=YHOO,GOOG,EBAY,AMZN ,返回的结果是每只股票信息占一行。

## 获取历史数据

请求地址url： [http://ichart.yahoo.com/table.csv?s=<string>&a=<int>&b=<int>&c=<int>&d=<int>&e=<int>&f=<int>&g=d&ignore=.csv](http://ichart.yahoo.com/table.csv?s=<string>&a=<int>&b=<int>&c=<int>&d=<int>&e=<int>&f=<int>&g=d&ignore=.csv)

参数列表：

- s – 股票名称
- a – 起始时间，月
- b – 起始时间，日
- c – 起始时间，年
- d – 结束时间，月
- e – 结束时间，日
- f – 结束时间，年
- g – 时间周期。

Example: g=w, 表示周期是’周’。d->’日’(day), w->’周’(week)，m->’月’(mouth)，v->’dividends only’

一定注意月份参数，其值比真实数据-1。如需要9月数据，则写为08

# 简单的可视化股票查询

	#基于python 2.7.10版本
	from urllib import urlopen
	from Tkinter import *
	import csv
	
	def req():   #响应按下button的回调函数
    	g = entry.get()
    	print g
    	if g != '':
        	url = 'http://finance.yahoo.com/d/quotes.csv?s='+g+'&f=sl1d1t1c1ohgv'
        	u = urlopen(url)
        	r = csv.reader(u)
        	for i in r:
            	for t in range(7):
                	la[t].config(text=i[t]) 

	top.geometry('450x250')
	Label(top,text='Stock name',font=(30)).grid(row=0,column=0 )   #标签

	entry = Entry(top,font=(30))             #输入文本框
	entry.grid(row=0,column=2)

	Label(top,text='Stock ticker symbol',font=(30)).grid(row=1,column=0)  #选择按钮，多选之一
	Label(top,text='Price of last trade',font=(30)).grid(row=2,column=0)
	Label(top,text='Last trade date',font=(30)).grid(row=3,column=0)
	Label(top,text='Time of last trade',font=(30)).grid(row=4,column=0)
	Label(top,text='Last opening price',font=(30)).grid(row=5,column=0)
	Label(top,text='Daily high price',font=(30)).grid(row=6,column=0)
	Label(top,text='Daily low price',font=(30)).grid(row=7,column=0)
	la1 = Label(top,font=(30))
	la2 = Label(top,font=(30))
	la3 = Label(top,font=(30))    
	la4 = Label(top,font=(30))
	la5 = Label(top,font=(30))
	la6 = Label(top,font=(30))
	la7 = Label(top,font=(30))
	la = [la1,la2,la3,la4,la5,la6,la7]
	la1.grid(row=1,column=2)
	la2.grid(row=2,column=2)
	la3.grid(row=3,column=2)
	la4.grid(row=4,column=2)
	la5.grid(row=5,column=2)
	la6.grid(row=6,column=2)
	la7.grid(row=7,column=2)
	Button(top,text='Submit',font=(35),command=req).grid(row=8,column=1)
	top.mainloop()

**运行后在文本输入框中输入GOOG，得到如下结果**

![](http://i.imgur.com/rSXPItJ.png)

**IBM的也可以查询到**

![](http://i.imgur.com/GcAbLJh.png)

有木有很神奇呢，其实很多大型网站都会提供优质的API函数，什么百度地图API，淘宝API之类的，利用这些数据可以写出方便自己获取资源的脚本。
