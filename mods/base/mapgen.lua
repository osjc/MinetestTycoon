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

local function PutToLog(Text)
  local file = openfile("mapgen.log","a")
  file:write(Text.."\n")
  file:close()
  LogLineNum=LogLineNum+1
end

local function PosToString(pos)
  return("["..pos.x..","..pos.y..","..pos.z.."]")
end

minetest.register_on_generated(function(minp, maxp)
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
  ReportedBlocks[Index]={Line=LogLineNum,Report=PosReport}
  print("Emerge: "..Index.." "..LastTime)
  PutToLog(Index..TimeReport..PosReport)
end)

local function LoadLog()
  util.IterateOverLines("mapgen.log", function(Line)
    local FirstChar=string.sub(Line,1,1)
    local FirstPos=string.find(Line," ")
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
    end
    LogLineNum=LogLineNum+1
  end)
end

LoadLog()
