mapgen={}

local function PackChunkIndex(pos, cy, cz)
  local cx
  if cy == nil then
    local d = inode.DissectPosition(pos)
    cx = d.cx
    cy = d.cy
    cz = d.cz
  end
  local ChunkIndex = cx*1048576+cy*1024+cz
  return ChunkIndex
end

LastTime=0

local function GetTimeReport()
  local TimeReport=""
  local CurrentTime = clock.GetTime()
  if CurrentTime>LastTime then
    TimeReport=" T"..(CurrentTime-LastTime-1)
    LastTime=CurrentTime
  end
  return TimeReport
end

LogLineNum=1
ReportedBlocks={}
PlayerPos=nil

local function PutToLog(Text)
  local file = openfile("mapgen.log","a")
  file:write(Text.."\n")
  file:close()
  LogLineNum=LogLineNum+1
end

function base.RecordPlayerPosition(player)
  if PlayerPos==nil then
    return
  end
  local Pos = player:get_pos()
  local Index = PackChunkIndex(Pos)
  if Index == PlayerPos then
    return
  end
  local Code = 0
  local Found
  for x=-1,1 do
    for y=-1,1 do
      for z=-1,1 do
        if x~=0 or y~=0 or z~=0 then
          local NewIndex=PlayerPos + x*1048576 + y*1024 + z
          if NewIndex==Index then
            Found=Code
          end
          Code=Code+1
        end
      end
    end
  end
  local Report
  if Found == nil then
    Report="Pa"..Index
  else
    Report="P"..Found
  end
  local TimeReport=GetTimeReport()
  PutToLog(Report..TimeReport)
  PlayerPos=Index
  print("PlayerPos: "..Index.." "..LastTime)
end

local function PosToString(pos)
  return("["..pos.x..","..pos.y..","..pos.z.."]")
end

local function GenerateAndRecord(minp, maxp)
  if bedrock.Generate(minp, maxp) then
    return
  end
  local Index=PackChunkIndex(minp)
  local MinpStr = PosToString(minp)
  local MaxpStr = PosToString(maxp)
  local PosReport = " "..MinpStr.." "..MaxpStr
  local Previous=ReportedBlocks[Index]
  local TimeReport=GetTimeReport()
  if Previous then
    local Msg="Duplicated emerge: "..Index
    print(Msg.." first seen at line "..Previous.Line)
    local Report=":"..(LogLineNum-1-Previous.Line)..TimeReport
    if Previous.Report~=PosReport then
      Report=Report..PosReport
    end
    PutToLog(Report)
    return
  end
  if PlayerPos==nil then
    PlayerPos=Index
    print("PlayerPos: "..Index)
  end
  ReportedBlocks[Index]={Line=LogLineNum,Report=PosReport}
  print("Emerge: "..Index.." "..LastTime)
  PutToLog(Index..TimeReport..PosReport)
end

local function LoadLog()
  local Deltas={}
  local Code=0
  for x=-1,1 do
    for y=-1,1 do
      for z=-1,1 do
        if x~=0 or y~=0 or z~=0 then
          Deltas[Code]=x*1048576 + y*1024 + z
          Code=Code+1
        end
      end
    end
  end
  util.IterateOverLines("mapgen.log", function(Line)
    local FirstChar=string.sub(Line,1,1)
    local FirstPos=string.find(Line," ") or string.len(Line)
    local IndexEnd=FirstPos-1
    local PosReport=nil
    while true do
      local StartPos=FirstPos+1
      local NextItem=string.sub(Line,StartPos,StartPos)
      if NextItem=="[" then
        PosReport=string.sub(Line,FirstPos,-1)
        break
      end
      FirstPos=string.find(Line," ",StartPos)
      if NextItem=="T" then
        local EndPos=FirstPos
        if EndPos==nil then
          EndPos=-1
        else
          EndPos=EndPos-1
        end
        StartPos=StartPos+1
        local TimeDeltaStr=string.sub(Line,StartPos,EndPos)
        local TimeDelta=tonumber(TimeDeltaStr)+1
        LastTime=LastTime+TimeDelta
      end
      if FirstPos==nil then
        break
      end
    end
    if FirstChar>="0" and FirstChar<="9" and FirstPos ~= nil then
      local IndexStr=string.sub(Line, 1, IndexEnd)
      local Index=tonumber(IndexStr)
      ReportedBlocks[Index]={Line=LogLineNum,Report=PosReport}
      if PlayerPos==nil then
        PlayerPos=Index
      end
    elseif FirstChar=="P" then
      local CodeType=string.sub(Line, 2, 2)
      if CodeType=="a" then
        local PlayerPosStr=string.sub(Line,3,IndexEnd)
        PlayerPos=tonumber(PlayerPosStr)
      else
        local CodeStr=string.sub(Line,2,IndexEnd)
        local Code=tonumber(CodeStr)
        local Delta=Deltas[Code]
        PlayerPos=PlayerPos+Delta
      end
    end
    LogLineNum=LogLineNum+1
  end)
end

if config.RecordMapgen then
  LoadLog()
  minetest.register_on_generated(GenerateAndRecord)
else
  minetest.register_on_generated(bedrock.Generate)
end
