#!/usr/bin/env python3
"""
build.py - 打包 MagiskFrida Custom 模块 ZIP

用法:
    python build.py

输出:
    MagiskFrida-custom.zip
"""

import zipfile
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BASE_DIR = PROJECT_ROOT / "base"
FILES_DIR = PROJECT_ROOT / "files"
METAINF_DIR = PROJECT_ROOT / "META-INF"
OUTPUT_ZIP = PROJECT_ROOT / "MagiskFrida-custom.zip"

# 需要打包的源目录
SOURCE_DIRS = [BASE_DIR, FILES_DIR, METAINF_DIR]

# 必须存在的文件
REQUIRED_FILES = [
    "module.prop",
    "utils.sh",
    "customize.sh",
    "action.sh",
    "service.sh",
    "META-INF/com/google/android/update-binary",
]


def collect_files():
    """收集所有要打包的文件，返回 (arcname, filepath) 列表"""
    result = []

    for src_dir in SOURCE_DIRS:
        if not src_dir.exists():
            print(f"[!] 目录不存在，跳过: {src_dir.name}")
            continue

        for root, dirs, files in os.walk(src_dir):
            for f in files:
                filepath = Path(root) / f
                # arcname = 相对于项目根目录的路径
                arcname = filepath.relative_to(PROJECT_ROOT)
                # 去掉 base/ 前缀，让文件直接在 ZIP 根目录
                if arcname.parts[0] == "base":
                    arcname = Path(*arcname.parts[1:])
                result.append((arcname.as_posix(), filepath))

    return result


def validate(files):
    """检查必须的文件是否都存在"""
    arcnames = [arcname for arcname, _ in files]
    missing = [f for f in REQUIRED_FILES if f not in arcnames]

    # 至少要有一个 frida-server 二进制
    has_binary = any(a.startswith("files/frida-server-") for a in arcnames)

    if missing:
        print("[!] 缺少文件:")
        for m in missing:
            print(f"      {m}")
        sys.exit(1)

    if not has_binary:
        print("[!] files/ 目录下没有 frida-server 二进制")
        print("    请先下载 frida-server 并放入 files/ 目录")
        sys.exit(1)

    print(f"[*] 校验通过，共 {len(files)} 个文件")


def build():
    print(f"[*] 输出: {OUTPUT_ZIP.name}")

    files = collect_files()
    validate(files)

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
        for arcname, filepath in files:
            zout.write(filepath, arcname)
            print(f"    + {arcname}")

    size_kb = OUTPUT_ZIP.stat().st_size / 1024
    print(f"\n[+] 打包完成: {OUTPUT_ZIP}")
    print(f"    大小: {size_kb:.0f} KB")


if __name__ == "__main__":
    build()
