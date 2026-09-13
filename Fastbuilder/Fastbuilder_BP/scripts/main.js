import { system, world } from "@minecraft/server"
let reconfirm = false
let blockLocation1 = { x: 0, y: 0, z: 0 }
let blockLocation2 = { x: 0, y: 0, z: 0 }
let blockAmount = {}
let blockList = {}
let blockUid = 1//air = 0
let blocks
let dx
let dy
let dz

world.beforeEvents.playerBreakBlock.subscribe((e) => {
    let player = e.player
    let block = player.getBlockFromViewDirection().block
    let item = e.itemStack
    if (item?.typeId !== `minecraft:diamond_pickaxe`)
        return
    e.cancel = true
    player.sendMessage(block.location.x + " " + block.location.y + " " + block.location.z)
    if (reconfirm) {
        blockLocation2 = block.location
        let minX = Math.min(blockLocation1.x, blockLocation2.x)
        let maxX = Math.max(blockLocation1.x, blockLocation2.x)
        let minY = Math.min(blockLocation1.y, blockLocation2.y)
        let maxY = Math.max(blockLocation1.y, blockLocation2.y)
        let minZ = Math.min(blockLocation1.z, blockLocation2.z)
        let maxZ = Math.max(blockLocation1.z, blockLocation2.z)
        dx = maxX - minX + 1
        dy = maxY - minY + 1
        dz = maxZ - minZ + 1
        blocks = new Array(dx * dy * dz).fill(0)
        for (let x = minX; x <= maxX; ++x)
            for (let y = minY; y <= maxY; ++y)
                for (let z = minZ; z <= maxZ; ++z) {
                    let block = e.dimension.getBlock({ x: x, y: y, z: z })
                    if (block.typeId === `minecraft:air`)
                        continue
                    if (blockAmount[block.typeId] === undefined)
                        blockAmount[block.typeId] = 0
                    blockAmount[block.typeId] += 1
                    if (blockList[block.typeId] === undefined)
                        blockList[block.typeId] = blockUid++
                    let index = (x - minX) * dy * dz + (y - minY) * dz + (z - minZ)
                    blocks[index] = blockList[block.typeId]
                }
        let message = `\n`
        for (let key in blockAmount)
            message += `${key}: ${blockAmount[key]}\n`
        reconfirm = false
        console.log(`所需数量` + message)
        console.log(`方块列表` + JSON.stringify(blockList))
        console.log(`dx: ` + dx + ` dy: ` + dy + ` dz: ` + dz)
        console.log(`方块数组` + JSON.stringify(blocks))
        player.sendMessage(`方块信息记录完毕，请在控制台查看`)
        blockLocation1 = { x: 0, y: 0, z: 0 }
        blockLocation2 = { x: 0, y: 0, z: 0 }
        blockAmount = {}
        blockList = {}
        blockUid = 1
        blocks = []
        dx = 0
        dy = 0
        dz = 0
        return
    }
    if (reconfirm === false) {
        reconfirm = true
        blockLocation1 = block.location
        player.sendMessage("Break other blocks to confirm")
    }
    blockLocation1 = block.location
})