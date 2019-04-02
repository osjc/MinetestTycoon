def UnsignedToSigned(Value, MaxPositive):
  if Value < MaxPositive:
    return Value
  else:
    return Value - 2*MaxPositive

def DecodePosition(Position):
  X = UnsignedToSigned(Position % 4096, 2048)
  Position = (Position-X) / 4096
  Y = UnsignedToSigned(Position % 4096, 2048)
  Position = (Position-Y) / 4096
  Z = UnsignedToSigned(Position % 4096, 2048)
  return X+2048,Y+2048,Z+2048

class TStack(object):
  def __init__(s):
    s.Name=None
    s.Wear=None
    s.Size=None
    s.Meta=None

class TInventory(object):
  def __init__(s):
    s.Name=None
    s.Width=None
    s.Stacks=None

class TMetaDataItem(object):
  def __init__(s):
    s.Position=None
    s.TypeId=None
    s.Content=None
    s.Variables=None
    s.InventorySet=None

class TObject(object):
  def __init__(s):
    s.Type=None
    s.PosX=None
    s.PosY=None
    s.PosZ=None
    s.Data=None
    # LuaEntity
    s.Name=None
    s.Health=None
    s.VelocityX=None
    s.VelocityY=None
    s.VelocityZ=None
    s.Yaw=None

class TTimer(object):
  def __init__(s):
    s.Position=None
    s.Timeout=None
    s.Elapsed=None

class TBlockInfo(object):
  def __init__(s):
    s.Version=None
    s.TimeStamp=None
    s.Flags=None
    s.LightingFlags=None
    s.NameList=None
    s.NameMap=None
    s.Map=None
    s.Meta=None
    s.Objects=None
    s.Timers=None

def ToHex(Data):
  import binascii
  return binascii.hexlify(Data).upper()

def Malformed(Msg):
  raise RuntimeError(Msg)

def Read(Count):
  return InFile.read(Count)

def ReadAndCheck(Name, Size):
  Data=Read(Size)
  if len(Data)==Size:
    return Data
  elif len(Data)==0:
    Msg="missing"
  else:
    Msg="corrupted"
  Malformed(Name+" is "+Msg)

def ReadU8(Name):
  Data=ReadAndCheck(Name, 1)
  return ord(Data)

def DecodeU16(Data):
  return 256*ord(Data[0])+ord(Data[1])

def ReadU16(Name):
  Data=ReadAndCheck(Name, 2)
  return DecodeU16(Data)

def ReadU32(Name):
  Data=ReadAndCheck(Name, 4)
  return 65536*DecodeU16(Data[:2])+DecodeU16(Data[2:])

def ReadS32(Name):
  Value=ReadU32(Name)
  if Value>0x7FFFFFFF:
    Value-=0x100000000
  return Value

def ReadDataBlock(Name, ReadSizeProc=ReadU16):
  Size=ReadSizeProc(Name+" size")
  return ReadAndCheck(Name,Size)

def LineName(Name):
  global NameOfTheLine
  NameOfTheLine=Name

def ReadInventoryLine():
  Line=ReadLine()
  Result=[]
  Pos=0
  Buffer=""
  WasBackslash=False
  InsideString=False
  for Ch in Line:
    if Ch<" " or Ch>"~":
      MalformedLine("contains invalid character")
    if InsideString:
      if WasBackslash:
        WasBackslash=False
      elif Ch=="\\":
        WasBackslash=True
      elif Ch=="\"":
        InsideString=False
    else:
      if Ch==" ":
        if Buffer!="":
          Result.append(Buffer)
          Buffer=""
        continue
      elif Ch=="\"":
        InsideString=True
    Buffer+=Ch
  if Buffer!="":
    Result.append(Buffer)
  return Result

def MalformedLine(Msg):
  Malformed(NameOfTheLine+" "+Msg)

def ReadLine():
  Line=InFile.readline()
  if Line[-1]!="\n":
    MalformedLine("has an invalid end: "+repr(Line[-1]))
  return Line[:-1]

def ToInt(Name, Value):
  try:
    return int(Value)
  except ValueError:
    Malformed(Name+' is not a valid number: '+repr(Value))

def ParseInventorySet():
  def InventoryLineName(Name):
    LineName('Inventory '+Name)
  def CheckComponentCount(Count):
    if len(Line)!=Count:
      MalformedLine('has wrong count of components: '+str(len(Line)))
  def CheckOpCode(Expected):
    if isinstance(Expected, str):
      Invalid=OpCode!=Expected
    elif isinstance(Expected, tuple):
      Invalid=OpCode not in Expected
    else:
      raise ValueError('Wrong type of "Expected"')
    if Invalid:
      Msg=Name+" is not "
      if isinstance(Expected, tuple):
        Msg+=' in '
        Expected='", "'.join(Expected)
      Msg+='"'+Expected+'"'
      MalformedLine('is not '+Expected+': '+repr(OpCode))
  Result=[]
  while True:
    InventoryLineName("header line 1")
    Line=ReadInventoryLine()
    if Line[0]=="EndInventory":
      break
    CheckComponentCount(3)
    Inv=TInventory()
    Result.append(Inv)
    OpCode,Inv.Name,Count=Line
    CheckOpCode("List")
    Count=ToInt("Inventory item count", Count)
    InventoryLineName("header line 2")
    Line=ReadInventoryLine()
    CheckComponentCount(2)
    OpCode,Width=Line
    CheckOpCode("Width")
    Inv.Width=ToInt("Inventory width", Width)
    Num=0
    Inv.Stacks=[]
    while True:
      Count=Count-1
      Num+=1
      InventoryLineName("data line "+str(Num))
      Line=ReadInventoryLine()
      OpCode=Line[0]
      CheckOpCode(("Empty","Item","EndInventoryList"))
      if OpCode=="EndInventoryList":
        if Count>0:
          Malformed("Too few inventory list lines")
        break
      elif OpCode=="Empty":
        CheckComponentCount(1)
        Stack=None
      else:
        Stack=TStack()
        if len(Line)==5:
          Stack.Meta=Line.pop()
        Stack.Wear=0
        if len(Line)==4:
          Wear=Line.pop()
          Stack.Wear=ToInt("Item wear", Wear)
        if len(Line)==2:
          OpCode,Stack.Name=Line
          Stack.Size=1
        else:
          if len(Line)!=3:
            print repr(Line)
          CheckComponentCount(3)
          OpCode,Stack.Name,StackSize=Line
          Stack.Size=ToInt("Stack size", StackSize)
        if Stack.Size<1 or Stack.Size>65535:
          Malformed("Invalid stack size: "+str(Stack.Size))
        if Stack.Size!=1:
          if Stack.Wear!=0:
            Malformed("Worn out multiitem stack encountered")
          elif Stack.Meta is not None:
            Malformed("Multiitem stack with metadata encountered")
      Inv.Stacks.append(Stack)
  return Result

def CheckField(Name, Expected, ReaderProc=ReadU8, ZeroIsNotOk=True):
  Value=ReaderProc(Name)
  if ZeroIsNotOk or Value!=0:
    if Value!=Expected:
      Malformed(Name+" is "+str(Value)+", should be "+str(Expected))
  return Value

VarChars="0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def ParseMetaData(Block):
  Version=Block.Version
  Block.Meta=[]
  if Version<=22:
    Reader=ReadU16
  else:
    Reader=ReadU8
  if Version==28:
    Expected=2
  else:
    Expected=1
  MetadataVersion=CheckField("Metadata version", Expected, Reader, False)
  if MetadataVersion==0:
    return
  MetadataCount=ReadU16("Metadata count")
  while MetadataCount>0:
    MetadataCount-=1
    Item=TMetaDataItem()
    Block.Meta.append(Item)
    Item.Position=ReadU16("Position")
    if Version<=22:
      Item.TypeId=ReadU16("Type ID")
      Item.Content=ReadDataBlock("Content")
      continue
    VarCount=ReadU32("Metadata variable count")
    VarNum=0
    VariablesSeen={}
    Item.Variables=[]
    while VarCount>0:
      VarCount-=1
      VarNum=VarNum+1
      Name=ReadDataBlock("Metadata variable name")
      for Ch in Name:
        if Ch not in VarChars:
          Msg="Variable name contains invalid char '"+repr(Ch)+'"'
          Malformed(Msg+": "+repr(Name))
      if Name in VariablesSeen:
        Malformed("Variable encountered more than once: "+Name)
      VariablesSeen[Name]=True
      Value=ReadDataBlock("Metadata variable value", ReadU32)
      Item.Variables.append((Name, Value))
      if Version>=28:
        Unknown=ReadAndCheck("Unknown after metadata variable value", 1)
        if Unknown!="\x00":
          Malformed("Unsupported data after variable: "+ToHex(Unknown))
    Item.InventorySet=ParseInventorySet()

def ParseBlockHeader():
  Block=TBlockInfo()
  Version=ReadU8("Version")
  Block.Version=Version
  if Version<22 or Version>28:
    Malformed("\nDATA VERSION NOT SUPPORTED: "+str(Version))
  Block.Flags=ReadU8("Flags")
  if Version>=27:
    Block.LightingFlags=ReadU16("Lighting completion flags")
  if Version<=23:
    Expected=1
  else:
    Expected=2
  CheckField("Content width", Expected)
  CheckField("Parameters width", 2)
  return Block

def ParseNodeTimers(Result):
  TimerCount=ReadU16("Timer count")
  while TimerCount>0:
    Timer=TTimer()
    Result.append(Timer)
    TimerCount-=1
    Timer.Position=ReadU16("Timer position")
    Timer.Timeout=ReadS32("Timer timeout")
    Timer.Elapsed=ReadS32("Timer elapsed time")

def ParseBlockRest(Block):
  Version=Block.Version
  Block.Objects=[]
  Block.Timers=[]
  if Version<=24:
    TimerVersion=ReadU8("Timer data version")
    if TimerVersion==1:
      if Version==23:
        Malformed("Timer data version 1 in mapblock version 23")
      ParseNodeTimers(Block.Timers)
    elif TimerVersion!=0:
      Malformed("Timer format version invalid: "+str(TimerVersion))
  ObjectDataVersion=ReadU8("Object data version")
  if ObjectDataVersion!=0:
    Malformed("Object data version invalid: "+str(ObjectDataVersion))
  ObjectCount=ReadU16("Object count")
  while ObjectCount>0:
    ObjectCount-=1
    Object=TObject()
    Block.Objects.append(Object)
    Object.Type=ReadU8("Object type")
    Object.PosX=ReadS32("Object X position")
    Object.PosY=ReadS32("Object Y position")
    Object.PosZ=ReadS32("Object Z position")
    if Object.Type==7:
      ObjectDataSize=ReadU16("LuaEntity data size")
      ObjectVersion=ReadU8("LuaEntity data version")
      ObjectDataSize-=1
      if ObjectVersion!=1:
        Malformed("Unsupported LuaEntity data version: "+str(ObjectVersion))
      Object.Name=ReadDataBlock("LuaEntity name")
      ObjectDataSize-=len(Object.Name)+2
      Object.Data=ReadDataBlock("LuaEntity data", ReadU32)
      ObjectDataSize-=len(Object.Data)+4
      Object.Health=ReadU16("LuaEntity health")
      Object.VelocityX=ReadS32("LuaEntity X velocity")
      Object.VelocityY=ReadS32("LuaEntity Y velocity")
      Object.VelocityZ=ReadS32("LuaEntity Z velocity")
      Object.Yaw=ReadS32("LuaEntity Yaw")
      ObjectDataSize-=2+4+4+4+4
      if ObjectDataSize!=0:
        Malformed("LuaEntity data inconsistent with object data size")
    else:
      Object.Data=ReadDataBlock("Object data")
  Block.TimeStamp=ReadU32("Last save timestamp")
  NameMapVersion=ReadU8("Name to ID mapping version")
  if NameMapVersion!=0:
    Malformed("Name to ID mapping version invalid: "+str(NameMapVersion))
  NameMapCount=ReadU16("Name to ID mapping count")
  Block.NameList=[]
  Block.NameMap={}
  while NameMapCount>0:
    NameMapCount-=1
    Ident=ReadU16("Mapping item ID")
    Name=ReadDataBlock("Mapping item name")
    if Ident in Block.NameMap:
      Malformed("ID is already mapped: "+str(Ident))
    Block.NameList.append((Ident,Name))
    Block.NameMap[Ident]=Name
  if Version>=25:
    TimerDataSize=ReadU8("Timer data size")
    if TimerDataSize!=10:
      Malformed("Timer data size invalid: "+str(TimerDataSize))
    ParseNodeTimers(Block.Timers)

def Iterate(Name):
  for Z in range(16):
    for Y in range(16):
      for X in range(16):
        yield X,Y,Z,Name+" for ("+str(X)+","+str(Y)+","+str(Z)+")"

def ParseBlockData(Block):
  Version=Block.Version
  Map=[]
  Block.Map=Map
  for Y in range(16):
    Plane=[]
    Map.append((Y,Plane))
    for X in range(16):
      Plane.append((X,[]))
  for X,Y,Z,Name in Iterate("Param0"):
    if Version<=23:
      Param=ReadU8(Name)
    else:
      Param=ReadU16(Name)
    Plane=Map[Y][1]
    Row=Plane[X][1]
    Row.append((Z,[Param]))
  for X,Y,Z,Name in Iterate("Param1"):
    Param=ReadU8(Name)
    Plane=Map[Y][1]
    Row=Plane[X][1]
    Item=Row[Z][1]
    Item.append(Param)
  for X,Y,Z,Name in Iterate("Param2"):
    Param=ReadU8(Name)
    Plane=Map[Y][1]
    Row=Plane[X][1]
    Item=Row[Z][1]
    if Version<=23:
      Param0=Item[0]
      if Param0>=0x80:
        Param0*=16
        Param0+=Param/16
        Param=Param%16
        Item[0]=Param0
    Item.append(Param)

def ParseBinaryBlock(InF):
  global InFile
  InFile=InF
  try:
    Block=ParseBlockHeader()
    ParseBlockData(Block)
    ParseMetaData(Block)
    ParseBlockRest(Block)
  finally:
    InFile=None
  return Block
