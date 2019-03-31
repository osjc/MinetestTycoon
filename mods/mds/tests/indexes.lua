
local file

local function PrintCore(What)
  file:write(What)
end

local Space=""

local function Print(What)
  PrintCore(Space)
  PrintCore(What)
end

local function PrintPos(Pos)
  Print("(x="..Pos.x..",y="..Pos.y..",z="..Pos.z..")")
  Space=" "
end

local function PrintLn(what)
  PrintCore("\n")
  Space=""
end

local function TestPos(x, y, z)
  pos = {x=x, y=y, z=z}
  PrintPos(pos)
  Print("=")
  index = inode.CalculateIndex(pos)
  Print(index)
  new = inode.PositionFromIndex(index)
  if new.x~=x or new.y~=y or new.z~=z then
    Print("->")
    PrintPos(new)
  end
  PrintLn()
end

local function TestIt()
  file = openfile("indexes.txt", "w")
  TestPos(-30912,-30912,-30912)
  TestPos(-30911,-30912,-30912)
  TestPos(-30912,-30911,-30912)
  TestPos(-30912,-30912,-30911)
  TestPos(-30912+79,-30912+79,-30912+79)
  TestPos(-30912+80,-30912,-30912)
  TestPos(-30912+81,-30912,-30912)
  TestPos(30927,-30912+79,-30912+79)
  TestPos(-30912,-30912,-30912+80)
  TestPos(-30912+1,-30912,-30912+80)
  TestPos(30927,-30912+79,30927)
  TestPos(-30912,-30912+80,-30912)
  TestPos(-30912+1,-30912+80,-30912)
  TestPos(-30912+79,-30912+80+79,-30912+79)
  TestPos(-30912+80,-30912+80,-30912)
  TestPos(-30912+81,-30912+80,-30912)
  TestPos(30927,-30912+80+79,30927)
  TestPos(-30912,-30912+80+80,-30912)
  TestPos(-30912+1,-30912+80+80,-30912)
  TestPos(30927,-30912+80*3-1,30927)
  TestPos(-30912,-30912+80*3,-30912)
  TestPos(-30912+1,-30912+80*3,-30912)
  file:close()
end

TestIt()
