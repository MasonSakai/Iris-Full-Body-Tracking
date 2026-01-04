from lxml import etree as ET

from utils import Log
from utils.scribe import IExposable, LoadSaveMode, Scribe
from utils.scribe.internal.CrossRefHandler import CrossRefHandler
from utils.scribe.internal.PostLoadIniter import PostLoadIniter


class ScribeLoader:
	
	crossRefs: CrossRefHandler
	initer: PostLoadIniter
	curParent: IExposable
	curXmlParent: ET.ElementBase
	curPathRelToParent: str
	has_load_file: bool

	def __init__(self):
		self.crossRefs = CrossRefHandler()
		self.initer = PostLoadIniter()

	def BeginLoadSession(self) -> None:
		if Scribe.mode != LoadSaveMode.Inactive:
			Log.Error(Log.LogLevel.Error, f"Called BeginLoadSession() but current mode is {Scribe.mode.name}")
			Scribe.ForceStop()
			
		Scribe.mode = LoadSaveMode.LoadingVars
		
	def LoadFile(self, filePath: str) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Critical, f"Called LoadFile() but current mode is {Scribe.mode.name}")
			Scribe.ForceStop()
			return
		if self.has_load_file:
			Log.Error(Log.LogLevel.Warning, "File opened when LoadFile called, closing");
			self.CloseFile()
		if self.curParent is not None:
			Log.Error(Log.LogLevel.Error, "Current parent is not null in LoadFile");
			self.curParent = None
		if self.curPathRelToParent != None:
			Log.Error(Log.LogLevel.Error, "Current path relative to parent is not null in LoadFile")
			self.curPathRelToParent = None
		try:
			tree = ET.parse(filePath)
			self.curXmlParent = tree.getroot()
			self.curPathRelToParent = ''
			self.has_load_file = True
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception while init loading file: {filePath}\n{ex}")
			self.ForceStop()
			raise
		
	def LoadString(self, data: str) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Critical, f"Called LoadString() but current mode is {Scribe.mode.name}")
			Scribe.ForceStop()
			return
		if self.has_load_file:
			Log.Error(Log.LogLevel.Warning, "File opened when LoadFile called, closing");
			self.CloseFile()
		if self.curParent is not None:
			Log.Error(Log.LogLevel.Error, "Current parent is not null in LoadString");
			self.curParent = None
		if self.curPathRelToParent != None:
			Log.Error(Log.LogLevel.Error, "Current path relative to parent is not null in LoadString")
			self.curPathRelToParent = None
		try:
			self.curXmlParent = ET.fromstring(data)
			self.curPathRelToParent = ''
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception while init loading string: {data}\n{ex}")
			self.ForceStop()
			raise

	def CloseFile(self) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Critical, f"Called EndFile() but current mode is {Scribe.mode.name}")
		else:
			Scribe.ExitNode()
			self.curXmlParent = None
			self.curParent = None
			self.curPathRelToParent = None
			self.has_load_file = False

	def EndLoadSession(self) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Critical, f"Called FinalizeLoading() but current mode is {Scribe.mode.name}")
		else:
			try:
				if self.has_load_file:
					Log.Error(Log.LogLevel.Warning, "File opened when FinalizeLoading called, closing");
					self.CloseFile()
				Scribe.mode = LoadSaveMode.Inactive
				#DeepProfiler.Start("ResolveAllCrossReferences()")
				self.crossRefs.ResolveAllCrossReferences()
				#DeepProfiler.End();
				#DeepProfiler.Start("DoAllPostLoadInits()")
				self.initer.DoAllPostLoadInits()
				#DeepProfiler.End()
			except Exception as ex:
				Log.Error(Log.LogLevel.Critical, f"Exception in FinalizeLoading(): {ex}")
				self.ForceStop()
				raise

	def InitLoading(self, path: str) -> None:
		self.BeginLoadSession()
		self.LoadFile(path)

	def InitLoadingFromString(self, data: str) -> None:
		self.BeginLoadSession()
		self.LoadString(data)

	def FinalizeLoading(self) -> None:
		self.CloseFile()
		self.EndLoadSession()

	def EnterNode(self, nodeName: str) -> bool:
		if self.curXmlParent is not None:
			childNode = self.curXmlParent.find(nodeName)
			if childNode is None and nodeName.isnumeric():
				childNode = list(self.curXmlParent)[int(nodeName)]
			if childNode is None:
				return False
			self.curXmlParent = childNode
		if self.curPathRelToParent is None:
			self.curPathRelToParent = ''
		self.curPathRelToParent += '/' + nodeName
		return True

	def ExitNode(self) -> None:
		if self.curXmlParent is not None:
			self.curXmlParent = self.curXmlParent.getparent()
		if self.curXmlParent is None:
			return
		length = self.curPathRelToParent.rfind('/')
		self.curPathRelToParent = self.curPathRelToParent[:length]
	
	def ForceStop(self) -> None:
		self.curXmlParent = None
		self.curParent = None
		self.curPathRelToParent = None
		self.has_load_file = False
		self.crossRefs.Clear(False)
		self.initer.Clear()
		match Scribe.mode:
			case LoadSaveMode.LoadingVars | LoadSaveMode.ResolvingCrossRefs | LoadSaveMode.PostLoadInit:
				Scribe.mode = LoadSaveMode.Inactive