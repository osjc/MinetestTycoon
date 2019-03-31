minetest.register_on_joinplayer(function(player)
  local Superblock,Loading=mds.GetSuperblock()
  if Loading then
    base.TeleportToLobby(player)
  end
end)
