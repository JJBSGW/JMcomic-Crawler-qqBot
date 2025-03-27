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
    config_file_path = r"C:\Users\Lucky\Desktop\Bot\Lagrange.OneBot_win-x64_net9.0_SelfContained\Lagrange.OneBot\bin\Release\net9.0\win-x64\publish\jmcomic\src\plugins\P\option.yml"
    download_comic(config_file_path)
    