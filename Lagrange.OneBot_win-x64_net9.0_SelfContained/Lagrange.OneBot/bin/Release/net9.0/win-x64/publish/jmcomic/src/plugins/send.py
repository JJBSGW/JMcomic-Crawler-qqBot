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
DOWNLOAD_SCRIPT = r"C:\Users\Lucky\Desktop\Bot\Lagrange.OneBot_win-x64_net9.0_SelfContained\Lagrange.OneBot\bin\Release\net9.0\win-x64\publish\jmcomic\src\plugins\P\download.py"
# 定义漫画下载目录
COMIC_DIR = r"C:\Users\Lucky\Desktop\Bot\Lagrange.OneBot_win-x64_net9.0_SelfContained\Lagrange.OneBot\bin\Release\net9.0\win-x64\publish\jmcomic\src\plugins\P"
CRAWLER_DIR = r"C:\Users\Lucky\Desktop\JMComic-Crawler-Python-master\p"

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