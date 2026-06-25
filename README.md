# MagiskFrida Custom

基于 [ViRb3/magisk-frida](https://github.com/ViRb3/magisk-frida) 修改的定制版本。

## 改了什么

相比原版做了以下定制：

| 改动项 | 原版 | 本版 |
|--------|------|------|
| 监听端口 | 默认 27042 | `127.0.0.1:1234` |
| 进程名 | `frida-server` | `fr_1663` |
| 安装后二进制名 | `frida-server` | `fr_1663` |

目的是降低 frida-server 在设备上的明显特征，方便安全研究和逆向分析。

---

## 目录结构

```
magisk-frida-custom/
├── README.md               本文件
├── build.py                打包脚本，生成可刷入的 ZIP
├── base/                   模块脚本模板（已修改）
│   ├── utils.sh            核心启动逻辑
│   ├── customize.sh        安装脚本
│   ├── action.sh           面具 Action 按钮脚本
│   ├── service.sh          开机启动脚本
│   ├── post-fs-data.sh
│   └── module.prop         模块信息
├── files/                  frida-server 二进制文件
│   ├── frida-server-arm64
│   ├── frida-server-arm
│   ├── frida-server-x86
│   └── frida-server-x86_64
└── META-INF/               Magisk 模块安装器
    └── com/google/android/
        ├── update-binary
        └── updater-script
```

---

## 使用前：替换 frida-server

模块自带的 frida-server 版本可能不是你需要的。替换方法：

### 1. 下载你需要的版本

从 Frida 官方 Release 下载对应架构的 frida-server：

```
https://github.com/frida/frida/releases
```

例如你需要 arm64 版本，下载：

```
frida-server-17.x.x-android-arm64.xz
```

### 2. 解压

```sh
xz -d frida-server-17.x.x-android-arm64.xz
```

得到一个没有扩展名的文件。

### 3. 重命名并替换

**重要：文件名必须保持 `frida-server-<架构>` 格式，这是 `customize.sh` 安装时查找的名称。**

| 设备架构 | 文件名 |
|----------|--------|
| arm64 手机 | `files/frida-server-arm64` |
| arm 手机 | `files/frida-server-arm` |
| x86 模拟器 | `files/frida-server-x86` |
| x86_64 模拟器 | `files/frida-server-x86_64` |

替换 `files/` 目录下对应文件即可。

### 4. 只给 arm64 用的话

可以删掉其他三个架构文件，减小体积：

```sh
rm files/frida-server-arm
rm files/frida-server-x86
rm files/frida-server-x86_64
```

只保留 `files/frida-server-arm64`。

### 5. 版本匹配

电脑端 frida 工具版本要和手机端 frida-server 一致：

```sh
frida --version          # 电脑端
```

版本不一致会导致连接失败。

---

## 自定义端口

端口在 `base/utils.sh` 的 `start_frida_server()` 函数里：

```sh
"$FRIDA_BIN" -D -l 127.0.0.1:1234
```

### 改端口

把 `1234` 改成你要的端口，例如 `8080`：

```sh
"$FRIDA_BIN" -D -l 127.0.0.1:8080
```

### 改监听地址

| 需求 | 写法 |
|------|------|
| 仅本机访问（推荐，配合 adb forward） | `-l 127.0.0.1:1234` |
| 局域网可访问（不推荐长期开） | `-l 0.0.0.0:1234` |

改完后重新打包刷入。

---

## 自定义进程名

进程名在三个文件里同步修改：

### 1. `base/utils.sh`

```sh
FRIDA_BIN="$MODPATH/bin/fr_1663"        # 二进制路径
```

```sh
result="$(busybox pgrep 'fr_1663')"     # 进程检测
```

### 2. `base/customize.sh`

```sh
mv -f "$F_BINDIR/frida-server-$F_ARCH" "$F_BINDIR/fr_1663"
```

```sh
set_perm "$MODPATH/bin/fr_1663" 0 2000 0755 u:object_r:system_file:s0
```

### 3. `base/action.sh`

```sh
result="$(busybox pgrep 'fr_1663')"
```

把所有 `fr_1663` 替换成你想要的名字即可。注意 `files/frida-server-arm64` 这个文件名不要改，那是 ZIP 内部的安装源文件名，安装后才会重命名。

---

## 打包

### 用打包脚本

```sh
python build.py
```

会在项目根目录生成：

```
MagiskFrida-custom.zip
```

### 手动打包

把 `base/`、`files/`、`META-INF/` 三个目录的内容放到 ZIP 根目录（不要套文件夹）：

```
ZIP 根目录
├── utils.sh
├── customize.sh
├── action.sh
├── service.sh
├── post-fs-data.sh
├── module.prop
├── files/
│   └── frida-server-arm64
└── META-INF/
    └── com/google/android/
        ├── update-binary
        └── updater-script
```

**常见错误：多套了一层文件夹。** 打开 ZIP 第一层必须直接看到 `module.prop` 和 `utils.sh`。

---

## 刷入

1. 把生成的 ZIP 传到手机
2. 打开 Magisk / KernelSU / APatch
3. 模块 -> 从本地安装 -> 选择 ZIP
4. 重启手机

---

## 验证

```sh
# 查看进程（名字是 fr_1663）
ps -A | grep fr_1663

# 查看端口（1234 的十六进制是 04D2）
cat /proc/net/tcp | grep 04D2
```

两个都有输出就是成功了。

电脑端连接：

```sh
adb forward tcp:1234 tcp:1234
frida-ps -H 127.0.0.1:1234
```

---

## Credit

Original project: [ViRb3/magisk-frida](https://github.com/ViRb3/magisk-frida)
