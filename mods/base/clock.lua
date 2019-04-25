clock = {}

local ClockTime
local Divider

local GetGameTime = minetest.get_gametime
minetest.get_gametime = nil
local Restart = minetest.after
minetest.after = nil

local Periodic = {}

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
    for _,Record in pairs(Periodic) do
      Record.Proc(unpack(Record.Arg))
    end
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

function clock.GetTime()
  return ClockTime
end

function clock.RegisterPeriodicProc(Name,Procedure,...)
  Periodic[Name]={Proc=Procedure,Arg=arg}
end

function clock.UnregisterPeriodicProc(Name)
  Periodic[Name]=nil
end

if config.DebugClock then
  local Key = {}
  clock.RegisterPeriodicProc(Key, function()
    local Time = GetGameTime()
    Seconds = math.floor(ClockTime/10)
    SubSeconds = ClockTime - Seconds*10
    local timestr = string.format("%d.%d",Seconds,SubSeconds)
    print(timestr.." "..tostring(Time))
  end)
end
