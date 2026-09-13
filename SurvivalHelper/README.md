# SurvivalHelper / 生存辅助 GUI

Minecraft Bedrock 26.45 生存辅助插件。

当前版本：**v2.8.0**。

## 固定包身份

正常升级时不要更换 UUID，只提高 manifest 版本：

- Header UUID: `bc420939-9c71-4f34-a71f-6117dad3ad34`
- Data Module UUID: `3cc68508-b078-49f8-b813-ae8bd40e83c6`
- Script Module UUID: `5d450947-945e-4e78-940b-7fbb061c7887`
- 当前 manifest version: `[2,8,0]`

依赖：

- `@minecraft/server` `2.9.0`
- `@minecraft/server-ui` `2.1.0`

## 源码重建

`source/` 保留 v2.7.2 的完整 UTF-8 源码分片，`upgrade_v280.py` 是确定性的 v2.8.0 升级补丁。

执行：

```bash
python rebuild.py
```

会先拼接 `source/main.part*.js.txt`，再自动应用 `upgrade_v280.py`，最终生成当前正式版 `scripts/main.js`。

## v2.8.0 重点变化

- 指南针总菜单可同时识别 myLand 与 PlayerShop。
- 管理员中心可同时进入生存辅助、地皮系统和玩家商店管理。
- 新增 `bridge:survival_menu` / `bridge:survival_admin` 请求入口，其他插件可以通过轻量 tag 打开生存辅助 GUI，不依赖跨行为包自定义命令。
- 与 myLand / PlayerShop 继续保持独立安装，不添加硬依赖。

## 现有功能

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
