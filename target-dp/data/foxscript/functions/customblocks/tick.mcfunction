execute as @e[type=minecraft:item_frame,tag=customblocks.luckyblock] run function foxscript:customblocks/luckyblock/place
execute as @e[type=minecraft:armor_stand,tag=customblocks.luckyblock] at @s unless block ~ ~ ~ minecraft:glass run function foxscript:customblocks/luckyblock/destroy
execute as @e[type=minecraft:item_frame,tag=customblocks.uranium_ore] run function foxscript:customblocks/uranium_ore/place
execute as @e[type=minecraft:armor_stand,tag=customblocks.uranium_ore] at @s unless block ~ ~ ~ minecraft:glass run function foxscript:customblocks/uranium_ore/destroy
