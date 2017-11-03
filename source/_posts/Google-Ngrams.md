---
title: Google Ngrams
date: 2017-10-31 09:25:11
tags: Ngrams
categories: 大数据
---
<script type="text/javascript">
function change()
{
 document.getElementById("mchart").src="https://books.google.com/ngrams/interactive_chart?content=Albert+Einstein%2CSherlock+Holmes&year_start=1800&year_end=2000&corpus=15&smoothing=3&share=&direct_url=t1%3B%2CAlbert%20Einstein%3B%2Cc0%3B.t1%3B%2CSherlock%20Holmes%3B%2Cc0";
 "https://books.google.com/ngrams/interactive_chart?content="

}
</script>

Google Books Ngram Viewer是一个在谷歌扫描的所有图书中快速查询词语的使用情况的工具，谷歌扫描并数字化的图书占人类出版书籍的4%，通过这个工具可以查询到从17世纪至今，所有出版物中某些词汇出现频率的变化曲线，至2012年已经完成超过520万本图书，包含500,000,000,000个单词。Ngrams网址：https://books.google.com/ngrams

这个工具用于大数据分析可以说明一些现象，比如毛主席的受欢迎度，峰值时间段代表着什么不言自明
<iframe name="ngram_chart" src="https://books.google.com/ngrams/interactive_chart?content=%E6%AF%9B%E6%B3%BD%E4%B8%9C%2C+%E6%AF%9B%E4%B8%BB%E5%B8%AD&year_start=1900&year_end=2017&corpus=23&smoothing=3&share=&direct_url=t1%3B%2C%E6%AF%9B%E6%B3%BD%E4%B8%9C%3B%2Cc0" width=900 height=500 marginwidth=0 marginheight=0 hspace=0 vspace=0 frameborder=0 scrolling=no></iframe>

比如人们对当下的关注度很高，毕竟人们经常忘记历史，从下图可见：
<iframe name="ngram_chart" src="https://books.google.com/ngrams/interactive_chart?content=1850%2C1900%2C1950%2C2000&year_start=1800&year_end=2017&corpus=15&smoothing=3&share=&direct_url=t1%3B%2C1850%3B%2Cc0%3B.t1%3B%2C1900%3B%2Cc0%3B.t1%3B%2C1950%3B%2Cc0%3B.t1%3B%2C2000%3B%2Cc0" width=900 height=500 marginwidth=0 marginheight=0 hspace=0 vspace=0 frameborder=0 scrolling=no></iframe>

自制查询：
查询词语<input type="text" id="keywords" name="查询词语">
起始年份<input type="number" id="start_year" name="起始年份" min="1700" require="required">终止年份<input type="number" id="end_year" name="终止年份" max="2017">平滑程度<select id="smoothing"><option value="0">0</option><option value="1">1</option>       <option value="2">2</option><option value="3" selected="">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9</option><option value="10">10</option><option value="20">20</option><option value="30">30</option><option value="40">40</option><option value="50">50</option></select>
<input type="submit" id="sub" value="查询" onclick="change()">
<iframe id="mchart" name="ngram_chart" src="" width=900 height=500 marginwidth=0 marginheight=0 hspace=0 vspace=0 frameborder=0 scrolling=no></iframe>




