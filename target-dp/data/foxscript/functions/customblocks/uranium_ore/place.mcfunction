execute at @s align xyz run summon armor_stand ~0.5 ~ ~0.5 {Marker:1b,Invisible:1b,Pose:{Head:[0f,180f,0f]},Tags:["customblocks","customblocks.uranium_ore"],ArmorItems:[{},{},{},{id:"minecraft:item_frame",Count:1b,tag:{CustomModelData:2}}]}
execute at @s run setblock ~ ~ ~ minecraft:glass
execute at @s align xyz run playsound minecraft:block.stone.break block @a[distance=..16]
kill @s
