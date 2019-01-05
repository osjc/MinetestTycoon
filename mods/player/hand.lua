-- The player's hand
minetest.register_item(":", {
  type = "none",
  wield_image = "wieldhand.png",
  wield_scale = {x=1,y=1,z=2.5},
  tool_capabilities = {
    full_punch_interval = 1.0,
    max_drop_level = 0,
    groupcaps = {
      fleshy = {times={[2]=2.00, [3]=1.00}, uses=0, maxlevel=1},
      crumbly = {times={[2]=3.00, [3]=0.70}, uses=0, maxlevel=1},
      snappy = {times={[3]=0.40}, uses=0, maxlevel=1},
      oddly_breakable_by_hand = {
        times={[1]=7.00,[2]=4.00,[3]=1.40},
        uses=0,
        maxlevel=3
      },
    },
    damage_groups = {fleshy=1},
  }
})
