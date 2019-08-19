local SinglePlayer

minetest.register_on_joinplayer(function(player)
  local Superblock,Loading=mds.GetSuperblock()
  if Loading then
    base.TeleportToLobby(player)
  end
  if config.RecordMapgen then
    local name = player:get_player_name()
    if name == "singleplayer" then
      SinglePlayer=player
      clock.RegisterPeriodicProc("Recorder", base.RecordPlayerPosition, player)
    end
  end
end)

minetest.register_on_leaveplayer(function(player)
  if config.RecordMapgen then
    local name = player:get_player_name()
    if name == "singleplayer" then
      SinglePlayer=nil
      clock.UnregisterPeriodicProc("Recorder")
    end
  end
end)
