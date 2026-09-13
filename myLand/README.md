# myLand

Minecraft Bedrock 26.45 地皮系统。

当前仓库快照：**v4.1.2**。

## 固定包身份

正常升级时不要更换 UUID，只提高 manifest 版本：

- Header UUID: `564362d8-058b-4dff-8f02-16b35534e943`
- Data Module UUID: `861a17e6-981b-4db4-935b-99d047d83caf`
- Script Module UUID: `e40f815c-af98-47ac-a1df-8913a4d3d3c7`
- 当前 manifest version: `[1,1,2]`

依赖：

- `@minecraft/server` `2.9.0`
- `@minecraft/server-ui` `2.1.0`

## 源码

当前连接器以 UTF-8 文本方式写入 GitHub，因此 `scripts/main.js` 的精确源码按顺序存放在：

`source/main.part01.js.txt` ... `source/main.part05.js.txt`

执行：

```bash
python rebuild.py
```

会生成 `scripts/main.js`。这些分片按文件名顺序直接拼接即可还原当前脚本。

## 当前重点功能

- 指南针统一“服务器辅助”总菜单
- 与 SurvivalHelper 独立安装或合装均可使用
- 跨插件菜单使用 scoreboard 心跳 + 临时玩家标签，不通过跨包 `runCommand`
- 地皮 GUI / 管理员 GUI
- 木锄 X/Z 圈地、Y 全高度保护
- 信任、黑名单、Flags
- 经济、公开大厅、地皮出售/购买
- 欢迎语、离开语、地皮描述
- 安全传送、冷却、战斗限制
- 低频边界粒子
- 数据备份、检查、修复
- 地皮 ID 自动复用最小空闲正整数

## 正式更新规则

1. 普通更新保持三个 UUID 不变。
2. 同步提高 `header.version` 和各 module `version`。
3. 保持 `entry: scripts/main.js`。
4. 发布前检查 JavaScript 语法、manifest、依赖和包根目录结构。
5. 只有明确要作为全新插件身份安装时才整套更换 UUID。

> `pack.icon.png` 属于二进制文件，当前 ChatGPT GitHub 写入接口没有直接从本地上传二进制附件的能力，因此本目录暂不包含图标；这不影响后续从仓库直接维护源码。
