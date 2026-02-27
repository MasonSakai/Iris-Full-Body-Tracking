import os
from typing import Type
from lxml import etree as ET

from utils import Log
from utils.scribe import LoadSaveMode, Scribe
from utils import ParseHelper
from utils.scribe.internal.DebugLoadIDsSavingErrorsChecker import DebugLoadIDsSavingErrorsChecker


class ScribeSaver:
	
	baseXmlTree: ET.ElementBase
	curXmlParent: ET.ElementBase
	curPathRelToParent: str

	savingForDebug: bool
	anyInternalException: bool

	loadIDsErrorsChecker: DebugLoadIDsSavingErrorsChecker

	def __init__(self):
		self.loadIDsErrorsChecker = DebugLoadIDsSavingErrorsChecker()
		
		self.curXmlParent = None
		self.curPathRelToParent = None
		self.baseXmlTree = None
		self.savingForDebug = False
		self.anyInternalException = False
	
	def InitSaving(self, documentElementName: str) -> None:
		if Scribe.mode != LoadSaveMode.Inactive:
			Log.Error(Log.LogLevel.Critical, f"Called InitSaving() but current mode is {Scribe.mode.name}");
			Scribe.ForceStop()
		try:
			Scribe.mode = LoadSaveMode.Saving
			self.EnterNode(documentElementName)
			self.baseXmlTree = ET.ElementTree(self.curXmlParent)
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
				raise Exception(f"Can't finalize saving due to internal exception. The whole file would be most likely corrupted anyway. File path: {filePath}")
			try:
				self.ExitNode()
				dirname = os.path.dirname(filePath)
				if dirname:
					os.makedirs(dirname, exist_ok=True)
				self.baseXmlTree.write(filePath, encoding="utf-8", xml_declaration=True, pretty_print=True)

				Scribe.mode = LoadSaveMode.Inactive;
				self.savingForDebug = False
				self.loadIDsErrorsChecker.CheckForErrorsAndClear()
				self.curXmlParent = None
				self.baseXmlTree = None
				self.curPathRelToParent = None
				self.anyInternalException = False
			except Exception as ex:
				Log.Error(Log.LogLevel.Critical, f"Exception in FinalizeLoading(): {ex}")
				self.ForceStop()
				raise

	def WriteElement[T](self, elementName: str, value: T, vType: Type[T]) -> None:
		if self.curXmlParent is None:
			Log.Error(Log.LogLevel.Error, "Called WriteElemenet(), but writer is null.")
		else:
			try:
				node: ET.ElementBase = ET.SubElement(self.curXmlParent, elementName)
				o = ParseHelper.ToString(value, vType)
				if isinstance(o, str):
					node.text = o
				else:
					(text, attrs) = o
					node.text = text
					for (k, v) in attrs:
						node.set(k, v)
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
		
	def EnterNode(self, nodeName: str | int) -> bool:
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
		self.curPathRelToParent = None
		self.baseXmlTree = None
		self.savingForDebug = False
		self.anyInternalException = False
		self.loadIDsErrorsChecker.Clear()
		if Scribe.mode != LoadSaveMode.Saving:
			return
		Scribe.mode = LoadSaveMode.Inactive