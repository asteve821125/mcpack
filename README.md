# Minecraft Bedrock 插件归档

这个仓库用于保存值得继续开发或作为历史参考的 Minecraft 基岩版插件源码。

## 当前维护

- `myLand/` — Minecraft Bedrock 26.45 地皮系统。当前快照 v4.1.2，包含 GUI、经济、公开大厅、权限/黑名单、管理员管理、数据维护，以及与生存辅助的指南针协同。
- `SurvivalHelper/` — Minecraft Bedrock 26.45 生存辅助 GUI。当前快照 v2.7.2，包含多个人传送点、采集辅助、TPA、死亡点、管理员设置，以及与 myLand 的指南针协同。

## 历史归档 / 参考

- `ForeverDeer/` — 自定义武器、装备、模型与资源包项目，包含永恒剑、长枪、弓、胸甲和自定义方块。
- `Fastbuilder/` — 两点选区与结构扫描/编码原型，可继续发展为蓝图与快速建造系统。
- `MyGunAddon/` — 早期枪械与自定义子弹实体实验，适合作为后续现代 Script API 重写的参考。

## 说明

- `myLand` 与 `SurvivalHelper` 的正常正式升级必须保持各自既有 UUID，只提高 manifest 版本。
- 两个当前维护项目的大型 `main.js` 以 UTF-8 源码分片保存在各自 `source/` 目录，运行各目录下的 `rebuild.py` 即可还原 `scripts/main.js`。
- `Server` 等旧版集合的核心功能已逐步被新版插件替代。

> 注意：历史项目不代表当前 Minecraft Bedrock 26.45 可直接运行；其中部分使用旧版组件或脚本 API，需要升级后再使用。
