---
title: 关于DNS的学习记录 其一
keywords:
  - DNS
  - TCP
  - UDP
  - tcpdump
  - named
  - Linux
  - dig
tags:
  - DNS
  - TCP
  - UDP
  - tcpdump
  - named
  - Linux
  - dig
  - 计算机网络
categories: 计算机网络
abbrlink: 94d49d67
date: 2024-08-04 19:25:03
cover:
description:
---

最近要做关于DNS服务收发包的业务，但是对于DNS实现的细节却不是很了解，于是抽空学习一下并记录一下。

# DNS简介

DNS（Domain Name System，域名系统）是互联网的重要组成部分，它将人类易读的域名（如`google.com`）转换为计算机易于处理的IP地址（如`142.250.72.14`）。这一过程使得我们能够通过域名访问网站，而不需要记住难以理解的IP地址。

当您在浏览器中输入 `google.com` 并访问该网站时，背后会发生一系列步骤来实现这一过程：

### 1. 浏览器缓存
首先，浏览器会检查其自身缓存中是否有关于 `google.com` 的IP地址记录。如果有，浏览器会直接使用这个IP地址进行访问。

### 2. 操作系统缓存
如果浏览器缓存中没有，浏览器会请求操作系统的DNS缓存。

### 3. 路由器缓存
如果操作系统缓存中没有，操作系统会查询本地网络的路由器缓存。

### 4. ISP DNS缓存
如果路由器缓存中没有，路由器会向ISP（互联网服务提供商）的DNS服务器发送查询请求。

### 5. 递归DNS查询
如果ISP的DNS服务器没有缓存结果，它会进行递归查询，过程如下：

1. **根域名服务器**：ISP的DNS服务器会向根域名服务器发送查询请求。根域名服务器知道负责管理顶级域（如 `.com`、`.net`、`.org`）的服务器位置，并返回这些顶级域服务器的地址。
   
2. **顶级域服务器**：ISP的DNS服务器向顶级域服务器发送请求，顶级域服务器知道管理特定域名（如 `google.com`）的权威DNS服务器，并返回这些权威服务器的地址。
   
3. **权威DNS服务器**：ISP的DNS服务器向权威DNS服务器发送请求，权威DNS服务器知道 `google.com` 的具体IP地址，并返回该IP地址。

### 6. 返回结果
通过上述递归查询，最终得到 `google.com` 的IP地址，这个地址会被缓存下来用于将来的查询。然后，ISP的DNS服务器会将这个IP地址返回给路由器，路由器再返回给操作系统，操作系统再返回给浏览器。

### 7. 建立连接
浏览器收到IP地址后，会通过TCP（传输控制协议）建立与该IP地址的服务器的连接。具体过程包括：

1. **DNS解析**：已完成，如上所述。
2. **TCP握手**：浏览器与目标服务器进行三次握手，建立可靠的TCP连接。
3. **HTTP请求**：连接建立后，浏览器向服务器发送HTTP请求（例如GET请求）以获取网页内容。

### 8. 服务器响应
服务器收到HTTP请求后，会处理请求并返回相应的HTML、CSS、JavaScript文件和其他资源。

### 9. 渲染页面
浏览器接收到服务器返回的资源后，会解析并渲染页面，将其显示给用户。

这就是从输入 `google.com` 到访问具体网站背后的详细过程。这个过程涉及多个步骤和技术，包括DNS解析、TCP/IP协议、HTTP协议等。

# DNS服务器

在DNS系统中，不同类型的DNS服务器扮演着不同的角色。以下是根域名服务器、顶级域服务器和权威DNS服务器的详细介绍及其例子：

### 1. 根域名服务器（Root DNS Servers）

根域名服务器是DNS系统的顶端，负责指向顶级域服务器。全球共有13个逻辑根域名服务器，但每个逻辑服务器在不同位置有多个物理实例。以下是部分根域名服务器的例子：

- **A根服务器**：
  - 运营机构：Verisign
  - IPv4地址：198.41.0.4
  - IPv6地址：2001:503:ba3e::2:30

- **B根服务器**：
  - 运营机构：信息科学研究所（ISI）
  - IPv4地址：199.9.14.201
  - IPv6地址：2001:500:200::b

- **F根服务器**：
  - 运营机构：互联网系统联盟（ISC）
  - IPv4地址：192.5.5.241
  - IPv6地址：2001:500:2f::f

### 2. 顶级域服务器（Top-Level Domain Servers）

顶级域服务器管理特定顶级域（TLD），如 `.com`、`.net`、`.org` 等，指向管理这些域名的权威DNS服务器。以下是部分顶级域服务器的例子：

- **.com TLD服务器**：
  - 运营机构：Verisign
  - 示例服务器：
    - a.gtld-servers.net（IPv4：192.5.6.30，IPv6：2001:503:a83e::2:30）
    - b.gtld-servers.net（IPv4：192.33.14.30，IPv6：2001:503:231d::2:30）

- **.org TLD服务器**：
  - 运营机构：Public Interest Registry（PIR）
  - 示例服务器：
    - a0.org.afilias-nst.info（IPv4：199.19.56.1，IPv6：2001:500:e::1）
    - b0.org.afilias-nst.org（IPv4：199.249.112.1，IPv6：2001:500:40::1）

### 3. 权威DNS服务器（Authoritative DNS Servers）

权威DNS服务器管理具体域名（如 `example.com`），提供域名的最终解析结果。以下是部分权威DNS服务器的例子：

- **example.com的权威DNS服务器**：
  - 运营机构：Example DNS Hosting Provider
  - 示例服务器：
    - ns1.example.com（IPv4：192.0.2.1）
    - ns2.example.com（IPv4：192.0.2.2）
- **google.com的权威DNS服务器**：
  - 运营机构：Google
  - 示例服务器：
    - ns1.google.com（IPv4：216.239.32.10，IPv6：2001:4860:4802:32::a）
    - ns2.google.com（IPv4：216.239.34.10，IPv6：2001:4860:4802:34::a）

### 公共DNS服务器

公共DNS服务器是递归DNS服务器，面向最终用户提供DNS解析服务。它们接受用户的DNS查询请求，递归地查询其他DNS服务器，直至找到所需的IP地址，并将结果返回给用户。公共DNS服务器通常由大型互联网公司或组织运营，旨在提供高性能、可靠和安全的DNS解析服务。

常见的公共DNS服务器有：
- **Google 公共DNS**：8.8.8.8 和 8.8.4.4
- **Cloudflare 公共DNS**：1.1.1.1 和 1.0.0.1
- **OpenDNS**：208.67.222.222 和 208.67.220.220

### 与根域名服务器、顶级域服务器和权威DNS服务器的关系

1. **用户查询和公共DNS服务器**：
   - 用户的设备（如计算机、手机）配置使用公共DNS服务器，如8.8.8.8。当用户访问网站时，设备会向配置的公共DNS服务器发送DNS查询请求。

2. **公共DNS服务器递归查询**：
   - **根域名服务器**：如果公共DNS服务器的缓存中没有所需的记录，它会向根域名服务器发送请求。根域名服务器返回顶级域服务器的地址。（.com）
   - **顶级域服务器**：公共DNS服务器向顶级域服务器发送请求，顶级域服务器返回负责特定域名的权威DNS服务器地址。（example.com）
   - **权威DNS服务器**：公共DNS服务器向权威DNS服务器发送请求，权威DNS服务器返回最终的IP地址。(www.example.com)

3. **缓存和结果返回**：
   - 公共DNS服务器将结果缓存一段时间（根据DNS记录的TTL值），以便处理未来的相同请求更快。
   - 公共DNS服务器将解析结果返回给用户的设备，完成DNS查询过程。

### 关系总结

- **根域名服务器、顶级域服务器和权威DNS服务器**构成了DNS系统的层次结构，它们负责域名的分级管理和解析。
- **公共DNS服务器**在这层次结构的顶端，面向最终用户提供递归DNS解析服务。公共DNS服务器通过查询根域名服务器、顶级域服务器和权威DNS服务器，获取所需的DNS记录，并返回给用户。

公共DNS服务器的主要功能是为用户提供快速、可靠和安全的DNS解析服务，但它们本身并不管理任何域名或域名记录，而是通过查询其他类型的DNS服务器（根域名服务器、顶级域服务器和权威DNS服务器）来获取这些信息。

### 整体流程举例

当用户查询 `www.example.com` 时，DNS查询过程如下：

1. 用户的递归DNS服务器向根域名服务器发送请求。
2. 根域名服务器返回负责 `.com` 顶级域的TLD服务器地址。
3. 递归DNS服务器向TLD服务器发送请求，TLD服务器返回负责 `example.com` 的权威DNS服务器地址。
4. 递归DNS服务器向权威DNS服务器发送请求，权威DNS服务器返回 `www.example.com` 的IP地址。
5. 递归DNS服务器将结果返回给用户的设备，完成解析过程。

通过这些服务器的协作，用户得以顺利访问目标网站。

# DNS污染

**DNS污染**（也称为**DNS投毒**或**DNS缓存投毒**）是一种网络攻击技术，通过向DNS服务器注入虚假的DNS记录来破坏域名解析服务。这种攻击可以导致用户被重定向到恶意网站或错误的服务器。

### DNS污染的基本原理

1. **伪造响应**：攻击者通过向DNS服务器发送伪造的DNS响应，欺骗DNS服务器接受虚假的记录。这些伪造的记录可能包括错误的IP地址或假域名。
2. **缓存污染**：当DNS服务器接受并缓存这些伪造记录时，它们可能会在一定时间内被用于解析请求。这样，用户访问某个域名时可能被引导到恶意网站。

### 攻击流程

1. **选择目标DNS服务器**：攻击者选择一个目标DNS服务器进行攻击，通常是一个递归DNS服务器，因为它们处理大量的DNS查询请求。
   
2. **伪造DNS响应**：
   - 攻击者向目标DNS服务器发送伪造的DNS响应包。这些响应包包含错误的IP地址或虚假的域名记录。
   - 攻击者通常使用随机的事务ID、源端口和伪造的源IP地址来增加成功的概率。

3. **注入伪造记录**：
   - 目标DNS服务器在接收到伪造的响应时，可能将其缓存。由于DNS查询过程中没有足够的验证机制，攻击者的伪造记录被认为是合法的。
   - 攻击者可能会利用各种技术（例如，猜测正确的事务ID、利用源端口攻击等）来使伪造的响应被接受。

4. **用户受害**：
   - 当用户向受影响的DNS服务器发起域名解析请求时，服务器可能返回伪造的DNS记录，导致用户被重定向到恶意网站或错误的服务器。

### 防护措施

1. **使用DNSSEC**：
   - DNSSEC（Domain Name System Security Extensions）是一个用于增加DNS安全性的扩展，通过对DNS数据进行数字签名，确保数据的完整性和真实性。启用DNSSEC可以防止DNS投毒攻击，因为伪造的DNS记录不会通过验证。

2. **随机化**：
   - 随机化源端口和事务ID可以使攻击者更难以成功伪造DNS响应。现代DNS服务器（例如BIND、Unbound）通常会启用这种随机化机制。

3. **定期清理缓存**：
   - 定期清理DNS缓存可以减少缓存中伪造记录的有效时间。

4. **启用DNS解析器安全配置**：
   - 配置DNS服务器以限制哪些IP地址可以与其进行递归查询，避免开放递归，以降低被滥用的风险。

5. **监控和日志**：
   - 监控DNS服务器的日志和流量，检测异常行为，如大量未授权的DNS响应。

### 示例

假设攻击者想通过DNS污染将`www.example.com`重定向到一个恶意网站。攻击者可能会：

1. **向目标DNS服务器发送伪造的响应**，声称`www.example.com`的IP地址是恶意网站的IP地址。
2. **成功污染目标DNS服务器的缓存**，使其接受这些伪造记录。
3. **用户访问`www.example.com`时**，会被错误地引导到恶意网站。

这种攻击能够绕过用户的正常防护措施，因为用户无法直接检测DNS解析的正确性，尤其是在没有启用DNSSEC的情况下。
