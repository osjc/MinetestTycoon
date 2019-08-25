clock = {}

local ClockTime
local Divider = 0

local LastTime
local TickCount = 30
local TickCounts={30, 30, 30, 30, 30}
local TickCountIndex = 1
local TickCountsTotal = 30*5
local TickSize

local GetGameTime = minetest.get_gametime
local Restart = minetest.after

local Periodic = {}

local function RunClock()
  local Time = GetGameTime()
  if LastTime ~= Time then
    LastTime=Time
    TickCountsTotal=TickCountsTotal+TickCount-TickCounts[TickCountIndex]
    TickCounts[TickCountIndex]=TickCount
    if TickCountIndex==5 then
      TickCountIndex = 1
    else
      TickCountIndex = TickCountIndex + 1
    end
    TickCount=1
    TickSize = 50000/TickCountsTotal
  else
    TickCount = TickCount + 1
  end
  Divider = Divider + TickSize
  if Divider>1000 then
    ClockTime = ClockTime + 1
    for _,Record in pairs(Periodic) do
      Record.Proc(Record.Arg)
    end
    Divider = Divider - 1000
  end
  Restart(0.01,RunClock)
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

function clock.RegisterPeriodicProc(Name,Procedure,Argument)
  Periodic[Name]={Proc=Procedure,Arg=Argument}
end

function clock.UnregisterPeriodicProc(Name)
  Periodic[Name]=nil
end

if config.DebugClock then
  local Key = {}
  local OldRunClock=RunClock
  RunClock = function()
    OldRunClock()
    print("T: "..tostring(TickCountsTotal).." "..tostring(Divider))
  end
  clock.RegisterPeriodicProc(Key, function()
    local Time = GetGameTime()
    Seconds = math.floor(ClockTime/10)
    SubSeconds = ClockTime - Seconds*10
    local timestr = string.format("%d.%d",Seconds,SubSeconds)
    print("C: "..timestr.." "..tostring(Time).." "..tostring(Divider))
  end)
end
