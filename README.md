
# WeLearn 刷时长与完成度

## 一、项目信息
- **原作者**：[Avenshy](https://github.com/Avenshy)  
- **维护者**：[YZBRH/Welearn_helper](https://github.com/YZBRH/Welearn_helper)  
- **项目说明**：因 WeLearn 版本更新导致原登录方式失效，现基于 `selenium` 框架修复，脚本版权归原作者所有。


## 二、环境配置步骤

### （一）安装依赖库
在终端依次执行以下命令：  
```bash
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install selenium -i https://pypi.tuna.tsinghua.edu.cn/simple
```  


### （二）安装 Edge 浏览器驱动
1. **下载地址**：[Microsoft Edge WebDriver 下载页](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH#downloads)
2. 
3. **操作步骤**：  
   - 根据当前 Edge 浏览器版本选择对应驱动（通过 `Edge 设置 > 帮助与反馈 > 关于 Microsoft Edge` 查看版本号）。  
   - 下载后解压压缩包，将 `edgedriver_win64.exe` 文件复制到系统路径（如 `C:\Windows\System32`）或脚本运行目录。  
4. **版本对应示例**：  
   - 若 Edge 版本为 `136.0.3240.76`，下载 **Stable Channel** 下的 `136.0.3240.76 x64` 驱动。

### (三)注意
    -保证edge的驱动与程序在同一目录下
## 三、使用方法

 **运行脚本**：  
   - 双击 `刷时长启动.bat` 或 `刷完成度启动.bat`，按提示输入账号密码及课程信息。  

   - 如果真有问题，发issues或联系邮箱3150778793@qq.com

   - 6.14已测可用
## 四、项目声明
- 本脚本仅用于学习交流 
- 因使用脚本导致的账号风险或数据异常，由使用者自行承担责任。  
- 维护者仅对代码功能进行适配，不保证长期可用






