# JMcomic-Crawler-qqBot

## 代码下载

### JMComic-Crawler-Python-master

本项目是参照了github上和csdn的两个项目进行结合得到的可以用来爬取JMcomic上的本子的qq机器人。

首先下载**JMComic-Crawler-Python-master**，将其解压。 能看见一个setup.py，在这里打开shell，输入

```pip install .```

下载所有的依赖,或者输入

```python setup.py install```

也可以。

### NoneBot+Lagrange

根据你的操作系统选择你所需要的拉格朗日的压缩包

Releases · LagrangeDev/Lagrange.Core

我这里选择的是winodws的版本

![Uploading e4b6af5a3fbd9ccd6d2189ff484d161a.png…]()


将其解压后运行Lagrange.OneBot.exe文件

就会出现扫码登录的界面，使用你想要登录的qq小号扫码即可

### 代码编写

接下来按照JMComic-Crawler-Python-master的要求

我们需要一个option来配置下载本子，这个option.yml在JMComic-Crawler-Python-master的官方文档里面也有提到。

以下是我的代码部分

```
# 开启jmcomic的日志输出，默认为true

# 对日志有需求的可进一步参考文档 → https://jmcomic.readthedocs.io/en/latest/tutorial/11_log_custom/

log: true

# 配置客户端相关

client:

  # impl: 客户端实现类，不配置默认会使用JmModuleConfig.DEFAULT_CLIENT_IMPL

  # 可配置:

  #  html - 表示网页端

  #  api - 表示APP端

  # APP端不限ip兼容性好，网页端限制ip地区但效率高

  impl: api

  # domain: 域名配置，默认是 []，表示运行时自动获取域名。

  # 可配置特定域名，如下：

  # 程序会先用第一个域名，如果第一个域名重试n次失败，则换下一个域名重试，以此类推。

  domain: []

  # retry_times: 请求失败重试次数，默认为5

  retry_times: 5

  # postman: 请求配置

  postman:
    meta_data:
      # proxies: 代理配置，默认是 system，表示使用系统代理。
      # 以下的写法都可以:
      # proxies: null # 不使用代理
      # proxies: clash
      # proxies: v2ray
      # proxies: 127.0.0.1:7890
      # proxies:
      #   http: 127.0.0.1:7890
      #   https: 127.0.0.1:7890
      proxies: system

      # cookies: 帐号配置，默认是 null，表示未登录状态访问JM。
      # 禁漫的大部分本子，下载是不需要登录的；少部分敏感题材需要登录才能看。
      # 如果你希望以登录状态下载本子，最简单的方式是配置一下浏览器的cookies，
      # 不用全部cookies，只要那个叫 AVS 就行。
      # 特别注意！！！(https://github.com/hect0x7/JMComic-Crawler-Python/issues/104)
      # cookies是区分域名的：
      # 假如你要访问的是 `18comic.vip`，那么你配置的cookies也要来自于 `18comic.vip`，不能配置来自于 `jm-comic.club` 的cookies。
      # 如果你发现配置了cookies还是没有效果，大概率就是你配置的cookies和代码访问的域名不一致。
      cookies: null # 这个值是乱打的，不能用

# 下载配置

download:
  cache: true # 如果要下载的文件在磁盘上已存在，不用再下一遍了吧？默认为true
  image:
    decode: true # JM的原图是混淆过的，要不要还原？默认为true
    suffix: .jpg # 把图片都转为.jpg格式，默认为null，表示不转换。
  threading:
    # image: 同时下载的图片数，默认是30张图
    # 数值大，下得快，配置要求高，对禁漫压力大
    # 数值小，下得慢，配置要求低，对禁漫压力小
    # PS: 禁漫网页一次最多请求50张图
    image: 30
    # photo: 同时下载的章节数，不配置默认是cpu的线程数。例如8核16线程的cpu → 16.
    photo: 16



# 文件夹规则配置，决定图片文件存放在你的电脑上的哪个文件夹

dir_rule:

  # base_dir: 根目录。

  # 此配置也支持引用环境变量，例如

  # base_dir: ${JM_DIR}/下载文件夹/

  base_dir: 

  # rule: 规则dsl。

  # 本项只建议了解编程的朋友定制，实现在这个类: jmcomic.jm_option.DirRule

  # 写法:

  # 1. 以'Bd'开头，表示根目录

  # 2. 文件夹每增加一层，使用 '_' 或者 '/' 区隔

  # 3. 用Pxxx或者Ayyy指代文件夹名，意思是 JmPhotoDetail.xxx / JmAlbumDetail的.yyy。xxx和yyy可以写什么需要看源码。

  # 

  # 下面演示如果要使用禁漫网站的默认下载方式，该怎么写:

  # 规则: 根目录 / 本子id / 章节序号 / 图片文件

  # rule: 'Bd  / Aid   / Pindex'

  # rule: 'Bd_Aid

  # 默认规则是: 根目录 / 章节标题 / 图片文件

  rule: Bd_Pid

# 插件的配置示例

plugins:
  after_album:
    - plugin: img2pdf
      kwargs:
        pdf_dir: # pdf存放文件夹
        filename_rule: Aid # pdf命名规则，A代表album, name代表使用album.name也就是本子名称




其中的文件夹存放位置需要自己确定，代码源文件也可以查看JMComic-Crawler-Python-master里面提到的官方文档

然后我们就需要一个用来下载本子的py文件了

以下是我的下载代码

import jmcomic
import time

def download_comic(config_file_path):
    """
    下载漫画的函数
    :param config_file_path: 配置文件的路径
    """
    # 创建配置对象
    option = jmcomic.create_option_by_file(config_file_path)
    print("配置对象已初始化。")

    # 获取用户输入的漫画 ID
    print("请输入漫画 ID:")
    Id = input()
    
    # 使用 option 对象来下载漫画
    jmcomic.download_album(Id, option)
    print(f"漫画 {Id} 下载完成。")
    
    # 如果需要实现删除功能，可以在这里调用 delete_album 函数
    # delete_album(Id)

# 调用函数

if __name__ == "__main__":
    config_file_path = r"你的配置文件的路径"
    download_comic(config_file_path)
    




到这里使用这个代码就可以在本机上下载本子了，但是我们如果想要在qq机器人上也能下载，我们需要再配置一个用来发送下载的本子的py代码

from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment
import os
import sys
import subprocess
from pathlib import Path
import re
import asyncio
from typing import Optional
import shutil

# 定义正则表达式匹配命令

Test = on_regex(pattern=r'^测试$', priority=1)

@Test.handle()
async def Test_send(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg = "Bot启动正常"
    await Test.finish(message=Message(msg))

# download.py 路径

DOWNLOAD_SCRIPT = r""

# 定义漫画下载目录

COMIC_DIR = r""
CRAWLER_DIR = r""

# 创建命令处理器

jm_download = on_regex(pattern=r'^/jm\s+(\d+)$', priority=1)


async def execute_download(comic_id: str):
    """执行下载脚本并返回是否成功"""
    proc = None
    try:
        cmd = f'"{sys.executable}" "{DOWNLOAD_SCRIPT}"'
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(DOWNLOAD_SCRIPT)
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=comic_id.encode()),
            timeout=300.0  # 5分钟超时
        )
    
        if proc.returncode != 0:
            error_msg = stderr.decode('gbk', errors='ignore') if stderr else "未知错误"
            return False, f"下载失败: {error_msg}"
    
        return True, "下载成功"
    except asyncio.TimeoutError:
        if proc and proc.returncode is None:
            proc.kill()
            await proc.wait()
        return False, "下载超时"
    except Exception as e:
        return False, f"执行错误: {str(e)}"
    finally:
        if proc and proc.returncode is None:
            proc.kill()

async def safe_delete(path: Path):
    """安全删除文件或目录"""
    try:
        if path.exists():
            if path.is_file():
                os.remove(path)
                print(f"已删除文件: {path}")
            else:
                shutil.rmtree(path)
                print(f"已删除目录: {path}")
            return True
        return False
    except Exception as e:
        print(f"删除失败 {path}: {str(e)}")
        return False


@jm_download.handle()
async def handle_jm_download(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg = event.get_plaintext().strip()
    match = re.match(r'^/jm\s+(\d+)$', msg)
    if not match:
        await jm_download.finish("命令格式错误，请使用 /jm <漫画ID>")

    comic_id = match.group(1)
    pdf_file = None
    comic_folder = None
    
    try:
        # 发送开始消息
        await bot.send(event, Message(f"开始下载漫画 {comic_id}，这可能需要几分钟..."))
    
        # 执行下载
        success, result = await execute_download(comic_id)
        if not success:
            await jm_download.finish(result)
    
        # 查找PDF文件
        pdf_files = list(Path(COMIC_DIR).glob(f"*{comic_id}*.pdf"))
        if not pdf_files:
            await jm_download.finish(f"下载完成但未找到PDF文件，请检查目录: {COMIC_DIR}")
    
        pdf_file = pdf_files[0]
        # 获取爬虫目录下的同名文件夹
        comic_folder = Path(CRAWLER_DIR) / comic_id
    
        # 发送文件
        try:
            await bot.call_api(
                "upload_group_file",
                group_id=event.group_id,
                file=str(pdf_file),
                name=pdf_file.name
            )
            await bot.send(event, Message(f"漫画 {comic_id} 下载完成! 文件已上传"))
    
            # 发送成功后清理文件
            deleted_files = []
    
            # 删除PDF文件
            if await safe_delete(pdf_file):
                deleted_files.append(f"PDF文件: {pdf_file.name}")
    
            # 删除爬虫目录下的文件夹
            if await safe_delete(comic_folder):
                deleted_files.append(f"原始文件夹: {comic_folder.name}")
    
            if deleted_files:
                await bot.send(event, Message(f"已清理: {', '.join(deleted_files)}"))
    
        except Exception as e:
            await jm_download.finish(f"文件发送失败: {str(e)}")
    
    except Exception as e:
        await jm_download.finish(f"处理出错: {str(e)}")
    finally:
        # 确保无论如何都尝试清理
        cleanup_tasks = []
        if pdf_file and pdf_file.exists():
            cleanup_tasks.append(safe_delete(pdf_file))
        if comic_folder and comic_folder.exists():
            cleanup_tasks.append(safe_delete(comic_folder))
    
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)


```


这段代码实现了下载代码到本地再接受qq群聊中的代码，再将下载下来的文件发送出去，最后再删除下载的本子，不会一直存储在电脑上，造成电脑的负担加重。

### 配置qq机器人

那么最后我们只需要配置qq机器人即可了，参考NoneBot+Lagrange搭建qq机器人保姆级别教程_lagrange.onebot-CSDN博客提到的即可，写的非常详细了。

如果最后发现提示qq版本过低，可以删除配置文件再从头来一次。

参考github地址： https://github.com/hect0x7/JMComic-Crawler-Python

[Releases · LagrangeDev/Lagrange.Core](https://github.com/LagrangeDev/Lagrange.Core/releases)

参考csdn地址： https://blog.csdn.net/m0_66648798/article/details/141038846
