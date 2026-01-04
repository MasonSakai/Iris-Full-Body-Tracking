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


	def __init__(self):
		self.crossRefs = CrossRefHandler()
		self.initer = PostLoadIniter()

	def InitLoading(self, filePath: str) -> None:
		if Scribe.mode != LoadSaveMode.Inactive:
			Log.Error(f"Called InitLoading() but current mode is {Scribe.mode.name}")
			Scribe.ForceStop()
		if self.curParent is not None:
			Log.Error("Current parent is not null in InitLoading");
			self.curParent = None
		if self.curPathRelToParent != None:
			Log.Error("Current path relative to parent is not null in InitLoading")
			self.curPathRelToParent = None
		try:
			tree = ET.parse(filePath)
			self.curXmlParent = tree.getroot()
			self.curPathRelToParent = ''
			Scribe.mode = LoadSaveMode.LoadingVars
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception while init loading file: {filePath}\n{str(ex)}")
			self.ForceStop()
			raise
		
	def InitLoadingFromString(self, data: str) -> None:
		if Scribe.mode != LoadSaveMode.Inactive:
			Log.Error(Log.LogLevel.Critical, f"Called InitLoading() but current mode is {Scribe.mode.name}")
			Scribe.ForceStop()
		if self.curParent is not None:
			Log.Error(Log.LogLevel.Critical, "Current parent is not null in InitLoading");
			self.curParent = None
		if self.curPathRelToParent != None:
			Log.Error(Log.LogLevel.Critical, "Current path relative to parent is not null in InitLoading")
			self.curPathRelToParent = None
		try:
			self.curXmlParent = ET.fromstring(data)
			Scribe.mode = LoadSaveMode.LoadingVars
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception while init loading string: {data}\n{str(ex)}")
			self.ForceStop()
			raise

	def FinalizeLoading(self) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Critical, f"Called FinalizeLoading() but current mode is {Scribe.mode.name}")
		else:
			try:
				Scribe.ExitNode()
				self.curXmlParent = None
				self.curParent = None
				self.curPathRelToParent = None
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
		self.crossRefs.Clear(False)
		self.initer.Clear()
		match Scribe.mode:
			case LoadSaveMode.LoadingVars | LoadSaveMode.ResolvingCrossRefs | LoadSaveMode.PostLoadInit:
				Scribe.mode = LoadSaveMode.Inactive