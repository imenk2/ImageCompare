# Image Compare Tool
![](pic/main.png)

## 脚本运行的依赖库
openCV-python、numpy、Pillow
```#c
pip install opencv-python numpy Pillow
```

## 生成EXE
需要 pyinstaller
```#c
pip install pyinstaller
```

### 命令
```#c
:: cmd 转到安装目录
cd <..\ImageCompare>

:: 执行该命令生成带有图标的exe于dist目录中
pyinstaller -F -w -i "app.ico" --add-data "app.ico;." ImageCompare.py

```
