---
title: 解决JS通过Blob下载文件时文件损坏的问题
keywords:
  - JS
  - Javascript
  - Blob
  - 前端
  - 文件损坏
tags:
  - Javascript
  - axios
  - JS
  - Blob
  - 前端
categories: 前端
description: >-
  解决JS通过Blob下载文件时文件损坏的问题，当使用`Axios`发送请求时，设置`responseType`为`Blob`会告诉`Axios`将响应数据以二进制形式返回，而不是默认的JSON格式。如果不指定`responseType`，`Axios`将默认以JSON格式解析响应数据。结合上面所说，我的理解是二进制流本身是有个对数据要求很严格，而没指定返回类型，默认就把二进制流转成了字符串，而之后又把字符串转回`blob`对象的时候，中间可能就产生了意外的错误，比如编码格式啥的，进而造成二进制流损坏，也就是要下载的文件也损坏了；而从一开始指定为`blob`对象，接收到的二进制流是什么就是什么，中间不会再有变化。
abbrlink: 8c26a9e9
date: 2024-04-17 17:34:30
cover:
---

# 问题描述

博主最近要实现一个功能，前端上传一个`Excel`，后端对表格里面的数据进行处理，处理之后将存在错误的数据的错误原因重新写入一个新的`Excel`文件里面，并用字节流返回给前端，对于`Excel`的处理使用了`EasyExel`，大概后端代码如下：

```java
 public ResponseEntity<byte[]> uploadDoc(MultipartFile docFile, Long clsId) {
        if (docFile == null || docFile.isEmpty()){
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }

        if (!Objects.requireNonNull(docFile.getOriginalFilename(),"源文件为空！").endsWith(".xlsx")){
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
		
     	ArrayList<LearnerExcel> errors = new ArrayList<>();
        try {
            EasyExcel.read(docFile.getInputStream(), LearnerExcel.class,new PageReadListener<LearnerExcel>(list -> {

			// 自定义处理逻辑    

            })).sheet().doRead();

            if (!ObjectUtils.isEmpty(errors)){
                // 回写给前端
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                // 将数据写入到 ByteArrayOutputStream 中
                EasyExcel.write(out, LearnerExcel.class).sheet(0).doWrite(errors);

                // 设置响应头信息
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
                String fileName = "错误提示.xlsx";
                fileName = URLEncoder.encode(fileName, "UTF-8");
                headers.setContentDispositionFormData("attachment", fileName);
                return ResponseEntity.ok().headers(headers).body(out.toByteArray());

            }

            // 前端接收
            return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
        } catch (IOException e) {
            log.error("EasyExcel加载文件错误");
            throw new RuntimeException(e);
        }

    }
```

没啥好说的，就是拿官方的`demo`改了一下用。之后就是前端接收数据了：

```javascript
userUpload(formData,config).then(res =>{
        // 接收到后端返回的文件数据
        if (res.status === 200){
          // 利用Blob接收文件  
          const blob = new Blob([res.data], { type: 'application/octet-stream;charset=utf-8' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = '错误提示.xlsx'; // 指定文件名
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        }

      })
```

也没啥好说的，就是把返回的二进制数据转换成一个`Blob`对象，然后生成`a`标签实现下载。

确实也没啥问题，文件也下载好了，但是当我尝试打开文件的时候却发现报错：

![image-20240417174650676](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/17_17_46_57_image-20240417174650676.png)

![image-20240417174737925](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/17_17_47_38_image-20240417174737925.png)

也就是**文件损坏**。

# 问题分析

博主于是进行排查，首先想到的是我后端输出流写`Excel`的时候是不是~~方式不对~~？因为确实没咋用过`EasyExcel`，难免怀疑自己是不是哪里写错了，于是**找了一个已经存在的文件，回写之后依旧是无法打开文件，报错文件损坏**，那大概我的后端没啥问题了，应该是**前端的接收数据的时候哪里出错了**。

那么前端看看控制台，打印一下`respone`和`blob`：

![image-20240417175456202](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/17_17_54_56_image-20240417175456202.png)

然后注意到网络里面对于请求的预览是堆**乱码**：

![image-20240417175621735](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/17_17_56_21_image-20240417175621735.png)

由于是二进制流，*我也不能断言是这个乱码是不是正常现象*，貌似现在陷入了死局，我的前端水平也就这种水平，估计是分析不出了。

# 问题解决

只能自己网上搜索了，但经过上面的分析，大概可以确定问题在**前端**上，而且还就是那个`blob`解析数据流，那么凭借这几点直接搜索，果然获得了答案：

- [关于前端js文件blob下载问题](https://segmentfault.com/q/1010000041945435)
- [理解前端blob和ArrayBuffer，前端接受文件损坏的问题 - 努力化猿的鼠 - 博客园 (cnblogs.com)](https://www.cnblogs.com/dreamaker/p/14543079.html)
- [vue 解决 post请求下载文件，下载的文件损坏打不开，结果乱码 - 莫欺 - 博客园 (cnblogs.com)](https://www.cnblogs.com/m7777/p/13492399.html)

其实说的都是一个问题，就是前端请求后端的时候，没有指定返回类型`responseType`。那么尝试修改请求：

```javascript
axios({
        url: myURL,
        method: "POST",
        responseType: "blob"
}
// 用的框架不同，改的方式大致也有点区别，不过都是添加：responseType: 'blob'      
```

改起来还挺快的，再次尝试，发现成功解决问题。

# 问题拓展

那么为什么加上这个就能解决问题了呢？

首先`JS`中`Blob`对象是什么？

> 在JavaScript中，`Blob`（Binary Large Object）对象表示了一个不可变的、原始数据的类文件对象。它通常用于存储二进制数据，比如图像、音频、视频等等。`Blob`对象可以通过多种方式创建，比如使用`Blob`构造函数，或者使用`File`对象的`slice()`方法创建。一旦创建，`Blob`对象的数据内容是不可修改的。`Blob`对象通常用于处理文件上传、处理二进制数据、以及在浏览器中进行文件操作等场景。

那么进一步分析指定和没指定`responseType`类型时，处理返回结果有何区别：

> 当使用`Axios`发送请求时，设置`responseType`为`Blob`会告诉`Axios`将响应数据以二进制形式返回，而不是默认的JSON格式。如果不指定`responseType`，`Axios`将默认以JSON格式解析响应数据。
>
> - 设置`responseType`为`Blob`：
>
>   如果将`responseType`设置为`Blob`，则响应数据将以`Blob`对象的形式返回给你。你可以直接操作这个`Blob`对象，比如将其转换为URL以供下载或展示，或者将其作为文件上传到服务器。
>
> - 未设置`responseType`：
>
>   如果不设置`responseType`，`Axios`将默认以JSON格式解析响应数据。这意味着响应数据将被解析为`JavaScript`对象，并且你可以直接访问响应数据的属性。

结合上面所说，我的理解是二进制流本身是有个对数据要求很严格，而没指定返回类型，默认就把二进制流转成了字符串，而之后又把字符串转回`blob`对象的时候，中间可能就产生了意外的错误，比如编码格式啥的，进而造成二进制流损坏，也就是要下载的文件也损坏了；而从一开始指定为`blob`对象，接收到的二进制流是什么就是什么，中间不会再有变化。

当然这是博主的猜测，但是大致感觉就是这个原因了，究其根本还是自己对前端不是太熟。
