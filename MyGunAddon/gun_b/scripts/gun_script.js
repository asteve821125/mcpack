// 基岩版1.21.7 稳定版API脚本（无需Beta）
const gunSystem = server.registerSystem(0, 0);

gunSystem.initialize = function() {
  this.log("[GunSystem] 脚本初始化成功！");
  this.listenForEvent("minecraft:entity_use_item", (eventData) => this.onPlayerUseItem(eventData));
};

gunSystem.onPlayerUseItem = function(eventData) {
  const player = eventData.entity;
  const itemComponent = this.getComponent(player, "minecraft:hand_container");
  const itemStack = itemComponent.item;
  if (itemStack && itemStack.item === "dear:gun" && eventData.use_method === "right_click") {
    this.log("[GunSystem] 检测到枪械右键点击");
    this.shootBullet(player);
  }
};

gunSystem.shootBullet = function(player) {
  const position = this.getComponent(player, "minecraft:position");
  const rotation = this.getComponent(player, "minecraft:rotation");
  const direction = this.calculateDirection(rotation.x, rotation.y);
  const bullet = this.createEntity("dear:bullet");
  this.applyComponentChanges(bullet, {
    "minecraft:position": {x:position.x,y:position.y + 1.5,z:position.z},
    "minecraft:projectile": {direction:direction,power:3.0}
  });
  this.log("[GunSystem] 子弹实体已生成：" + bullet.__identifier__);
};

gunSystem.calculateDirection = function(pitch, yaw) {
  const radianPitch = pitch * (Math.PI / 180);
  const radianYaw = yaw * (Math.PI / 180);
  return {x:-Math.sin(radianYaw)*Math.cos(radianPitch),y:-Math.sin(radianPitch),z:Math.cos(radianYaw)*Math.cos(radianPitch)};
};

gunSystem.log = function(message) {
  const chatData = this.createEventData("minecraft:display_chat_event");
  chatData.message = message;
  this.broadcastEvent("minecraft:display_chat_event", chatData);
};