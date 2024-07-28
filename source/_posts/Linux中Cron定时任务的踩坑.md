---
title: Linux中Cron定时任务的踩坑
keywords: [CRON,corn,Linux,定时任务]
date: 2024-07-28 16:57:58
tags: [CRON,corn,Linux,定时任务]
categories: Linux
cover:
description:
---

# 前言

博主现在有个需求，需要定时执行一个脚本，于是在Linux环境中自然想到了`cron`。简单描述一下`cron`:

## 什么是 `cron` 服务？

`cron` 是 Unix 和类 Unix 操作系统中的一个守护进程，用于根据预定的时间表自动执行任务。这个服务是操作系统的核心部分，允许系统管理员和用户计划周期性任务，比如备份、系统维护和定时脚本执行。

## `cron` 表达式的语法和用法

`cron` 表达式最早出现在 Unix 系统中，作为 `cron` 守护进程的一部分，用于定期执行计划任务。`cron` 是由 Ken Thompson 在 1975 年为 Unix 操作系统编写的，其后在许多 Unix 和类 Unix 操作系统（如 Linux、BSD 等）中得到了广泛应用。

`cron` 表达式由五个字段组成，这些字段指定了任务的执行时间。每个字段之间用空格分隔，字段的顺序和含义如下：

```
* * * * * command to be executed
- - - - -
| | | | |
| | | | +----- Day of the week (0 - 7) (Sunday=0 or 7)
| | | +------- Month (1 - 12)
| | +--------- Day of the month (1 - 31)
| +----------- Hour (0 - 23)
+------------- Minute (0 - 59)
```

### 字段解释

1. **分钟（Minute）**：0-59
2. **小时（Hour）**：0-23
3. **月份中的日期（Day of Month）**：1-31
4. **月份（Month）**：1-12 或使用简写（如 Jan, Feb, Mar）
5. **星期中的日期（Day of Week）**：0-7（0 和 7 都表示星期日）或使用简写（如 Sun, Mon, Tue）

### 特殊字符

- `*`：表示任何值。
- `,`：用于指定多个值。
- `-`：用于指定值的范围。
- `/`：用于指定步长。

### 示例

#### 每天凌晨 2:30 执行任务

```sh
30 2 * * * /path/to/your/command
```

#### 每周一凌晨 3:00 执行任务

```sh
0 3 * * 1 /path/to/your/command
```

#### 每月的第一天凌晨 4:00 执行任务

```sh
0 4 1 * * /path/to/your/command
```

#### 每隔 5 分钟执行一次任务

```sh
*/5 * * * * /path/to/your/command
```

#### 每个工作日的中午 12:00 执行任务

```sh
0 12 * * 1-5 /path/to/your/command
```

## 工作原理

1. **后台运行**：`cron` 守护进程在后台运行，持续监视系统中的 `crontab` 文件和目录中的计划任务。

2. **定时检查**：`cron` 每分钟检查一次 `crontab` 文件，查看是否有需要执行的任务。

3. **执行任务**：如果当前时间匹配某个任务的时间表，`cron` 会执行该任务。

## 配置文件和目录

`cron` 服务通过几个关键的配置文件和目录来管理任务：

### 1. `/etc/crontab`
这是系统范围内的 `crontab` 文件，可以包含多个用户的任务。与用户的 `crontab` 文件不同，这个文件中每个任务需要指定用户。

格式示例：
```
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user command
0 5 * * * root /usr/bin/backup
```

### 2. `/etc/cron.d/`
这个目录包含独立的文件，每个文件可以包含一个或多个 `cron` 任务，适用于系统级别的任务。

### 3. `/var/spool/cron/crontabs/`
这个目录包含每个用户的 `crontab` 文件。这些文件是用户通过 `crontab -e` 命令创建和管理的。

### 4. `/etc/cron.hourly/`, `/etc/cron.daily/`, `/etc/cron.weekly/`, `/etc/cron.monthly/`
这些目录包含定期执行的脚本，分别在每小时、每天、每周和每月运行一次。将脚本放入相应的目录中，`cron` 将在对应的时间间隔内执行它们。

## 管理 `cron` 服务

### 启动和停止 `cron` 服务

在大多数 Linux 发行版中，`cron` 服务默认启动并在系统启动时自动运行。可以使用 `systemctl` 或 `service` 命令来手动启动、停止或重启 `cron` 服务。

使用 `systemctl`：
```sh
sudo systemctl start cron
sudo systemctl stop cron
sudo systemctl restart cron
sudo systemctl enable cron  # 在系统启动时自动启动
sudo systemctl disable cron # 禁止在系统启动时自动启动
```

使用 `service`：
```sh
sudo service cron start
sudo service cron stop
sudo service cron restart
```

### 查看 `cron` 日志

`cron` 服务的日志通常存储在系统日志文件中。查看日志可以帮助诊断任务是否正确执行。

例如，在基于 `syslog` 的系统中，可以通过以下命令查看 `cron` 日志：
```sh
grep CRON /var/log/syslog
```

在基于 `journalctl` 的系统中：
```sh
journalctl -u cron
```

## 安全性

`cron` 服务包含两个文件来控制用户的访问权限：

1. `/etc/cron.allow`：只有列在这个文件中的用户才能使用 `cron` 服务。
2. `/etc/cron.deny`：列在这个文件中的用户不能使用 `cron` 服务。

如果这两个文件都不存在，通常默认允许所有用户使用 `cron` 服务。

## 优点和缺点

### 优点
- **自动化**：减少了手动执行任务的需要。
- **灵活性**：可以精确到分钟级别的任务调度。
- **可靠性**：经过长期使用和测试，非常稳定。

### 缺点
- **复杂性**：配置文件语法可能对新用户不太友好。
- **缺乏可视化管理工具**：相比现代任务调度系统，`cron` 缺少图形界面的管理工具。

## 结论

`cron` 是 Linux 系统中一个强大且可靠的任务调度工具，通过它，可以轻松实现各种周期性任务的自动化。理解 `cron` 的基本工作原理和配置文件结构，是有效利用这一工具的关键。

# 问题描述

根据上面的描述，只要在`cron`服务对应的配置目录下增加自己的需要的脚本就行了，根据博主的需求，直接在`/etc/cron.hourly/`目录添加自己的脚本就好了。

![v](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/07/28_17_24_3_image-20240728172319429.png)

**值得注意的一点是，脚本必须要有可执行权限，不然会调度失败的。**

按照上面的说法，添加自定义脚本，并注意赋予可执行权限应该就好了吧，博主的脚本大概是这样：

```bash
#! /bin/bash

# 更新代码前执行一些操作

# 更新最新代码
git pull

# 写入一些新的东西

# 上传代码
git push
```

但是实际执行起来却没有效果，代码没有按照预期更新。

# 问题分析

首先看看自己的脚本是不是有问题，直接**手动执行**一下，确认是能**正常执行**的。

再者看看`cron`服务是不是正常运行，博主的是`debian12`，服务是由`systemd`接管的，直接`systemctl status cron`看看服务状态：

![image-20240728181223658](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/07/28_18_12_23_image-20240728181223658.png)

可见`cron`本身也是**正常运行**的。

但是在刚才的状态显示中，注意到一行：

![image-20240728181257563](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/07/28_18_12_57_image-20240728181257563.png)

根据这个提示信息搜索，发现了原因：

> 当使用 `cron` 运行任务时，如果任务产生了输出（标准输出或标准错误），默认情况下 `cron` 会尝试通过邮件发送这些输出给用户。然而，如果系统上没有安装邮件传输代理（MTA，例如 `sendmail` 或 `postfix`），就会出现“No MTA installed, discarding output”的提示。

也就是`cron`默认会以邮件的形式来发送任务输出信息，而我没有配置邮件服务，自然会有这个提示。要进一步排除问题肯定要看日志才行，那么如何解决呢？

- 重定向输出到文件

  你可以将 `cron` 任务的输出重定向到日志文件中。这样你可以查看这些文件来了解任务的执行情况。

  示例：

  假设你有一个脚本 `/path/to/your/script.sh`，你可以在 `crontab` 中将其输出重定向到文件：

  ```sh
  * * * * * /path/to/your/script.sh >> /path/to/your/logfile.log 2>&1
  ```

  这里 `>> /path/to/your/logfile.log 2>&1` 表示将标准输出和标准错误都重定向到 `/path/to/your/logfile.log` 文件中。

- 在脚本内部重定向输出

  你也可以在脚本本身内部进行输出重定向。这样可以确保所有输出都被重定向，无论脚本从哪里运行。

  示例：

  在你的脚本 `/path/to/your/script.sh` 的开头添加重定向：

  ```sh
  #!/bin/bash
  
  exec >> /path/to/your/logfile.log 2>&1
  
  # Your script content here
  echo "This is a log message"
  ```

- 安装 MTA

  如果你希望接收 `cron` 任务的邮件通知，可以安装并配置一个邮件传输代理（MTA）。常见的 MTA 包括 `sendmail` 和 `postfix`。


博主不是在`crontab`中配置的，自然只能采用第二种方法，将输出重定向到一个日志文件

```bash
#! /bin/bash
# 日志重定向
exec >> /home/xiao/logfile.log 2>&1

# 更新代码前执行一些操作

# 更新最新代码
git pull

# 写入一些新的东西

# 上传代码
git push
```

再次等待任务被执行，查看日志，发现了报错：

![image-20240728182657468](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/07/28_18_35_27_image-20240728182657468.png)

很明显就是没有`git`拉取的权限啊。我是以`ssh`的形式拉取代码的，已经把本地的`ssh`公钥配置好了，并且手动执行脚本也没有啥问题啊，为什么还会有这个报错呢？

# 问题解决

只能继续看日志，就脚本执行的结果的日志能看到的东西有限，只能分析出脚本执行失败是没有`git`权限的问题。那就看看`cron`本身的日志吧。

 `cron` 任务的执行日志通常可以通过以下几种方式查看：

在大多数 Linux 发行版中，`cron` 的执行日志记录在系统日志文件中。这些日志文件的位置和管理方式可能因发行版而异。

> ### 查看系统日志
>
> 在基于 `syslog` 的系统中，`cron` 的日志通常记录在 `/var/log/syslog` 或 `/var/log/cron` 文件中。
>
> #### 示例命令：
>
> ```sh
> grep CRON /var/log/syslog
> ```
>
> 或：
>
> ```sh
> cat /var/log/syslog | grep cron
> ```
>
> 在一些系统中，可能有专门的 `cron` 日志文件 `/var/log/cron`：
>
> ```sh
> cat /var/log/cron
> ```
>
> 在基于 `systemd` 的系统中，可以使用 `journalctl` 查看 `cron` 服务的日志：
>
> #### 示例命令：
>
> ```sh
> journalctl -u cron
> ```
>

查看日志：

![image-20240728183511779](https://gitlab.com/Echo-xzp/Resource/-/raw/main/img/2024/07/28_18_35_11_image-20240728183511779.png)

注意到上面那一行：` session closed for user root`

会话由`root`关闭，那么回到最根本的问题，`cron`**在执行的时候，是以谁的身份执行的**？

`cron` 任务在执行时的身份取决于任务的定义位置和方式。以下是几种常见情况：

> `cron` 任务在执行时的身份取决于任务的定义位置和方式。以下是几种常见情况：
>
> ## 1. 系统 `cron` 任务
>
> ### `/etc/crontab`
>
> 系统级别的 `crontab` 文件位于 `/etc/crontab`。在这个文件中，任务以明确指定的用户身份运行。每个任务行都有一个用户字段。
>
> #### 示例：
>
> ```sh
> SHELL=/bin/sh
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
> 
> # m h dom mon dow user  command
> 17 *    * * *   root    run-parts /etc/cron.hourly
> 25 6    * * *   root    run-parts /etc/cron.daily
> 47 6    * * 7   root    run-parts /etc/cron.weekly
> 52 6    1 * *   root    run-parts /etc/cron.monthly
> ```
>
> 在这个例子中，`run-parts` 命令中的所有脚本都以 `root` 用户身份运行。
>
> ### `/etc/cron.d`
>
> 类似于 `/etc/crontab`，在 `/etc/cron.d` 目录下的文件中也有一个用户字段，用于指定执行任务的用户。
>
> #### 示例：
>
> ```sh
> # /etc/cron.d/example
> SHELL=/bin/bash
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
> 
> # m h dom mon dow user  command
> 30 2 * * * root /path/to/your/script.sh
> ```
>
> ## 2. 用户 `cron` 任务
>
> ### 用户的 `crontab` 文件
>
> 用户可以通过 `crontab -e` 命令编辑他们自己的 `crontab` 文件。用户 `crontab` 文件中的任务以该用户的身份运行，不需要在任务行中指定用户。
>
> #### 示例：
>
> ```sh
> # 通过 `crontab -e` 编辑的用户 crontab 文件
> # m h dom mon dow  command
> 0 5 * * * /path/to/your/script.sh
> ```
>
> 这个任务会以当前用户身份运行。
>
> ## 3. 特定目录下的系统 `cron` 任务
>
> ### `/etc/cron.hourly`, `/etc/cron.daily`, `/etc/cron.weekly`, `/etc/cron.monthly`
>
> 这些目录中的脚本由系统 `cron` 任务（通常在 `/etc/crontab` 中定义）以指定用户（通常是 `root`）的身份运行。
>
> #### 示例：
>
> 在 `/etc/crontab` 文件中：
>
> ```sh
> # m h dom mon dow user  command
> 25 6 * * * root run-parts /etc/cron.daily
> ```
>
> 在 `/etc/cron.daily` 目录中的所有脚本都以 `root` 用户身份运行。
>
> ## 总结
>
> - **系统 `crontab` 文件（`/etc/crontab`）** 和 **`/etc/cron.d` 目录** 中的任务按照文件中指定的用户身份运行。
> - **用户 `crontab` 文件** 中的任务以相应用户的身份运行。
> - **`/etc/cron.hourly`、`/etc/cron.daily`、`/etc/cron.weekly`、`/etc/cron.monthly` 目录** 中的任务根据系统 `crontab` 文件中的定义，通常以 `root` 用户身份运行。
>
> 通过这些机制，`cron` 可以灵活地调度任务并确保它们以适当的用户权限执行。

根据第三点可知，**我的任务实际是以`root`的身份被执行的，但是实际上我`git`所配置的公钥是另外一个用户！**

那么解决其实也很好解决了，自己在`crontab`中加上自己要执行任务的脚本，配置好时间和身份，就解决问题了！

# 总结

本质上出问题还是自己对`cron`不够熟悉导致的，最关键的一点就是`cron`的运行环境和正常的shell中运行脚本有所区别：

## 1. 环境变量

当 `cron` 运行时，环境变量的设置与用户在交互式 shell 中的环境不同。常见的环境变量如 `PATH`、`HOME`、`USER` 等可能不会被正确设置。

### 解决方法
- **显式设置环境变量**：在 `cron` 作业中显式设置所需的环境变量。
- **使用绝对路径**：在 `cron` 作业中使用命令和文件的绝对路径。

### 示例：
```sh
* * * * * /usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin /path/to/your/script.sh
```

或在脚本的开头添加环境变量设置：
```sh
#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin
# 其他环境变量
/path/to/your/command
```

## 2. Shell 类型

`cron` 使用的默认 shell 是 `/bin/sh`，而不是用户在交互式 shell 中可能使用的 `/bin/bash` 或其他 shell。

### 解决方法
- **显式指定 shell**：在 `crontab` 文件或脚本中指定要使用的 shell。

### 示例：
在 `crontab` 文件的顶部指定 shell：
```sh
SHELL=/bin/bash
* * * * * /path/to/your/script.sh
```

在脚本的开头指定：
```sh
#!/bin/bash
# 脚本内容
```

## 3. 当前工作目录

当 `cron` 运行脚本时，当前工作目录通常是用户的主目录（`$HOME`），而不是脚本所在的目录。

### 解决方法
- **显式指定工作目录**：在脚本中显式切换到脚本所在的目录或所需的工作目录。

### 示例：
```sh
#!/bin/bash
cd /path/to/your/directory
# 运行命令
/path/to/your/command
```

## 4. 输出重定向

`cron` 作业的标准输出和标准错误默认会通过邮件发送给用户，但在许多系统上邮件服务未配置或不使用。

### 解决方法
- **重定向输出**：在 `cron` 作业中显式地将输出和错误重定向到日志文件。

### 示例：
```sh
* * * * * /path/to/your/script.sh >> /path/to/your/logfile 2>&1
```

## 5. 限制和权限

`cron` 作业运行时的权限是提交作业的用户的权限。确保该用户有执行脚本所需的所有权限。

## 总结

由于 `cron` 运行时的环境与交互式 shell 不同，最好在 `cron` 作业或脚本中显式设置所需的环境变量、使用绝对路径、指定工作目录，并处理输出重定向。这些措施可以确保 `cron` 作业按预期运行。

# 拓展

其实在`cron`以外，之前也知道在`systemd`中，`cron`很多功能都被`systemd timers`替代了，顺便看看它怎么用吧。

## `systemd` timers 的优势

1. **更细粒度的控制**：`systemd` timers 提供了更详细的时间和日期配置选项，支持更复杂的定时任务安排。
2. **日志记录**：`systemd` 与 `journald` 紧密集成，提供了详细的日志记录和分析功能。
3. **依赖管理**：`systemd` timers 可以与其他 `systemd` 服务和目标（targets）定义依赖关系，确保任务在适当的系统状态下运行。
4. **集成性**：所有系统服务和定时任务都可以通过统一的 `systemd` 界面进行管理和监控。

## 使用 `systemd` timers 替代 `cron`

### 创建一个 `systemd` timer

假设我们有一个脚本 `/path/to/your/script.sh`，需要每天运行一次。我们可以创建一个 `systemd` timer 和一个相应的 `systemd` 服务。

### 1. 创建 `systemd` 服务单元文件

首先，创建一个服务单元文件 `/etc/systemd/system/my-script.service`：

```ini
[Unit]
Description=Run my script

[Service]
ExecStart=/path/to/your/script.sh
```

### 2. 创建 `systemd` timer 单元文件

然后，创建一个定时器单元文件 `/etc/systemd/system/my-script.timer`：

```ini
[Unit]
Description=Run my script daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

`OnCalendar=daily` 表示这个定时器将每天运行一次。`Persistent=true` 确保即使系统在预定时间关机或重启，任务也会在下次启动时立即运行。

### 3. 启用并启动定时器

启用并启动定时器：

```sh
sudo systemctl enable my-script.timer
sudo systemctl start my-script.timer
```

### 4. 检查定时器状态

你可以使用以下命令检查定时器的状态：

```sh
systemctl status my-script.timer
```

### 5. 查看日志

使用 `journalctl` 查看服务的日志：

```sh
journalctl -u my-script.service
```

## 其他 `systemd` timers 的配置示例

### 每小时运行一次

```ini
[Timer]
OnCalendar=hourly
```

### 每周一凌晨 3 点运行一次

```ini
[Timer]
OnCalendar=Mon *-*-* 03:00:00
```

### 每个月的第一天运行一次

```ini
[Timer]
OnCalendar=monthly
```

### 使用 `AccuracySec` 和 `RandomizedDelaySec`

为了减少同时启动的定时任务的负载，可以使用 `AccuracySec` 和 `RandomizedDelaySec` 选项：

```ini
[Timer]
OnCalendar=daily
AccuracySec=1h
RandomizedDelaySec=30m
```

## 总结

`systemd` timers 提供了一个强大且灵活的替代方案，可以完全取代传统的 `cron` 定时任务。通过创建相应的 `systemd` 服务和定时器单元文件，你可以轻松管理和监控定时任务，并享受 `systemd` 提供的高级功能和集成性。
