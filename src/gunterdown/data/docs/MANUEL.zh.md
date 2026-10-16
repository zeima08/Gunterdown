Gunterdown — 终端 Markdown 编辑器

界面语言：工具 > 界面语言（Alt+U）。选择会保存。
补全语言：Alt+L，或 --lang en/ja/zh/ko/fr。
界面语言与补全语言可以分别设置。
启动时可用 --ui-lang zh（也支持 en / ja / ko / fr）。

输入时弹出候选框：拉丁字母3个字符、日语和韩语2个字符、中文1个字符。
用 ↑/↓ 或 Shift+Tab 选择，Tab 确认，Esc 关闭。
Enter 仍用于换行。Ctrl+Space 手动显示候选词。
其他语言的候选词会标注语言代码。
日语和中文在没有空格的句子中也可以补全。
请使用系统输入法输入假名、汉字或韩文。
程序不提供拼音、罗马字或拉丁字母到韩文的输入法转换。

Ctrl+S 保存；Ctrl+X 退出；F2 打开菜单；F9 切换文件树。
Shift+左/右键选择；Ctrl+U 撤销；Ctrl+Y 重做；Alt+B 切换文档。
没有候选词时，Tab 在文件树和编辑区间切换。
未保存的文档带有 * 标记；关闭时需要确认。
恢复副本每30秒保存到 GUNTERDOWN_HOME/recover/。
所有补全均在本地离线处理。英法语纠错只提供词汇建议，不检查语法。
中日韩文补全匹配已输入的原文前缀。

快捷键（Esc 返回编辑区）：

文件
  Ctrl+N       新建
  Ctrl+O       打开…
  Ctrl+R       最近的文件
  Ctrl+S       保存
  Alt+E        另存为…
  —            全部保存
  Alt+X        关闭
  —            导入
  Ctrl+E       导出
  Ctrl+P       打印
  Ctrl+X       退出
编辑
  Ctrl+U       撤销
  Ctrl+Y       重做
  Ctrl+K       剪切
  Ctrl+C       复制
  Ctrl+V       粘贴
  Ctrl+A       全选
  —            增加缩进
  —            减少缩进
  Alt+/        切换注释
  F5           插入日期
  Ctrl+L       插入链接
  Alt+I        插入图片
搜索
  Ctrl+W       查找
  Ctrl+D       下一个
  Ctrl+B       上一个
  Ctrl+\       替换
  Ctrl+G       跳转到行
  F3           跳转到标题
  —            在文件中搜索
文章
  Alt+T        模板
  Alt+F        元数据
  Alt+S        目录
  Alt+N        重新编号
  Alt+2        二级标题
  Alt+3        三级标题
  Alt+C        代码
  Alt+Q        引用
  Alt+M        表格
  Alt+P        图片说明
  Alt+V        检查 Markdown
工具
  F6           HTML 预览
  F7           统计
  F8           拼写检查
  Alt+L        补全语言
  Alt+U        界面语言
  Alt+D        自动补全
  Alt+Z        专注模式
  Alt+W        自动折行
  Alt+#        行号
  F9           文件树
  —            更改目录
  —            偏好设置
帮助
  F1           使用手册
  Alt+H        快捷键
  F12          关于
  —            诊断

主题：Alt+Y 或 工具 > 主题。↑/↓ 预览，Enter 保存，Esc 取消。
配色：dark, light, solarized, nord, dracula, ocean, contrast。
启动时使用 --theme nord。自定义主题：GUNTERDOWN_HOME/themes/*.json。
