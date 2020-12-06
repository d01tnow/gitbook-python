# Scrapy



## 安装

```shell
# 使用 conda 安装
conda create -n scrapy python=3.7
conda install scrapy

```

## 快速入门

### 初始化

```shell
# 初始化项目, projectname 是项目名称
scrapy startproject projectname
# 正确创建后, 本目录下会出现 projectname 目录, 并且提示基本用法
# 创建 example
cd projectname
# 创建爬虫
scrapy genspider example www.bing.com
# 在 spiders 目录下创建了 example.py 文件
```

### 设置 items.py

items 是用于设置提取内容的结构

```python
# 提取标题, 链接, 作者
class InspectorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field(
```

## 进阶

### scrapy genspider

创建 spider

``` shell
# 查看 spider 类型
scrapy genspider -l
```

