-- Polluted stone. The polution makes it look ugly.

minetest.register_node("polluted:stone", {
  description = "Polluted stone",
  tiles ={"polluted_stone.png"},
  groups = {cracky=3},
  drop = 'polluted:cobble',
})

minetest.register_node("polluted:cobble", {
  description = "Polluted cobble",
  tiles ={"polluted_cobble.png"},
  is_ground_content = false,
  groups = {cracky=3},
})
