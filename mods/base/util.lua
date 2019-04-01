util={}

function util.IterateOverLines(FileName, Function)
  local File = openfile(FileName)
  if not File then
    return
  end
  while true do
    local Lines,Rest = File:read(8192, "*line")
    if not Lines then
      break
    end
    if Rest then
      Lines=Lines..Rest.."\n"
    end
    local Pos=0
    while true do
      local EndPos=string.find(Lines,"\n",Pos)
      if not EndPos then
        break
      end
      local Line=string.sub(Lines, Pos, EndPos-1)
      Function(Line)
      Pos=EndPos+1
    end
  end
end
