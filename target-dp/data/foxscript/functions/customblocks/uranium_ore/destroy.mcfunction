execute if entity @p[gamemode=survival] run summon item ~ ~0.5 ~ {Item:{id:"minecraft:item_frame",Count:1b,tag:{EntityTag:{Tags:["customblocks","customblocks.uranium_ore"],Invisible:1b},CustomModelData:2,display:{Name:"{\"text\":\"Uranium Ore\",\"italic\":\"false\"}"}}},Motion:[0.0d,0.2d,0.0d],PickupDelay:10}
execute if entity @p[gamemode=survival] run kill @e[type=item,distance=..1,limit=1,sort=nearest,nbt={Item:{id:"minecraft:glass"}}]
kill @s
effect give @p[gamemode=survival] minecraft:nausea 15 50 true