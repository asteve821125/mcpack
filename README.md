# Minecraft Bedrock 插件归档

这个仓库用于保存值得继续开发或作为历史参考的 Minecraft 基岩版插件源码。

## 当前维护

- `myLand/` — Minecraft Bedrock 26.45 地皮系统。当前版本 v4.2.0，使用共享金币，并与生存辅助、PlayerShop 协同。
- `SurvivalHelper/` — Minecraft Bedrock 26.45 生存辅助 GUI。当前版本 v2.8.0，支持三插件指南针总菜单与管理员中心。
- `PlayerShop/` — Minecraft Bedrock 26.45 玩家箱子商店。当前版本 v1.0.0；普通箱子 + 橡木告示牌、多商品、实时库存、市场搜索、共享金币、离线交易与双箱兼容。

## 公共协议

- 指南针协同：scoreboard objective `gui_bridge`，插件标识 `myland` / `survival` / `shop`。
- 公共金币：scoreboard objective `server_money`，参与者格式 `u:<lowercase player name>`。
- PlayerShop 保护索引：scoreboard objective `playershop_blocks`；myLand 遇到登记的商店箱子/告示牌时让 PlayerShop 优先处理。
- 跨插件 GUI 跳转使用短期玩家 tag，不依赖跨行为包 `runCommand()`。

## 历史归档 / 参考

- `ForeverDeer/` — 自定义武器、装备、模型与资源包项目。
- `Fastbuilder/` — 两点选区与结构扫描/编码原型。
- `MyGunAddon/` — 早期枪械与自定义子弹实体实验。

## 更新规则

- 已正式安装的插件正常升级必须保持原 UUID，只提高 manifest 版本。
- 新插件首次创建使用独立 UUID；后续升级保持 UUID 不变。
- 发布前检查 JavaScript 语法、manifest、依赖与 `.mcpack` 根目录结构。

> 注意：历史项目不代表当前 Minecraft Bedrock 26.45 可直接运行；其中部分使用旧版组件或脚本 API，需要升级后再使用。
