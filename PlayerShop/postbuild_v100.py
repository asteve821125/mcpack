from pathlib import Path

p = Path(__file__).resolve().parent / "scripts" / "main.js"
s = p.read_text(encoding="utf-8")

# Only accept oak sign blocks created next to the chest for shop creation.
s = s.replace(
    'const CHEST_ID = "minecraft:chest";\n',
    'const CHEST_ID = "minecraft:chest";\n'
    'const OAK_SIGN_BLOCK_IDS = new Set(["minecraft:standing_sign", "minecraft:wall_sign", "minecraft:oak_standing_sign", "minecraft:oak_wall_sign"]);\n',
    1,
)

old = 'function findAdjacentSign(chest){for(const b of adjacentBlocks(chest)){try{if(b.getComponent("minecraft:sign"))return b;}catch{}}return undefined;}\n'
new = '''function adjacentOakSignKeys(chest){
  const set=new Set();
  for(const b of adjacentBlocks(chest)){
    try{if(OAK_SIGN_BLOCK_IDS.has(b.typeId)&&b.getComponent("minecraft:sign"))set.add(locKey(b.dimension.id,b.location));}catch{}
  }
  return set;
}
function findNewAdjacentOakSign(chest,beforeKeys=new Set()){
  for(const b of adjacentBlocks(chest)){
    try{
      const key=locKey(b.dimension.id,b.location);
      if(!beforeKeys.has(key)&&OAK_SIGN_BLOCK_IDS.has(b.typeId)&&b.getComponent("minecraft:sign"))return b;
    }catch{}
  }
  return undefined;
}
'''
assert old in s, "adjacent sign helper not found"
s = s.replace(old, new, 1)

# Creation intent: remember existing signs so an old decoration sign cannot be hijacked.
start = s.index('function handleCreateIntent(player,chest){')
end = s.index('function rollbackCreationSign', start)
creation = '''function handleCreateIntent(player,chest){
  if(findShopByBlock(chest))return tell(player,"这个箱子已经是玩家商店。");
  if(shopsOf(player.name).length>=state.settings.defaultShopLimit)return tell(player,`你的商店数量已达到上限 ${state.settings.defaultShopLimit}。`);
  pendingSignCreates.set(player.id,{dimension:chest.dimension.id,chest:copyLoc(chest.location),beforeSigns:[...adjacentOakSignKeys(chest)],tick:system.currentTick});
  system.runTimeout(()=>finishCreateIntent(player),CREATE_SCAN_DELAY);
}
function finishCreateIntent(player){
  const pending=pendingSignCreates.get(player.id);pendingSignCreates.delete(player.id);
  if(!pending||!player?.isValid)return;
  let dim,chest;
  try{dim=world.getDimension(pending.dimension.replace("minecraft:",""));chest=dim.getBlock(pending.chest);}catch{}
  if(!chest||chest.typeId!==CHEST_ID)return;
  const sign=findNewAdjacentOakSign(chest,new Set(pending.beforeSigns??[]));
  if(!sign){tell(player,"创建商店需要把橡木告示牌实际放在箱子上或箱子侧面。");return;}
  const container=chest.getComponent("minecraft:inventory")?.container;
  if(!container||container.firstItem()===undefined){tell(player,"创建失败：请先在箱子里放入至少一种准备出售的商品。");return rollbackCreationSign(player,sign);}
  requestLandOwnership(player,chest.location,(allowed)=>{
    if(!allowed){tell(player,"创建失败：检测到 myLand 后，箱子商店只能创建在你自己的地皮内。");return rollbackCreationSign(player,sign);}
    system.run(()=>confirmCreateShop(player,chest,sign,0));
  });
}
'''
s = s[:start] + creation + s[end:]

# Retry creation confirmation while the vanilla sign editor is still occupying the player's UI.
start = s.index('async function confirmCreateShop(player,chest,sign)')
end = s.index('\n\nworld.afterEvents.worldLoad.subscribe', start)
confirm = '''async function confirmCreateShop(player,chest,sign,attempt=0){
  const chests=resolveChestBlocks(chest);
  for(const c of chests){const b=chest.dimension.getBlock(c);if(findShopByBlock(b))return tell(player,"创建失败：这个箱子或大箱子的另一半已经绑定商店。");}
  const count=(()=>{const c=chest.getComponent("minecraft:inventory")?.container;if(!c)return 0;const set=new Set();for(let i=0;i<c.size;i++){const item=c.getItem(i);if(item)set.add(itemFingerprint(item));}return set.size;})();
  const form=new MessageFormData().title("创建箱子商店").body(`将创建 ${chests.length>1?"大箱子":"单箱"} 商店。\\n检测到 ${count} 种商品。\\n\\n创建后会自动进入价格设置；告示牌显示“${player.name}”的商店。`).button1("取消").button2("确认创建");
  const r=await showForm(player,form,"创建确认");
  if(!r)return rollbackCreationSign(player,sign);
  if(r.canceled&&r.cancelationReason==="UserBusy"&&attempt<12){return system.runTimeout(()=>confirmCreateShop(player,chest,sign,attempt+1),10);}
  if(r.canceled||r.selection!==1)return rollbackCreationSign(player,sign);
  const id=nextShopId();
  const shop={id,owner:player.name,dimension:chest.dimension.id,chests,sign:copyLoc(sign.location),products:{},createdAt:Date.now()};
  state.shops.push(shop);state.nextId=nextShopId();
  for(const c of chests)markShopBlock(shop.dimension,c,true);markShopBlock(shop.dimension,shop.sign,true);
  writeShopSign(shop);saveData();tell(player,`商店 #${shop.id} 创建成功。现在设置商品价格。`);
  return showProductSettings(player,shop);
}'''
s = s[:start] + confirm + s[end:]

# A shop chest is not general storage: any currently stocked but unpriced item pauses sales until priced or removed.
start = s.index('async function showShopAtChest(player,shop){')
end = s.index('async function showBuyQuantity', start)
shop_ui = '''async function showShopAtChest(player,shop){
  if(sameName(player.name,shop.owner)){if(player.isSneaking)return showManageShop(player,shop);return;}
  if(isAdmin(player)&&player.isSneaking)return showManageShop(player,shop);
  const all=productRows(shop,true);
  const pending=all.filter(p=>p.present&&!(Number(p.price)>0));
  if(pending.length){tell(player,`该商店有 ${pending.length} 种箱内物品尚未定价，暂时停止营业。请联系店主设置价格或移除杂物。`);return;}
  const rows=all.filter(p=>Number(p.price)>0&&p.stock>0);
  const f=new ActionFormData().title(shopDisplayName(shop)).body(`你的余额：${formatMoney(getBalance(player.name,true))}\\n${rows.length?"选择商品购买。":"当前没有可购买商品。"}`);
  for(const p of rows)f.button(`${p.label}\\n库存 ${p.stock} · ${formatMoney(p.price)}/个`);
  f.button("关闭");
  const r=await showForm(player,f,"购买商店");if(!r||r.canceled)return;
  if(r.selection<rows.length)return showBuyQuantity(player,shop,rows[r.selection]);
}
'''
s = s[:start] + shop_ui + s[end:]

# Fix partial-stack purchasing and make the transaction fail-safe before item delivery.
start = s.index('function executePurchase(player,shop,fingerprint,qty){')
end = s.index('function recordTrade', start)
purchase = '''function executePurchase(player,shop,fingerprint,qty){
  shop=getShopById(shop.id);if(!shop)return tell(player,"商店已不存在。");
  const product=shop.products[fingerprint];if(!product||product.price<=0)return tell(player,"该商品已下架。");
  const container=shopContainer(shop);if(!container)return tell(player,"商店箱子当前未加载，请靠近后重试。");
  const matching=[];let stock=0;
  for(let i=0;i<container.size;i++){
    const item=container.getItem(i);if(!item||itemFingerprint(item)!==fingerprint)continue;
    matching.push({slot:i,item});stock+=item.amount;
  }
  if(stock<qty)return tell(player,`库存不足，当前仅剩 ${stock}。`);
  const total=product.price*qty;if(!Number.isSafeInteger(total)||total<1||total>2000000000)return tell(player,"交易金额无效或过大。");
  const buyerBefore=getBalance(player.name,true);if(buyerBefore<total)return tell(player,`余额不足，需要 ${formatMoney(total)}。`);
  const sellerBefore=getBalance(shop.owner,true);
  const tax=Math.floor(total*(state.settings.taxPercent/100));
  const sellerGain=total-tax;
  const slotBackup=[];const transfers=[];let remain=qty;
  try{
    for(const m of matching){
      if(remain<=0)break;
      const current=container.getItem(m.slot);if(!current||itemFingerprint(current)!==fingerprint)throw new Error("inventory changed");
      const originalAmount=current.amount;const take=Math.min(remain,originalAmount);
      slotBackup.push({slot:m.slot,item:current});
      const out=container.getItem(m.slot);out.amount=take;transfers.push(out);
      const left=originalAmount-take;
      if(left<=0)container.setItem(m.slot,undefined);
      else{const keep=container.getItem(m.slot);keep.amount=left;container.setItem(m.slot,keep);}
      remain-=take;
    }
    if(remain>0)throw new Error("inventory changed");
    if(!setBalance(player.name,buyerBefore-total))throw new Error("buyer balance write failed");
    if(!setBalance(shop.owner,Math.min(2000000000,sellerBefore+sellerGain))){setBalance(player.name,buyerBefore);throw new Error("seller balance write failed");}
  }catch(e){
    for(const b of slotBackup){try{container.setItem(b.slot,b.item);}catch{}}
    log("交易扣款/扣库存失败",e);tell(player,"交易失败，金币和库存已回滚。请重试。");return;
  }

  const inv=player.getComponent("minecraft:inventory")?.container;
  for(const stack of transfers){
    let leftover=stack;
    try{leftover=inv?.addItem(stack);}catch{}
    if(leftover){
      try{
        const entity=player.dimension.spawnItem(leftover,{x:player.location.x,y:player.location.y+0.5,z:player.location.z});
        try{entity.applyImpulse({x:(Math.random()-.5)*.18,y:.18,z:(Math.random()-.5)*.18});}catch{}
      }catch(e){log("/give 风格溢出物品发放失败",e);}
    }
  }
  product.lastStock=stock-qty;
  recordTrade({time:Date.now(),buyer:player.name,seller:shop.owner,shopId:shop.id,item:product.label,qty,total,tax});saveData();
  tell(player,`购买成功：${product.label} ×${qty}，支付 ${formatMoney(total)}。${product.lastStock===0?" §e该商品已售罄。§r":""}`);
  const seller=world.getAllPlayers().find(x=>sameName(x.name,shop.owner));if(seller)tell(seller,`${player.name} 购买了 ${product.label} ×${qty}，你获得 ${formatMoney(sellerGain)}。`);
}
'''
s = s[:start] + purchase + s[end:]

# If double-chest expansion is not exposed reliably by the runtime, refuse it and refund the chest.
s = s.replace(
    '    const combined=resolveChestBlocks(linked.other);\n    if(combined.length<2){return;}\n',
    '    const combined=resolveChestBlocks(linked.other);\n    if(combined.length<2){try{block.setType("minecraft:air");player.runCommand("give @s chest 1");}catch{}tell(player,"当前运行环境没有可靠识别到大箱子，已取消本次扩容并返还箱子。");return;}\n',
    1,
)

p.write_text(s, encoding="utf-8")
print("Applied PlayerShop v1.0.0 reliability patch")
