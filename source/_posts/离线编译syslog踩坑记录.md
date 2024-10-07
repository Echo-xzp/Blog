---
title: 离线编译syslog踩坑记录
keywords: [Linux,syslog,glib,pcre,离线编译,syslog-ng]
date: 2024-09-02 21:21:57
tags: [Linux,syslog,glib,pcre,离线编译,syslog-ng]
categories: Linux
cover:
description: "博主需要改动`syslog-ng`的源码，并重新编译`syslog-ng`。但是编译环境存在各种受限。首先是是在内网环境中，不能在线安装相关依赖，再者就是编译环境的`Linux`发行版是定制的，虽然应该是基于`CentOS`改过来的，但是系统上做了啥处理，不说`yum`和`dnf`，最基本的`rpm`都没有，通过下载`rpm`包再安装到本地的方法都不能实现了。最后就是编译环境的那些基础C库都老的很，编译`syslog-ng`达不到最低版本要求，因此啥依赖都得自己下载源码编译过来。`pkg-config` 是一个用于管理和查询已安装库的工具，特别是在编译和链接阶段。它简化了编译和链接过程中的配置工作，确保编译器和链接器能够找到和使用正确的库及其依赖项。GLib是一个通用的跨平台 C 语言库，主要用于提供基础设施功能和通用编程工具。它是 GNOME 桌面环境和 GTK+ 库的基础，广泛用于各种 C 语言程序中。报错：configure: error: Glib headers inconsistent with current compiler setting. You might be using 32 bit Glib with a 64 bit compiler, check PKG_CONFIG_PATH"
---

# 问题描述

博主需要改动`syslog-ng`的源码，并重新编译`syslog-ng`。但是编译环境存在各种受限。

首先是是在内网环境中，不能在线安装相关依赖，再者就是编译环境的`Linux`发行版是定制的，虽然应该是基于`CentOS`改过来的，但是系统上做了啥处理，不说`yum`和`dnf`，最基本的`rpm`都没有，通过下载`rpm`包再安装到本地的方法都不能实现了。最后就是编译环境的那些基础C库都老的很，编译`syslog-ng`达不到最低版本要求，因此啥依赖都得自己下载源码编译过来。在整个过程中也是踩坑无数，特此记录一下。

# 问题解决

外网还编译啥，直接包管理器安装不就好了？

```bash
sudo apt install syslog-ng
```

![image-20240902214021982](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/8_20_50_48_image-20240902214021982.png)

其实也达不到博主的要求，因为博主改动了部分源码，定制了部分功能，直接装上去也达不到要求。

不过如果在外网的话能够直接装一些依赖的库，也算简化了部分操作吧。但是现在是要实现完全离线安装，基本上包管理器是用不到了。

那么一切只能从源码编译过来了。

## `syslog-ng`源码

`github`上之际下载相关[源码](https://github.com/syslog-ng/syslog-ng/releases/download/syslog-ng-4.8.0/syslog-ng-4.8.0.tar.gz)

看`REAME`里面描述编译似乎很简单，试一试：

```bash
 ./configure && make && make install
```

想法很不错，第一步就失败：

![image-20240902215359821](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/8_20_51_30_image-20240902215359821.png)

报错明显就是`glib`不存在或者版本太低了，然后又是说`pkg-config`不存在？

那么先装个`pkg-config`再说。

## `pkg-config`安装

### 简介

首先什么是`pkg-config`？

`pkg-config` 是一个用于管理和查询已安装库的工具，特别是在编译和链接阶段。它简化了编译和链接过程中的配置工作，确保编译器和链接器能够找到和使用正确的库及其依赖项。具体来说，`pkg-config` 的主要用途包括：

#### 主要功能

1. **提供编译和链接标志**： `pkg-config` 能够查询库的编译器和链接器标志，这些标志对于正确地编译和链接程序是必要的。它提供了一种标准化的方法来获取这些标志，避免了手动配置的麻烦。

   - **编译标志**（Compiler Flags）：如头文件路径。
   - **链接标志**（Linker Flags）：如库文件路径和库名称。

   示例命令：

   ```
   bash复制代码pkg-config --cflags library-name
   pkg-config --libs library-name
   ```

2. **处理库的依赖关系**： `pkg-config` 能够处理库之间的依赖关系，并自动包含所需的标志。这意味着，如果一个库依赖于其他库，`pkg-config` 会将这些依赖的标志自动包括在内，简化了构建过程。

3. **查询库的版本信息**： 你可以使用 `pkg-config` 来获取库的版本信息，确保你使用的是正确版本的库。

   示例命令：

   ```
   bash
   
   
   复制代码
   pkg-config --modversion library-name
   ```

4. **支持多个库**： `pkg-config` 可以同时支持多个库，允许你在一个命令中查询多个库的标志，并将它们组合在一起。

   示例命令：

   ```
   bash
   
   
   复制代码
   pkg-config --cflags --libs library1 library2
   ```

#### 总结

`pkg-config` 是一个用于管理和查询已安装库的工具，它提供了一个标准化的方式来获取编译和链接所需的标志，处理库的依赖关系，并支持多个库的配置。它简化了构建过程，确保编译和链接过程中使用的是正确的库和版本。

### 安装

`pkg-config`源码地址在`github`上开源有，点击[查看](https://github.com/pkgconf/pkgconf)，但是这个是个开源版本，官方的是[这里](https://pkgconfig.freedesktop.org/releases/)

```bash
curl https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz -O
tar xzvf pkg-config-0.29.2.tar.gz
cd pkg-config-0.29.2.tar.gz
./configure
make
make install
```

注意如果`configure`的时候报错：

```
checking for glib-2.0>=2.16... no
configure:error :either a previously installed pkg-config or "glib-2.0 >= 2.16"could not be found.Please set GLIB_CFLAGS and GLIB_LIBS to the correct values or pass --with-internal-glib to configure to use the bundled copy.
```

可以指定使用`pkg-config`自带的`glib`库：

```bash
./configure --with-internal-glib
```

## 继续编译`syslog-ng`

继续执行第一节的操作，编译`syslog-ng`：

```
./configure
```

![image-20240908220407749](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/9_21_41_27_image-20240908220407749.png)

还是之前的报错，说明装了`pkg-config`貌似也解决不了问题。

那么基本上能定位到是`glib`库的问题了。

先看看系统的`glib`版本：

```bash
pkg-config --modversion glib-2.0
```

正好使用装好的`pkg-config`:

![image-20240908221345439](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/8_22_13_45_image-20240908221345439.png)

结果说没有？那么直接包管理器看看有没有装这个库：

```bash
# deb系
dpkg -s libglib2.0-dev 
# 红帽系
rpm -q glib2-devel
```

结果还是没有？

![image-20240908221629018](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/9_21_41_21_image-20240908221629018.png)

那么只能手动安装`glib`库了。

## `glib`库安装

### 简介

`glib`这个库听起来和`glibc`好接近，那么这个库实际是干啥的？

**GLib** 是一个通用的跨平台 C 语言库，主要用于提供基础设施功能和通用编程工具。它是 GNOME 桌面环境和 GTK+ 库的基础，广泛用于各种 C 语言程序中。

- **主要功能**：
  - 提供数据结构（如链表、哈希表、队列等）、文件和目录操作、线程和同步、事件循环等。
  - 提供跨平台的抽象，简化了不同操作系统上的编程工作。
  - 实现了许多标准 C 语言库没有的功能，如 Unicode 字符处理和国际化支持。
- **使用场景**：
  - 被用于构建图形用户界面（如 GTK+）
  - 被广泛应用于 GNOME 桌面环境和其他 C 语言应用程序。

### 安装

`glib`在`gitlab`上开源了的，点击[查看](https://gitlab.gnome.org/GNOME/glib/)，发行的历史源码在[这里](https://download.gnome.org/sources/glib/)查看，直接下载个最新的来编译。

```bash
curl -O https://download.gnome.org/sources/glib/2.80/glib-2.80.5.tar.xz
tar xJvf glib-2.80.5.tar.xz
cd glib-2.80.5
```

进去目录之后发现新版编译似乎不太一样啊，那就看文档咋说吧：

```bash
vim INSTALL.md
```

![image-20240908223604124](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/9_21_41_13_image-20240908223604124.png)

貌似讲的很清楚了，但是又要用到新的构建工具`meson`，`meson`要依赖`python`，这没完没了了，头大了，那只能找个老版本的不用`meson`编译的。

```bash
curl -O https://download.gnome.org/sources/glib/2.40/glib-2.40.2.tar.xz
tar xJvf glib-2.40.2.tar.xz
cd glib-2.40.2/
./configure
```

还好找到个可用的老版本，但是执行.`/configure`的时候又报错了：

![image-20240909214100330](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/9_21_41_46_image-20240909214100330.png)

这些真憋不住了。本来是不想编译`meson`特意装的老版本，结果又要编译`gettext`的库，不过至少不要依赖`python`，还稍微好点。

## `gettext`离线编译

### 简介

**`gettext`** 是一套开源的国际化（i18n）和本地化（l10n）工具，用于在软件开发中管理多语言支持。它允许程序从一种语言（通常是英语）切换到其他语言，而无需修改代码。`gettext` 为程序提供了一种机制来定义、获取和显示翻译文本，主要用于处理多语言的字符串。

`gettext` 的功能：

1. **消息翻译**：`gettext` 允许程序开发者使用简单的函数在运行时从源语言切换到目标语言。
2. **语言包管理**：通过 `.po` 和 `.mo` 文件，可以方便地管理不同语言的翻译文本。
3. **工具支持**：`gettext` 提供了多种工具来提取、合并和编译翻译文件，例如 `xgettext`、`msgmerge` 和 `msgfmt`。

### 离线编译

官网位置，点击[这里](https://www.gnu.org/software/gettext/gettext.html)。

直接官网拉下源码来编译：

```bash
curl -O https://ftp.gnu.org/pub/gnu/gettext/gettext-0.22.5.tar.gz
tar xzvf gettext-0.22.5.tar.gz
cd gettext-0.22.5/
./configure
make
make install
```

这个还好，一把就编译完成。

## `glib`编译

继续执行上面编译`glib`的操作：

```bash
./configure
make
```

结果*byd*还是有问题：

![](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/9_22_12_16_image-20240909221215855.png)

无疑就是重复定义的问题了。

拉下来的源码难道还存在问题？网上找了一下发现是编译器的问题，大概就是我的`gcc`版本太高，源码版本又老，因此你存在问题。

**解决问题博客**：[Bug 记录： gcc 7.5.0 编译 glib-2.9.6 报错 - 缘起花渊 - 博客园 (cnblogs.com)](https://www.cnblogs.com/yqmcu/p/15084263.html)

总结起来就是修改一下`./glib/gutils.h`，我的源码和博主的其实也差了几个版本，修改的地方有点出入，但是参照修改之后也能够用：

```c
// 修改前的
#ifdef G_IMPLEMENT_INLINES
 #  define G_INLINE_FUNC
 #  undef  G_CAN_INLINE
#elif defined (__GNUC__) 
#  define G_INLINE_FUNC extern inline
#elif defined (G_CAN_INLINE) 
 #  define G_INLINE_FUNC static inline
 #else /* can't inline */
 #  define G_INLINE_FUNC

// 修改后的
#ifdef G_IMPLEMENT_INLINES
 #  define G_INLINE_FUNC
 #  undef  G_CAN_INLINE
#elif defined (__GNUC__)
#  if __GNUC_PREREQ (4,2) && defined (__STDC_VERSION__) \
   && __STDC_VERSION__ >= 199901L
#    define G_INLINE_FUNC extern __inline __attribute__ ((__gnu_inline__))
#  else
#    define G_INLINE_FUNC extern __inline
#  endif
#elif defined (G_CAN_INLINE)
 #  define G_INLINE_FUNC static inline
 #else /* can't inline */
 #  define G_INLINE_FUNC
```

其实也就是改第二个`if`判断子句，只改其第一个`if`的就好了，改完再编译基本没问题了：

```bash
make clean
make
sudo make install
```

这下一次走通。

![image-20240916175449807](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/16_17_59_29_image-20240916175449807.png)

## `glib`编译的其他问题

博主在之前的编译的时候还遇到过其他问题：

- `glib`依赖`pcre`库，但是装好`pcre`库的，编译`glib`执行.`/configure`却依然报错找不到库或者不支持`UTF-8`编码，这个时候时候可用尝试加入`--with-pcre`参数
- `glib`也算比较基础的C库了，有时本地已经有这个库了，但是可能版本比较老，这个时候只能指定其他安装路径了，也就是在执行`./configure`的时候加上参数`----prefix=安装路径`

网上还找到了一篇文章，关于`glib`编译的相关问题都有描述，点击这里查看[ChinaUnix博客](http://blog.chinaunix.net/uid-31087949-id-5784871.html)

## 继续编译`syslog-ng`

这下依赖应该全有了吧，那么再次尝试编译`syslog-ng`：

### 编译配置生成

首先尝试生成`makefile`，执行：

```bash
./configure
```

还是不行：

![image-20240916175916064](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/16_17_59_16_image-20240916175916064.png)

还是找不到`glib`库，可是实际上我已经编译好并且安装好了啊，到底是什么原因造成这种问题的呢？

执行：

```bash
pkg-config --modversion glib-2.0
```

查看`glib`版本，发现`glib`根本就找不到啊，那么基本可以确定是`pkg-config`没找到`glib`的库路径了。

`pkg-config`的，默认搜寻路径：

**Linux 系统**：

- `/usr/lib/pkgconfig/`
- `/usr/share/pkgconfig/`
- `/usr/local/lib/pkgconfig/`
- `/usr/local/share/pkgconfig/`

**64 位系统**：

- `/usr/lib/x86_64-linux-gnu/pkgconfig/`
- `/usr/local/lib/x86_64-linux-gnu/pkgconfig/`

那么就是我安装的`glib`不在它的默认搜寻路径下，那么可以通过：

```bash
export PKG_CONFIG_PATH=/custom/path/to/pkgconfig:$PKG_CONFIG_PATH
```

来设置默认的搜寻路径，编译的时候同时最好把`glib`的链接库位置和头文件位置也设置一下，那么只能执行：

```bash
./configure PKG_CONFIG_PATH=/custom/path/to/pkgconfig CFLAG="-I/path/to/glib/include" LDLIBS="-L/path/to/glib/lib"
```

这次~~没有问题~~。至少编译文件现在是有了

![image-20240916182814287](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/16_18_28_14_image-20240916182814287.png)

### `configure`存在的问题

其实编译的时候可能还会报错缺少`openssl`的开发库，也就是`openssl-devel`开发库，或者就是缺失`json-c`库，也就是l`ibjson-c-dev`，再者还有其他什么库缺失的，其实如果你实际没有用到`syslog`这部分功能，其实`syslog-ng`提供了这部分的开关选项：

如关闭`ssl`加密支持：

```bash
./configure --disable-openssl
```

又或者是关闭j`son`支持：

```bash
./configure  --enable-json=no 
```

具体可以通过：

```bash
./configure  --help
```

查看配置生成详情。里面有很多参数的解释，博主看的时候才发现`glib`库的位置其实也是可以通过其他参数指定的：

![image-20240916183914148](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/16_19_2_58_image-20240916183914148.png)

初次之外，博主原来内网编译的时候还一直报错：

```
configure: error: Glib headers inconsistent with current compiler setting. You might be using 32 bit Glib with a 64 bit compiler, check PKG_CONFIG_PATH
```

一直不知道原因，后面试了很多方法发现还是`glib`库的路径没有指定好的原因，通过上面指定链接库和头文件位置解决了问题，也就是`LDLIBS`和`CFLAGS`参数。

### 编译`syslog-ng`

直接执行`make`，这次运气，直接一把通过。

![image-20240916184220479](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/09/16_18_56_28_image-20240916184220479.png)

但是原来博主还遇到了其他问题，现在找不到报错记录了，但是大概就是编译`syslog-ng`相关模块的时候找不到相应库的头文件，比如找不到`json.h`，也就是`json-c`库，这个问题最终也是通过上面讲到的**指定头文件地址**，或者直接**关闭编译相应的模块功能**解决。

现在没啥问题，直接:

```bash
sudo make install
```

即可完成安装。

## 总结

离线编译真的是要命啊，本来一行命令解决的事情，硬是搞了好久，本来已经编译过一次有点经验了，边写博客边编译，也搞了好久，中间问题层出不穷。总是由于需要一个库，结果库又有依赖，连着编译了好几个库。

之前总是感叹`Linux`这种包管理和依赖树真的是绝妙的设计，相比之下`Windows`那种一个软件自己搞一套依赖就笨重很多，但是现在回过头来看`Windows`那种依赖关系也减轻了很多不必要的负担。

编译麻烦还有一点是没有软件包管理器给我用，不然像这种库，我直接离线下载一个`rpm/dkg`包，本地再安装也是分分钟的事情，不至于这么麻烦。另外一点还是自己对C环境的编译不是很熟悉，像那种链接库的参数设置，熟悉的话遇到报错就能知道是什么库没有链接好，没有指定好路径。还是有很多要学的吧。
