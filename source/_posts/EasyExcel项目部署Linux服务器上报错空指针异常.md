---
title: EasyExcel项目部署Linux服务器上报错空指针异常
keywords:
  - EasyExcel
  - Linux
  - 空指针异常
  - Spring
  - Windows
  - docker
tags:
  - EasyExcel
  - Linux
  - Spring
  - Java
  - docker
categories: Java
description: >-
  EasyExcel项目部署Linux服务器上报错空指针异常;错误码为500的内部服务器异常，异常类型是：`java.lang.NullPointerException`，也就是空指针异常，而且报错信息竟然是无可用信息。日志根本看不出是什么原因造成了这个接口的错误。那么就看后台的日志吧，因为是通过`docker`部署的，那么直接`logs`查看日志：java.lang.NullPointerException:
  null at sun.awt.FontConfiguration.getVersion(FontConfiguration.java:1264) at
  sun.awt.FontConfiguration.readFontConfigFile(FontConfiguration.java:219) at
  sun.awt.FontConfiguration.init(FontConfiguration.java:107) at
  sun.awt.X11FontManager.createFontConfiguration(X11FontManager.java:774) at
  sun.font.SunFontManager$2.run(SunFontManager.java:431)
  结合上面的分析，可以知道，问题的根源就是：`alpine`的精简系统里面缺失基础字体！
abbrlink: 507a0589
date: 2024-04-19 10:35:20
cover:
---

# 问题描述

博主的`Spring`项目中有个接口功能是接收数据，并通过`EasyExcel`写入相关数据并返回数据流。在本地已经完成开发，测试也并没有什么问题，于是并通过`docker`构建镜像并部署到`Linux`服务器上，构建镜像的`dockerfile`如下：

```dockerfile
FROM openjdk:8-alpine
ARG JAVA_OPTS="-Xmx128M"
ENV JAVA_OPTS=$JAVA_OPTS
ENV RUN_ARGS=$RUN_ARGS
WORKDIR service
ADD target/app.jar app.jar
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar app.jar $RUN_ARGS"]
```

采用的是`java:8-alpine`的基础镜像，运行容器，没有啥问题。

但是博主测试刚才说的`EasyExcel`生成`excel`表格的接口时，却发生了**错误**，在浏览器开发者工具栏网络里面查看发现**报错结果**：

![image-20240419105116108](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/19_10_51_23_image-20240419105116108.png)

错误码为`500`的内部服务器异常，异常类型是：`java.lang.NullPointerException`，也就是**空指针异常**，而且报错信息竟然是*无可用信息*。

# 问题分析

那从浏览器日志根本看不出是什么原因造成了这个接口的错误。那么就看后台的日志吧，因为是通过`docker`部署的，那么直接`logs`查看日志：

```
2024-04-19 02:50:41.240 ERROR 7 --- [nio-8190-exec-4] o.a.c.c.C.[.[.[/].[dispatcherServlet]    : Servlet.service() for servlet [dispatcherServlet] in context with path [] threw exception [Request processing failed; nested exception is java.lang.NullPointerException] with root cause

java.lang.NullPointerException: null
        at sun.awt.FontConfiguration.getVersion(FontConfiguration.java:1264)
        at sun.awt.FontConfiguration.readFontConfigFile(FontConfiguration.java:219)
        at sun.awt.FontConfiguration.init(FontConfiguration.java:107)
        at sun.awt.X11FontManager.createFontConfiguration(X11FontManager.java:774)
        at sun.font.SunFontManager$2.run(SunFontManager.java:431)
        at java.security.AccessController.doPrivileged(Native Method)
        at sun.font.SunFontManager.<init>(SunFontManager.java:376)
        at sun.awt.FcFontManager.<init>(FcFontManager.java:35)
        at sun.awt.X11FontManager.<init>(X11FontManager.java:57)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:62)
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:423)
        at java.lang.Class.newInstance(Class.java:442)
        at sun.font.FontManagerFactory$1.run(FontManagerFactory.java:83)
        at java.security.AccessController.doPrivileged(Native Method)
        at sun.font.FontManagerFactory.getInstance(FontManagerFactory.java:74)
        at java.awt.Font.getFont2D(Font.java:491)
        at java.awt.Font.canDisplayUpTo(Font.java:2060)
        at java.awt.font.TextLayout.singleFont(TextLayout.java:470)
        at java.awt.font.TextLayout.<init>(TextLayout.java:531)
        at org.apache.poi.ss.util.SheetUtil.getDefaultCharWidth(SheetUtil.java:273)
        at org.apache.poi.xssf.streaming.AutoSizeColumnTracker.<init>(AutoSizeColumnTracker.java:117)
        at org.apache.poi.xssf.streaming.SXSSFSheet.<init>(SXSSFSheet.java:82)
        at org.apache.poi.xssf.streaming.SXSSFWorkbook.createAndRegisterSXSSFSheet(SXSSFWorkbook.java:684)
        at org.apache.poi.xssf.streaming.SXSSFWorkbook.createSheet(SXSSFWorkbook.java:705)
        at org.apache.poi.xssf.streaming.SXSSFWorkbook.createSheet(SXSSFWorkbook.java:88)
        at com.alibaba.excel.util.WorkBookUtil.createSheet(WorkBookUtil.java:84)
        at com.alibaba.excel.context.WriteContextImpl.createSheet(WriteContextImpl.java:223)
        at com.alibaba.excel.context.WriteContextImpl.initSheet(WriteContextImpl.java:182)
        at com.alibaba.excel.context.WriteContextImpl.currentSheet(WriteContextImpl.java:135)
        at com.alibaba.excel.write.ExcelBuilderImpl.addContent(ExcelBuilderImpl.java:54)
        at com.alibaba.excel.ExcelWriter.write(ExcelWriter.java:70)
        at com.alibaba.excel.ExcelWriter.write(ExcelWriter.java:47)
        at com.alibaba.excel.write.builder.ExcelWriterSheetBuilder.doWrite(ExcelWriterSheetBuilder.java:62)
```

从异常抛出栈来看，是由于`FontConfiguration`这个类报错产生的，而且它又在图像库`awt`下，结合它的名字，应该是和**字体**相关的吧，这个时候我又想到我的项目是在`docker`里面运行的，而且还是`alpine`类型的精简系统，是不是**字体缺失**造成的？在调用栈里面也可以明显看到有个`readFontConfigFile`的方法，看名字应该就是读取系统字体配置吧。

那么进行尝试吧：

先进入`docker`容器：

```
docker exec -it <容器名> sh
```

本来想看看系统里有啥字体的，执行:

```
fc-list
```

结果说没这个命令，那也就是`fontconfig`也没有装吧。

那在`Alpine Linux`里面`apk`应该总有吧：

![image-20240419112616949](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/19_11_26_17_image-20240419112616949.png)

那有`apk`就好办呐，先换个中科大源：

```bash
sed -i 's/http:\/\/dl-cdn.alpinelinux.org/https:\/\/mirrors.ustc.edu.cn/g' /etc/apk/repositories
apk update
```

先装个`fontconfig`来看看字体吧：

```bash
apk add fontconfig
```

再看看有啥字体吧:

```bash
fc-list
```

结果输出直接为空，也就是说**这个精简系统里面啥字体都没有**呐！

那么装上基础字体试试：

```
apk add ttf-dejavu
```

再更新一下字体缓存：

```bash
mkfontscale && mkfontdir && fc-cache
```

再退到宿主机，**重启一下容器**，发现接口能正常访问了。

# 问题解决

结合上面的分析，可以知道，问题的**根源**就是：`alpine`的**精简系统里面缺失基础字体**！

所以这个锅应该由`docker`的镜像来背，而不是`EasyExcel`运行在`Linux`系统上本身就有啥问题，针对于此，解决的方法也有很多：

1. 不使用精简版的`alpine`基础镜像，而是使用功能齐全的其他镜像，比如把`openjdk:8-alpine`换成`openjdk:8`

   ```dockerfile
   #采用环境齐全的镜像
   FROM openjdk:8
   ARG JAVA_OPTS="-Xmx128M"
   ENV JAVA_OPTS=$JAVA_OPTS
   ENV RUN_ARGS=$RUN_ARGS
   WORKDIR service
   ADD target/app.jar app.jar
   ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar app.jar $RUN_ARGS"]2
   ```

   

2. 像我上面分析的那样，镜像里面自己下个基础字体的包，但是肯定不能真像我那样部署好了再进入容器里面搞，不能每次部署都要自己操作一遍吧。因此更好的解决方法是`dockerfile`里面加入我刚才执行的命令，自己封装一个镜像：

   ```dockerfile
   FROM openjdk:8-alpine
   ARG JAVA_OPTS="-Xmx128M"
   ENV JAVA_OPTS=$JAVA_OPTS
   ENV RUN_ARGS=$RUN_ARGS
   RUN sed -i 's/http:\/\/dl-cdn.alpinelinux.org/https:\/\/mirrors.ustc.edu.cn/g' /etc/apk/repositories && apk update
   RUN apk add ttf-dejavu fontconfig && rm -rf /var/cache/apk/* && mkfontscale && mkfontdir && fc-cache
   WORKDIR service
   ADD target/app.jar app.jar
   ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar app.jar $RUN_ARGS"]
   ```

两种方法都行吧，图省事其实还是第一种方法好，换个镜像就解决问题了，但是相应的可能构建的镜像稍微大了一点。

顺便引用一下普通镜像和`alpine`版本镜像有何区别：

> `openjdk:x-alpine` 和 `openjdk:x` 镜像之间的主要区别在于基础操作系统的不同：
>
> 1. **openjdk:x-alpine：** 这个镜像基于 Alpine Linux 发行版构建。Alpine Linux 是一个轻量级的 Linux 发行版，专注于简洁和精简，因此 `openjdk:x-alpine` 镜像通常比较小，体积更小，适合用于构建轻量级的 Docker 容器。Alpine Linux 使用 `musl` C 库替代了传统的 `glibc`，并使用 `apk` 包管理器来管理软件包。
> 2. **openjdk:x：** 这个镜像通常基于常见的 Linux 发行版，如 Ubuntu、Debian、CentOS 等。这些发行版通常包含了更多的软件包和工具，因此 `openjdk:x` 镜像的体积通常比较大。与 Alpine Linux 不同，这些常见的 Linux 发行版使用传统的 `glibc` C 库，并使用 `apt`（或者 `apt-get`）包管理器（在 Debian/Ubuntu 等）或者 `yum` 包管理器（在 CentOS/RHEL 等）来管理软件包。
