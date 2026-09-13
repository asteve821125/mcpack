from pathlib import Path

p = Path(__file__).resolve().parent / "scripts" / "main.js"
s = p.read_text(encoding="utf-8")

s = s.replace('const VERSION = "4.1.2";', 'const VERSION = "4.2.0";')
s = s.replace('const BRIDGE_OTHER = "survival";\n', 'const BRIDGE_PEERS = ["survival", "shop"];\n')
s = s.replace(
    'const BRIDGE_TAG_ADMIN = "bridge:myland_admin";\n',
    'const BRIDGE_TAG_ADMIN = "bridge:myland_admin";\n'
    'const BRIDGE_TAG_SHOP_MENU = "bridge:playershop_menu";\n'
    'const BRIDGE_TAG_SHOP_ADMIN = "bridge:playershop_admin";\n'
    'const ECONOMY_OBJECTIVE = "server_money";\n'
    'const ECONOMY_META_OBJECTIVE = "server_economy_meta";\n'
    'const SHOP_BLOCK_OBJECTIVE = "playershop_blocks";\n'
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

start = s.index('function ensureEconomy() {')
end = s.index('function formatMoney(value)', start)
econ = '''function getEconomyObjective() {
  try { return world.scoreboard.getObjective(ECONOMY_OBJECTIVE) ?? world.scoreboard.addObjective(ECONOMY_OBJECTIVE, "服务器金币"); }
  catch { return undefined; }
}
function getEconomyMetaObjective() {
  try { return world.scoreboard.getObjective(ECONOMY_META_OBJECTIVE) ?? world.scoreboard.addObjective(ECONOMY_META_OBJECTIVE, "公共经济元数据"); }
  catch { return undefined; }
}
function economyParticipant(name) { return `u:${playerKey(name)}`; }
function ensureEconomy() {
  if (!state.economy || typeof state.economy !== "object") state.economy = { balances: {} };
  if (!state.economy.balances || typeof state.economy.balances !== "object") state.economy.balances = {};
  getEconomyObjective();
}
function migrateLegacyEconomyOnce() {
  ensureEconomy();
  const money = getEconomyObjective();
  const meta = getEconomyMetaObjective();
  if (!money || !meta) return;
  try {
    if ((meta.getScore("myland_v1_migrated") ?? 0) > 0) return;
    for (const [name, raw] of Object.entries(state.economy.balances ?? {})) {
      const value = Math.max(0, Math.min(2000000000, Math.floor(Number(raw) || 0)));
      const key = economyParticipant(name);
      if (money.getScore(key) === undefined) money.setScore(key, value);
    }
    meta.setScore("myland_v1_migrated", 1);
    console.warn(`[myLand] 已将旧版地皮余额迁移到共享经济 ${ECONOMY_OBJECTIVE}`);
  } catch (e) { logError("共享经济迁移失败", e); }
}
function getBalanceByName(name, initialize = true) {
  ensureEconomy();
  const obj = getEconomyObjective();
  if (!obj) return START_BALANCE;
  const key = economyParticipant(name);
  try {
    let value = obj.getScore(key);
    if (value === undefined && initialize) { obj.setScore(key, START_BALANCE); value = START_BALANCE; }
    return Math.max(0, Math.floor(Number(value) || 0));
  } catch { return START_BALANCE; }
}
function setBalanceByName(name, value) {
  ensureEconomy();
  const obj = getEconomyObjective();
  if (!obj) return;
  obj.setScore(economyParticipant(name), Math.max(0, Math.min(2000000000, Math.floor(Number(value) || 0))));
}
function addBalanceByName(name, delta) {
  const next = Math.max(0, Math.min(2000000000, getBalanceByName(name, true) + Math.floor(Number(delta) || 0)));
  setBalanceByName(name, next);
  return next;
}
'''
s = s[:start] + econ + s[end:]

s = s.replace(
    'loadData();\n  console.warn(`[myLand] v${VERSION} 已加载',
    'loadData();\n  migrateLegacyEconomyOnce();\n  console.warn(`[myLand] v${VERSION} 已加载',
    1,
)

marker = 'function interactionFlag(typeId) {'
helper = '''function shopBlockKey(block) {
  const dim = block?.dimension?.id === "minecraft:nether" ? "n" : block?.dimension?.id === "minecraft:the_end" ? "e" : "o";
  const l = block?.location;
  return l ? `${dim}:${Math.floor(l.x)}:${Math.floor(l.y)}:${Math.floor(l.z)}` : "";
}
function isShopManagedBlock(block) {
  try {
    const obj = world.scoreboard.getObjective(SHOP_BLOCK_OBJECTIVE);
    const key = shopBlockKey(block);
    return !!obj && !!key && (obj.getScore(key) ?? 0) > 0;
  } catch { return false; }
}

'''
s = s.replace(marker, helper + marker, 1)

hstart = s.index('async function showCompassHub(player) {')
hend = s.index('async function showMainMenu(player) {', hstart)
hub = '''async function showCompassHub(player) {
  if (!player?.isValid) return;
  try {
    const hasSurvival = bridgeAlive("survival");
    const hasShop = bridgeAlive("shop");
    const enabled = ["地皮系统", ...(hasSurvival ? ["生存辅助"] : []), ...(hasShop ? ["玩家商店"] : [])].join("、");
    const form = new ActionFormData().title("§l服务器辅助").body(`当前已启用：${enabled}。\n\n请选择要进入的系统。`)
      .button("§e地皮系统\n§7地皮、经济、公开大厅等");
    if (hasSurvival) form.button("§a生存辅助\n§7采集、传送、玩家互助等");
    if (hasShop) form.button("§b玩家商店\n§7箱子商店、市场搜索、交易管理");
    const admin = isAdmin(player);
    if (admin) form.button("§6管理员中心\n§7管理已启用的插件");
    const response = await form.show(player);
    if (response.canceled) return;
    let index = 0;
    if (response.selection === index++) return system.run(() => showMainMenu(player));
    if (hasSurvival && response.selection === index++) { try { player.addTag("bridge:survival_menu"); } catch {} return; }
    if (hasShop && response.selection === index++) { try { player.addTag(BRIDGE_TAG_SHOP_MENU); } catch {} return; }
    if (admin && response.selection === index) return system.run(() => showCompassAdminHub(player));
  } catch (error) { logError("打开指南针总菜单失败", error); }
}

async function showCompassAdminHub(player) {
  if (!player?.isValid || !isAdmin(player)) return;
  try {
    const hasSurvival = bridgeAlive("survival");
    const hasShop = bridgeAlive("shop");
    const form = new ActionFormData().title("§l管理员中心").body("管理当前已启用的插件")
      .button("§e地皮系统管理\n§7地皮、经济、备份与修复");
    if (hasSurvival) form.button("§a生存辅助管理\n§7全服设置与玩家权限");
    if (hasShop) form.button("§b玩家商店管理\n§7商店、交易与经济设置");
    form.button("返回总菜单");
    const response = await form.show(player);
    if (response.canceled) return;
    let index = 0;
    if (response.selection === index++) return system.run(() => showAdminMenu(player));
    if (hasSurvival && response.selection === index++) { try { player.addTag("bridge:survival_admin"); } catch {} return; }
    if (hasShop && response.selection === index++) { try { player.addTag(BRIDGE_TAG_SHOP_ADMIN); } catch {} return; }
    return system.run(() => showCompassHub(player));
  } catch (error) { logError("打开管理员中心失败", error); }
}

'''
s = s[:hstart] + hub + s[hend:]
s = s.replace('if (bridgeAlive(BRIDGE_OTHER)) return;', 'if (bridgeAlive("survival") || bridgeAlive("shop")) return;')

s = s.replace(
    '  const land = getLandAt(event.block.location, event.player.dimension.id);\n  if (!land) return;',
    '  if (isShopManagedBlock(event.block)) return;\n  const land = getLandAt(event.block.location, event.player.dimension.id);\n  if (!land) return;',
    1,
)
s = s.replace(
    'world.beforeEvents.playerBreakBlock.subscribe((event) => {\n  if (!loaded) return;\n  const land = getLandAt(event.block.location, event.dimension.id);',
    'world.beforeEvents.playerBreakBlock.subscribe((event) => {\n  if (!loaded) return;\n  if (isShopManagedBlock(event.block)) return;\n  const land = getLandAt(event.block.location, event.dimension.id);',
)

needle = '''      if (player.hasTag(BRIDGE_TAG_MENU)) {
        player.removeTag(BRIDGE_TAG_MENU);
        system.run(() => { void showMainMenu(player); });
      }'''
replacement = needle + '''
      for (const tag of player.getTags()) {
        if (!tag.startsWith("shop:landcheck:")) continue;
        player.removeTag(tag);
        const [, , dimCode, xs, ys, zs] = tag.split(":");
        const dimId = dimCode === "n" ? "minecraft:nether" : dimCode === "e" ? "minecraft:the_end" : "minecraft:overworld";
        const location = { x: Number(xs), y: Number(ys), z: Number(zs) };
        const land = getLandAt(location, dimId);
        player.removeTag("shop:landok"); player.removeTag("shop:landdeny");
        player.addTag(land && isOwner(player, land) ? "shop:landok" : "shop:landdeny");
      }'''
assert needle in s
s = s.replace(needle, replacement, 1)

p.write_text(s, encoding="utf-8")
print("Applied myLand v4.2.0 upgrade patch")
