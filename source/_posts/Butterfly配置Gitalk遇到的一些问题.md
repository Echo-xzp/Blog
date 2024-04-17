---
title: Butterfly解决Gitalk密钥暴露的问题
keywords:
  - Butterfly
  - Gitalk
  - Hexo
  - Vercle
tags:
  - Butterfly
  - Gitalk
  - Hexo
  - Vercle
  - 个人博客
categories: 杂项
description: >-
  Butterfly配置Gitalk,个人博客解决Gitalk密钥暴露的问题，点击登录Github的时候一直加载，最后直接超时报错了。用Koa来中间转发一下请求，然后利用函数接口部署成一个在线服务，一开始就感觉直接配置文件中写死Gitalk的secret是十分不安全的。
abbrlink: 17b458ca
date: 2024-04-08 10:42:19
cover:
---

# 问题描述

博主最近闲的没事又在摆弄博客，想着给博客加个评论系统，`butterfly`本身集成了不少评论系统，只要在配置里面配一下就好了：

```yaml
comments:
  # Up to two comments system, the first will be shown as default
  # Choose: Disqus/Disqusjs/Livere/Gitalk/Valine/Waline/Utterances/Facebook Comments/Twikoo/Giscus/Remark42/Artalk
  use: Gitalk # Valine,Disqus
  text: true # Display the comment name next to the button
  # lazyload: The comment system will be load when comment element enters the browser's viewport.
  # If you set it to true, the comment count will be invalid
  lazyload: false
  count: false # Display comment count in post's top_img
  card_post_count: false # Display comment count in Home Page
```

我看腾讯云的那个评论系统用的人挺多的，但是考虑腾讯云在国内，搞不好~~谁乱评论，结果我背锅被拷走了~~，所以我还是想换一个，筛选了一下发现`Gitalk`很不错，基于`Github`的`issue`系统，集成进入博客以后跟踪`issue`确实跨域方便很多，看看`Gitalk`的[Github主页](https://github.com/gitalk/gitalk)，用起来其实也很简单，更何况`butterfly`已经集成的差不多了，直接`Github`申请个`oauth2`第三方应用就行了，申请点[这里](https://github.com/settings/applications/new)。

![image-20240408112036382](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/8_11_20_43_image-20240408112036382.png)

注意回调链接和主页面链接写你的博客网站就行了就行了，这个具体的配置原理应该也就是刚才说的`oauth2`了。

之后改`butterfly`的配置文件就好了：

```yaml
gitalk:
  client_id: c2e02f1625dd3048e2af
  client_secret: 不给你看
  repo: echo-xzp.github.io
  owner: echo-xzp
  admin: echo-xzp
  option:
```

仓库名就是你要集成`issue`的仓库，`owner`和`admin`写自己的用户名就行了，具体配置其实参照`Gitalk`的官方文档更加详细。

现在貌似配的都差不大了，直接推送部署，结果发现就有问题了：点击登录`Github`的时候一直加载，最后直接**超时报错**了。

# 问题分析

由于众所周知的原因，登录`Github`是经常性的抽风，大抵这就是超时的原因了。开代理后再次尝试，发现一点问题没有了。

那么有没有方法解决这个问题呢？`Github`的[issue](https://github.com/gitalk/gitalk/issues/514)就有提到，用代理请求的方式来获取，博主于是按照线索又是一顿搜索，最后找到了一个博主给出的具体[解决方案](https://prohibitorum.top/7cc2c97a15b4.html)，他还给了几种解决方法，看[代码](https://github.com/Dedicatus546/cors-server)其实也就是用`Koa` 来中间转发一下请求，然后利用函数接口部署成一个在线服务，而博主的博客刚好又是在`Vercle`上的,于是理所当然的部署`Vercle`上了,部署可以参照那个博主的[博客](https://prohibitorum.top/7cc2c97a15b4.html)，给的十分的详细，部署其实也很简单，直接`fork`一下，`Vercle`直接导入项目在`deploy`就行了，不过由于**域名污染**的原因，**必须要自定义一个域名才能正常访问接口**。再改一下`butterfly`的配置：

```yaml
gitalk:
  client_id: c2e02f1625dd3048e2af
  client_secret: 不给你看
  repo: echo-xzp.github.io
  owner: echo-xzp
  admin: echo-xzp
  proxy: https://cors-server.hitagi.icu/github_access_token
  option:
    proxy: https://cors-server.hitagi.icu/github_access_token
```

推送部署，发现这下没问题了：

![image-20240408114733344](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/8_11_47_33_image-20240408114733344.png)

# 问题拓展

貌似都解决了，但是博主从一开始就感觉直接配置文件中写死`Gitalk`的`secret`是十分不安全的，我的项目本身就是个公开仓库，这好比就是光着屁股天天跑，虽然我的`Github`也不值钱咯，但是总叫人心里不舒服。于是博主就想能不能把`secret`写进环境变量里面，然后在`yaml`里面直接引用就行了，以多年`Spring`中配置`yaml`的经验来看，是不是直接用个占位符就能实现？类似：

```yaml
gitalk:
  client_id: c2e02f1625dd3048e2af
  client_secret: ${GITALK_TOKEN}
  repo: echo-xzp.github.io
  owner: echo-xzp
  admin: echo-xzp
  proxy: https://cors-server.hitagi.icu/github_access_token
  option:
    proxy: https://cors-server.hitagi.icu/github_access_token
```

推送一下，发现直接报错了，果然不行，于是博主一想，`Spring`里面明显是有专门的处理器来处理`yaml`的，自然而然那种方式就能实现了，但是现在的`yaml`在`nodejs`完成编译，之后更是直接运行在浏览器里面了，那到底该如何替换呢？注定要光着屁股吗？

# 问题解决

回到刚才所说的，在`hexo`构建的时候是运行在`nodejs`里面的，那就大有文章可做了。首先我的项目推送上去的时候，是由`vercle`的`CI/CD`替我完成构建的，具体也就是执行`npm run build`，直接在`package.json`看一下这个命令具体执行了啥：

```json
{
  "name": "hexo-site",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "build": "hexo clean && hexo generate",
    "clean": "hexo clean",
    "deploy": "hexo deploy",
    "server": "hexo server",
    "preview": "hexo clean && hexo g && hexo s"
  },
  "hexo": {
    "version": "7.1.1"
  },
}
```

不就是清除缓存再重新生成一遍页面吗？那按照这个思路可以在前面加一句让它在生成前先处理一下配置的`yaml`。

按照这个思路，先在`hexo`根目录建立一个`scripts`文件夹，里面开始写处理`yaml`的脚本：

```javascript
// update-config.js
const fs = require('fs');
const yaml = require('js-yaml');

const update_config = () =>{
    try {
        // 读取Hexo配置文件
        const configData = fs.readFileSync('_config.butterfly.yml', 'utf8');
        
        // 解析YAML数据
        const parsedConfig = yaml.load(configData);
    
        // 修改你想要的变量，例如修改title
        // GITALK_TOKEN是环境变量，要预先配置
        parsedConfig.gitalk.client_secret = process.env.GITALK_TOKEN;
    
        // 将修改后的配置转换回YAML格式
        const newYaml = yaml.dump(parsedConfig);
    
        // 将修改后的配置写回配置文件中
        fs.writeFileSync('_config.butterfly.yml', newYaml, 'utf8');
    
        console.log("Hexo配置文件已修改成功！");
    } catch (err) {
        console.error('修改Hexo配置文件时出现错误:', err);
    }
}

module.exports = {
    update_config,
}
```

注意这里面调用了第三方库，必须在`hexo`里面先安装好:

```bash
 npm i js-yaml --save
```

然后再写个入口，再到入口里面调用刚才那个函数就好了：

```javascript
const {update_config} = require('./update-config')

const main = () =>{
    update_config();
}

main()
```

最后再修改一下构建命令：

```json
{
  "name": "hexo-site",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "build": "node scripts/index && hexo clean && hexo generate",
    "clean": "hexo clean",
    "deploy": "hexo deploy",
    "server": "hexo server",
    "preview": "hexo clean && hexo g && hexo s"
  },
  "hexo": {
    "version": "7.1.1"
  },
}
```

也就是加个：`node scripts/index`指令，轻轻松松解决。

最后就是刚才那个环境变量，`node`里面通过`process.env.你的环境变量名`能够直接获取，关键是要预先配置好，我的是部署在`vercle`里面，也就是往它里面配置就好了，具体做法是找到：`你的project` > `Setting` > `Environment Variables`，直接添加就好了，如下：

![image-20240408121428553](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/8_12_14_28_image-20240408121428553.png)

值得说一点的是你**更新环境变量后要重新部署项目才会生效**，博主就是这里折腾了好久，都配置好了还报错，还以为我这种方法不行了，结果是我没有更新部署。

按照上面的几点一步一步来基本没啥问题了，推送部署，完全没啥问题了。

# 后记

博主在查看`vercle`构建日志的时候又发现一个奇怪的事情：

![image-20240408121832594](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/04/8_12_18_32_image-20240408121832594.png)

看日志明显脚本被执行了几次，这就又有点奇怪了。于是博主进行了一系列测试，发现原来`hexo`**每次执行命令的时候都会自动执行scripts底下暴露的函数**。还找到一篇说明的[博客](https://r3zound.github.io/2023/05/hexo-custom-script/)，那么其实我的还能简化一下，`packages.json`都不要改：

```
{
  "name": "hexo-site",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "build": "hexo clean && hexo generate",
    "clean": "hexo clean",
    "deploy": "hexo deploy",
    "server": "hexo server",
    "preview": "hexo clean && hexo g && hexo s"
  },
  "hexo": {
    "version": "7.1.1"
  },
}
```

完美解决。
