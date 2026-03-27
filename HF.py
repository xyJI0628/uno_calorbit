# -*- coding: utf-8 -*-

# 需要导入os和sys模块
import os
import subprocess

def load_mkl():
    # 加载 MKL 库
    subprocess.run(['module', 'load', 'mkl'], check=True)

def convert_fchk_files():
    # 获取当前目录下所有的 .fchk 文件
    fchk_files = [f for f in os.listdir() if f.endswith('.fchk')]
    
    if not fchk_files:
        print("没有找到 .fchk 文件")
        return

    # 遍历每个 .fchk 文件，进行 UNO 转换
    for fchk_file in fchk_files:
        # 输出对应的 UNO 文件
        output_file = fchk_file.replace('.fchk', '-UNO.fchk')
        try:
            print(f"正在处理文件: {fchk_file}")
            # 使用 subprocess 启动 Python 解释器并执行 UNO
            subprocess.run(['python', '-c', f"from mokit.lib.gaussian import uno; uno('{fchk_file}')"], check=True)
            print(f"生成文件: {output_file}")
        except Exception as e:
            print(f"处理文件 {fchk_file} 时出错: {e}")

# 执行脚本
if __name__ == "__main__":
    load_mkl()  # 加载 MKL 库
    convert_fchk_files()  # 执行 UNO 转换
