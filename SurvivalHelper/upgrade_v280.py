from pathlib import Path

p = Path(__file__).resolve().parent / "scripts" / "main.js"
s = p.read_text(encoding="utf-8")

s = s.replace('const PLUGIN_VERSION = "2.7.2";', 'const PLUGIN_VERSION = "2.8.0";')
s = s.replace('const BRIDGE_OTHER = "myland";\n', 'const BRIDGE_PEERS = ["myland", "shop"];\n')
s = s.replace(
    'const BRIDGE_TAG_LAND_ADMIN = "bridge:myland_admin";\n',
    'const BRIDGE_TAG_LAND_ADMIN = "bridge:myland_admin";\n'
    'const BRIDGE_TAG_SHOP_MENU = "bridge:playershop_menu";\n'
    'const BRIDGE_TAG_SHOP_ADMIN = "bridge:playershop_admin";\n'
    'const BRIDGE_TAG_SELF_MENU = "bridge:survival_menu";\n'
    'const BRIDGE_TAG_SELF_ADMIN = "bridge:survival_admin";\n'
)

old = '''function pulseBridge() {
  const obj = getBridgeObjective();
  if (!obj) return;
  try {
    obj.setScore(BRIDGE_SELF, BRIDGE_TTL);
    const other = obj.getScore(BRIDGE_OTHER) ?? 0;
    if (other > 0) obj.setScore(BRIDGE_OTHER, Math.max(0, other - 1));
  } catch {}
}
'''
new = '''function pulseBridge() {
  const obj = getBridgeObjective();
  if (!obj) return;
  try {
    obj.setScore(BRIDGE_SELF, BRIDGE_TTL);
    for (const peer of BRIDGE_PEERS) {
      const score = obj.getScore(peer) ?? 0;
      if (score > 0) obj.setScore(peer, Math.max(0, score - 1));
    }
  } catch {}
}
'''
assert old in s
s = s.replace(old, new)

hstart = s.index('async function showCompassHub(player) {')
hend = s.index('async function showMainMenu(player) {', hstart)
hub = '''async function showCompassHub(player) {
  if (!player?.isValid) return;
  try {
    const hasLand = bridgeAlive("myland");
    const hasShop = bridgeAlive("shop");
    const enabled = ["生存辅助", ...(hasLand ? ["地皮系统"] : []), ...(hasShop ? ["玩家商店"] : [])].join("、");
    const admin = isAdmin(player);
    const form = new ActionFormData().title("§l服务器辅助").body(`当前已启用：${enabled}。\n\n请选择要进入的系统。`)
      .button("§a生存辅助\n§7采集、传送、玩家互助等");
    if (hasLand) form.button("§e地皮系统\n§7地皮、经济、公开大厅等");
    if (hasShop) form.button("§b玩家商店\n§7箱子商店、市场搜索、交易管理");
    if (admin) form.button("§6管理员中心\n§7管理已启用的插件");
    const response = await form.show(player);
    if (response.canceled) return;
    let index = 0;
    if (response.selection === index++) return system.run(() => showMainMenu(player));
    if (hasLand && response.selection === index++) { try { player.addTag(BRIDGE_TAG_LAND_MENU); } catch {} return; }
    if (hasShop && response.selection === index++) { try { player.addTag(BRIDGE_TAG_SHOP_MENU); } catch {} return; }
    if (admin && response.selection === index) return system.run(() => showCompassAdminHub(player));
  } catch (error) { console.warn(`[生存辅助] 打开统一指南针菜单失败: ${error}`); }
}

async function showCompassAdminHub(player) {
  if (!player?.isValid || !isAdmin(player)) return;
  try {
    const hasLand = bridgeAlive("myland");
    const hasShop = bridgeAlive("shop");
    const form = new ActionFormData().title("§l管理员中心").body("管理当前已启用的插件")
      .button("§a生存辅助管理\n§7全服开关、玩家权限、传送点上限");
    if (hasLand) form.button("§e地皮系统管理\n§7地皮、经济、备份与修复");
    if (hasShop) form.button("§b玩家商店管理\n§7商店、交易与经济设置");
    form.button("返回总菜单");
    const response = await form.show(player);
    if (response.canceled) return;
    let index = 0;
    if (response.selection === index++) return system.run(() => showAdminMenu(player));
    if (hasLand && response.selection === index++) { try { player.addTag(BRIDGE_TAG_LAND_ADMIN); } catch {} return; }
    if (hasShop && response.selection === index++) { try { player.addTag(BRIDGE_TAG_SHOP_ADMIN); } catch {} return; }
    return system.run(() => showCompassHub(player));
  } catch (error) { console.warn(`[生存辅助] 打开管理员中心失败: ${error}`); }
}

'''
s = s[:hstart] + hub + s[hend:]

mark = '// Compass coordination:'
listener = '''system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    try {
      if (player.hasTag(BRIDGE_TAG_SELF_ADMIN)) {
        player.removeTag(BRIDGE_TAG_SELF_ADMIN);
        if (isAdmin(player)) system.run(() => showAdminMenu(player));
      } else if (player.hasTag(BRIDGE_TAG_SELF_MENU)) {
        player.removeTag(BRIDGE_TAG_SELF_MENU);
        system.run(() => showMainMenu(player));
      }
    } catch {}
  }
}, 2);

'''
s = s.replace(mark, listener + mark, 1)

p.write_text(s, encoding="utf-8")
print("Applied SurvivalHelper v2.8.0 upgrade patch")
