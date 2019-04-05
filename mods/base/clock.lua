local ClockTime
local Divider

local GetGameTime = minetest.get_gametime
minetest.get_gametime = nil

local function RunClock()
  local Time = GetGameTime()
  local Seconds = math.floor(ClockTime/10)
  local SubSeconds = ClockTime - Seconds*10
  if Seconds<Time then
    Divider=1
  end
  if Divider then
    ClockTime = ClockTime + 1
    Divider = nil
  else
    Divider = 1
  end
  Restart(0.05,RunClock)
end

local function InitClock()
  local Time = GetGameTime()
  local Function = InitClock
  if Time ~= nil then
    ClockTime = Time*10
    Function=RunClock
  end
  Restart(0.05, Function)
end
InitClock()

function base.GetTime()
  return ClockTime
end

function base.After(Time,Procedure,...)
  Restart(Time,Procedure,unpack(arg))
end
