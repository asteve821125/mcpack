# SurvivalHelper / 生存辅助 GUI

Minecraft Bedrock 26.45 生存辅助插件。

当前仓库快照：**v2.7.2**。

## 固定包身份

正常升级时不要更换 UUID，只提高 manifest 版本：

- Header UUID: `bc420939-9c71-4f34-a71f-6117dad3ad34`
- Data Module UUID: `3cc68508-b078-49f8-b813-ae8bd40e83c6`
- Script Module UUID: `5d450947-945e-4e78-940b-7fbb061c7887`
- 当前 manifest version: `[2,7,2]`

依赖：

- `@minecraft/server` `2.9.0`
- `@minecraft/server-ui` `2.1.0`

## 源码

当前连接器以 UTF-8 文本方式写入 GitHub，因此 `scripts/main.js` 的精确源码按顺序存放在：

`source/main.part01.js.txt` ... `source/main.part04.js.txt`

执行：

```bash
python rebuild.py
```

会生成 `scripts/main.js`。这些分片按文件名顺序直接拼接即可还原当前脚本。

## 当前重点功能

- 指南针统一“服务器辅助”总菜单
- 与 myLand 独立安装或合装均可使用
- 管理员中心可动态显示当前已安装插件
- 多个人传送点，默认 6 个；管理员可设置每名玩家上限
- TNT 下界投掷
- 危险坠落保护
- 连锁挖矿、连锁砍树
- 潜行电梯
- 死亡点记录/返回
- TPA
- 坐标分享
- 全服功能开关和玩家权限管理

## 正式更新规则

1. 普通更新保持三个 UUID 不变。
2. 同步提高 `header.version` 和各 module `version`。
3. 保持 `entry: scripts/main.js`。
4. 旧数据结构发生变化时，只添加实际需要的一次性迁移，不堆无关兼容分支。
5. 发布前检查 JavaScript 语法、manifest、依赖和包根目录结构。
6. 只有明确要作为全新插件身份安装时才整套更换 UUID。

> `pack_icon.png` 属于二进制文件，当前 ChatGPT GitHub 写入接口没有直接从本地上传二进制附件的能力，因此本目录暂不包含图标；这不影响后续从仓库直接维护源码。
