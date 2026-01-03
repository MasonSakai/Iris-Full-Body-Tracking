from lxml import etree as ET

from utils import Log
from utils.scribe import IExposable, LoadSaveMode, Scribe, Scribe_Deep


class ScribeSaver:
	
	curXmlParent: ET.ElementBase
	curPathRelToParent: str

	savingForDebug: bool
	anyInternalException: bool
	
	def InitSaving(self, documentElementName: str) -> None:
		if Scribe.mode != LoadSaveMode.Inactive:
			Log.Error(Log.LogLevel.Critical, f"Called InitSaving() but current mode is {Scribe.mode.name}");
			Scribe.ForceStop()
		try:
			Scribe.mode = LoadSaveMode.Saving
			self.EnterNode(documentElementName)
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception while init saving\n{ex}")
			self.ForceStop()
			raise

	def FinalizeSaving(self, filePath: str) -> None:
		if Scribe.mode != LoadSaveMode.Saving:
			Log.Error(Log.LogLevel.Critical, f"Called FinalizeSaving() but current mode is {Scribe.mode.name}")
		else:
			if self.anyInternalException:
				self.ForceStop();
				raise Exception(Log.LogLevel.Critical, f"Can't finalize saving due to internal exception. The whole file would be most likely corrupted anyway. File path: {filePath}")
			try:
				self.ExitNode();
				ET.ElementTree(self.curPathRelToParent).write(filePath, encoding="utf-8", xml_declaration=True, pretty_print=True)

				Scribe.mode = LoadSaveMode.Inactive;
				self.savingForDebug = False
				self.curXmlParent = None
				self.curParent = None
				self.curPathRelToParent = None
				self.anyInternalException = False
			except Exception as ex:
				Log.Error(Log.LogLevel.Critical, f"Exception in FinalizeLoading(): {ex}")
				self.ForceStop()
				raise

	def WriteElement(self, elementName: str, value: str) -> None:
		if self.curXmlParent is None:
			Log.Error(Log.LogLevel.Error, "Called WriteElemenet(), but writer is null.")
		else:
			try:
				ET.SubElement(self.curXmlParent, elementName).text = value
			except Exception as ex:
				self.anyInternalException = True
				raise

	def WriteAttribute(self, attributeName: str, value: str) -> None:
		if self.curXmlParent is None:
			Log.Error(Log.LogLevel.Error, "Called WriteAttribute(), but root is null.")
		else:
			try:
				self.curXmlParent.set(attributeName, value);
			except Exception as ex:
				self.anyInternalException = True
				raise

	# def DebugOutputFor(self, saveable: IExposable) -> str:
	# 	if Scribe.mode != LoadSaveMode.Inactive:
	# 		Log.Error(Log.LogLevel.Error, "DebugOutput needs current mode to be Inactive")
	# 		return ""
	# 	try:
	# 		with StringWriter() as output:
	# 			settings = XmlWriterSettings()
	# 			settings.Indent = True
	# 			settings.IndentChars = "  "
	# 			settings.OmitXmlDeclaration = True
	# 			try:
	# 				with  XmlWriter.Create(output, settings) as self.writer:
	# 					Scribe.mode = LoadSaveMode.Saving
	# 					self.savingForDebug = True
	# 					Scribe_Deep.Look(saveable, saveable.__qualname__, IExposable)
	# 				return output.ToString()
	# 			finally:
	# 				self.ForceStop()
	# 	except Exception as ex:
	# 		Log.Error(Log.LogLevel.Error, f"Exception while getting debug output: {ex}")
	# 		self.ForceStop()
	# 		return ""
		
	def EnterNode(self, nodeName: str) -> bool:
		try:
			if self.curXmlParent is None:
				self.curXmlParent = ET.Element(nodeName)
				self.curPathRelToParent = nodeName
			else:
				self.curXmlParent = ET.SubElement(self.curXmlParent, nodeName)
				self.curPathRelToParent += '/' + nodeName
			return True
		except Exception as ex:
			self.anyInternalException = True
			return False

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
		self.savingForDebug = False
		self.anyInternalException = False
		if Scribe.mode != LoadSaveMode.Saving:
			return
		Scribe.mode = LoadSaveMode.Inactive