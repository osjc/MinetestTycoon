def Write(Line):
  OutFile.write(Line)

def NewLine():
  Write("\n")

def WriteLn(Line):
  Write(Line)
  NewLine()

def DecodeIntraBlockPosition(Position):
  Z=Position/256
  Position%=256
  Y=Position/16
  X=Position%16
  return X,Y,Z

def EmitInventorySet(Set):
  for Item in Set:
    Write("Inventory: "+repr(Item.Name))
    if Item.Width!=0:
      Write(" width"+str(Item.Width))
    NewLine()
    EmptyCount=0
    for Stack in Item.Stacks:
      if Stack is None:
        EmptyCount+=1
      else:
        if EmptyCount>0:
          Write("E")
          if EmptyCount>1:
            Write(" "+str(EmptyCount))
          NewLine()
          EmptyCount=0
        if Stack.Size>1:
          Write("S "+str(Stack.Size)+" ")
        else:
          Write("I ")
        Write(repr(Stack.Name))
        if Stack.Wear>0:
          Write(" "+str(Stack.Wear))
        if Stack.Meta is not None:
          Write(" "+repr(Stack.Meta))
        NewLine()

def EmitPosition(Position, ShowValue):
  if ShowValue:
    Write(str(Position)+" (")
  Vect=DecodeIntraBlockPosition(Position)
  Write("L%02d%02d%02d"%Vect)
  if ShowValue:
    Write(")")

def EmitMetaData(Block, EmitVolatileData):
  for Item in Block.Meta:
    NewLine()
    Write("Metadata: ")
    EmitPosition(Item.Position, EmitVolatileData)
    NewLine()
    if Item.TypeId is not None:
      WriteLn("TypeID: "+str(Item.TypeID))
      WriteLn("Content: "+ToHex(Item.Content))
    else:
      for Name,Value in Item.Variables:
        WriteLn("Variable: "+Name+" "+repr(Value))
      EmitInventorySet(Item.InventorySet)

def EmitFlags(Flags, Name, Description):
  FlagList=[]
  for Mask,Flag in Description:
    if Flags&Mask:
      FlagList.append(Flag)
      Flags-=Mask
  if Flags>0:
    FlagList.append("Unknown("+"%X"%Flags+")")
  if len(FlagList)>0:
    WriteLn(Name+": "+" ".join(FlagList))

def EmitBlockInfo(Block, EmitVolatileData):
  if EmitVolatileData:
    WriteLn("Version: "+str(Block.Version))
    WriteLn("TimeStamp: "+str(Block.TimeStamp))
  EmitFlags(Block.Flags, "Flags", [
    (0x01,"IsUnderground"),
    (0x02,"DayNightDiffers"),
    (0x04,"LightingExpired"),
    (0x08,"Ungenerated"),
  ])
  if Block.LightingFlags is not None:
    Flags=0xFFFF-Block.LightingFlags
    EmitFlags(Flags, "LightingIncomplete", [
      (0x0001,"DayEast"),
      (0x0002,"DayTop"),
      (0x0004,"DayNorth"),
      (0x0008,"DayWest"),
      (0x0010,"DayBottom"),
      (0x0020,"DaySouth"),
      (0x0040,"NightEast"),
      (0x0080,"NightTop"),
      (0x0100,"NightNorth"),
      (0x0200,"NightWest"),
      (0x0400,"NightBottom"),
      (0x0800,"NightSouth"),
    ])
    if EmitVolatileData:
      for Ident,Name in Block.NameList:
        WriteLn("M "+str(Ident)+" "+repr(Name))

def EmitObjects(Block, EmitVolatileData):
  EmitDelimiter=False
  for Object in Block.Objects:
    if EmitDelimiter:
      NewLine()
      EmitDelimiter=False
    Type=Object.Type
    if Type==7:
      Write("LuaEntity:")
    else:
      TypeText=str(Type)
      Write("Object: "+str(Type))
    Write(" ("+str(Object.PosX)+","+str(Object.PosY)+","+str(Object.PosZ)+")")
    if Type==7:
      NewLine()
      WriteLn("Name: "+repr(Object.Name))
      Write("Velocity: ("+str(Object.VelocityX)+",")
      WriteLn(str(Object.VelocityY)+","+str(Object.VelocityZ)+")")
      WriteLn("Yaw: "+str(Object.Yaw))
      WriteLn("Health: "+str(Object.Health))
      WriteLn("Data: "+repr(Object.Data))
      EmitDelimiter=True
    else:
      WriteLn(" "+ToHex(Object.Data))

def EmitTimers(Block, EmitVolatileData):
  for Timer in Block.Timers:
    Write("Timer: ")
    EmitPosition(Timer.Position, EmitVolatileData)
    WriteLn(" "+str(Timer.Timeout)+" "+str(Timer.Elapsed))

def EmitBlockData(Block):
  NameMap=Block.NameMap
  Map=Block.Map
  for Y,Plane in Map:
    for X,Row in Plane:
      for Z,(Param0,Param1,Param2) in Row:
        Write("L%02d%02d%02d: "%(X,Y,Z))
        if Param0 not in NameMap:
          Malformed("Unknown node ID: "+str(Param0))
        Write(repr(NameMap[Param0]))
        if Param1!=0 or Param2!=0:
          Write(" ")
        if Param1!=0:
          Write(str(Param1))
        if Param2!=0:
          Write(","+str(Param2))
        NewLine()

def EmitBlock(OutF,Block,Volatile):
  global OutFile
  OutFile=OutF
  try:
    EmitBlockInfo(Block, Volatile)
    NewLine()
    EmitBlockData(Block)
    EmitMetaData(Block,Volatile)
    if len(Block.Objects)>0:
      NewLine()
      EmitObjects(Block, Volatile)
    if len(Block.Timers)>0:
      NewLine()
      EmitTimers(Block, Volatile)
  finally:
    OutFile=None
