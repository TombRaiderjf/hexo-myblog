#coding=utf-8

# python 2.7.12版本，3.0以上版本不要使用
# 需要模块：xlwt  pdfminer
#实现内容，在命令行中输入python miner.py 你的pdf存放的文件夹(！不能含有空格）的全称（如 python miner.py C:\installfile\python27\my)
# *****将此脚本与pdf置于同一个文件夹中*****
#不含异常处理，因此可能遇到意外，
#将目录下所有pdf转为txt并输出到当前工作目录下out_pdf2txt文件夹中，excel表格名为output.xls保存在当前工作目录下

import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
import xlwt
import os
import codecs

def main(argv):
    
    '''用于批量提取pdf中的词语，导出至excel'''

    def process(data):
        debug = 0
# input option default
        password = ''
        pagenos = set()
        maxpages = 0
# output option default
        outfile = root+'\\'+data+'.txt'
        imagewriter = None
        rotation = 0
        codec = 'utf-8'
        caching = True
        laparams = LAParams()
        PDFDocument.debug = debug
        PDFParser.debug = debug
        CMapDB.debug = debug
        PDFPageInterpreter.debug = debug
        rsrcmgr = PDFResourceManager(caching=caching)
        outfp = file(outfile,'w')
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,imagewriter=imagewriter)

        fp = file(data+'.pdf', 'rb')
        #检测pdf是否可以抽取文本，若不可以，直接返回
        fp_parser = PDFParser(fp)
        doc = PDFDocument(fp_parser)
        if not doc.is_extractable:
            return
        print 'Reading ...'+data+'.pdf....'
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos,maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
        fp.close()
        device.close()
        outfp.close()

        fo = codecs.open(outfile, 'r', 'utf-8')
        #向excel表格里填写数据
        tmp = fo.read()
        pos = tmp.find('/')
        if pos != -1:
            ws.write(i+1,1,tmp[:pos].strip())

        for j in range(len(wd)):
            if tmp.find(wd[j]) != -1:
                ws.write(i+1,j+3,1)
            else:
                ws.write(i+1,j+3,0)
        fo.close()

    if len(sys.argv) != 2:
        print '请输入要处理的文件夹位置'.decode('utf-8').encode('cp936')
        return
    
    file_name = argv[1]
    
    if not os.path.isdir(file_name):
        print '输入的地址不是一个文件夹'.decode('utf-8').encode('cp936')
        return
    
    files = os.listdir(file_name)
    if len(files) == 0:
        print '这是一个空文件夹'.decode('utf-8').encode('cp936')
        return
    
    s = list()
    for f in files:
        temp = os.path.splitext(f)
        if temp[1] == '.pdf':
            s.append(temp[0])
            
    if len(s) == 0:
        print '这个文件夹里没有pdf文件'.decode('utf-8').encode('cp936')
        return
    
   # 在当前目录创建excel表格 
    w = xlwt.Workbook(encoding='utf-8')
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'SimSun'
    style.font = font
    ws = w.add_sheet('Sheet1')
    # 填写表头
    wd =[ u'医患冲突', u'医疗纠纷', u'医疗事故',u'医疗暴力', u'医闹' , u'暴力伤医']
    ws.write(0,0,'编号')
    ws.write(0,1,'报刊')
    ws.write(0,2,'日期')
    for pt in range(len(wd)):
        ws.write(0,pt+3,wd[pt])

    root = 'out_pdf2txt'
    if not os.path.isdir(root):
        os.mkdir(root)
    for i in range(len(s)):
        process(s[i])

    w.save('output.xls')
    print 'Finished! '+' Successful: %s'%len(s)
    
if __name__=='__main__':
    sys.exit(main(sys.argv))
