# myLand

Minecraft Bedrock 26.45 地皮系统。

当前版本：**v4.2.0**。

## 固定包身份

正常升级时不要更换 UUID，只提高 manifest 版本：

- Header UUID: `564362d8-058b-4dff-8f02-16b35534e943`
- Data Module UUID: `861a17e6-981b-4db4-935b-99d047d83caf`
- Script Module UUID: `e40f815c-af98-47ac-a1df-8913a4d3d3c7`
- 当前 manifest version: `[1,2,0]`

依赖：

- `@minecraft/server` `2.9.0`
- `@minecraft/server-ui` `2.1.0`

## 源码重建

`source/` 保留 v4.1.2 的完整 UTF-8 源码分片，`upgrade_v420.py` 是确定性的 v4.2.0 升级补丁。

执行：

```bash
python rebuild.py
```

会先拼接 `source/main.part*.js.txt`，再自动应用 `upgrade_v420.py`，最终生成当前正式版 `scripts/main.js`。

## v4.2.0 重点变化

- 公共金币改为 scoreboard objective：`server_money`。
- 首次升级会把旧 `state.economy.balances` 一次性迁移到共享金币，并用 `server_economy_meta` 标记，避免重复覆盖。
- 与 PlayerShop 使用同一份金币，myLand 卸载不会删除公共余额。
- 指南针总菜单可同时识别 `survival` / `shop`。
- 管理员中心可同时进入地皮、生存辅助和玩家商店管理。
- 共享 `playershop_blocks` 保护索引：已登记商店箱子/告示牌由 PlayerShop 优先处理，避免 myLand 的普通容器/破坏规则与商店冲突。
- PlayerShop 创建商店时可通过短期 tag 请求 myLand 判断“是否为创建者自己的地皮”；不直接读取 myLand 数据文件。

## 现有功能

- 地皮 GUI / 管理员 GUI
- 木锄 X/Z 圈地、Y 全高度保护
- 信任、黑名单、Flags
- 公共金币、公开大厅、地皮出售/购买
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
