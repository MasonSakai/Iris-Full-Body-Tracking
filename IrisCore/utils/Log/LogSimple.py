

import os
from utils import Log


messages: list[str] = []
tabDepth: int = 0

def Message(text: str):
    for _ in range(tabDepth):
        text = "  " + text;
    messages.append(text)

def BeginTabMessage(text: str):
    Message(text)
    tabDepth += 1

def EndTab():
    tabDepth -= 1

def FlushToFileAndOpen():
    if len(messages) == 0:
        return
    path = os.path.join(GenFilePaths.SaveDataFolderPath, "LogSimple.txt")
    with open(path, 'w') as f:
        log = CompiledLog();
        f.write(log)
    messages.Clear()

def FlushToStandardLog(logLevel: Log.LogLevel = Log.LogLevel.Info):
    if len(messages) == 0:
        return
    Log.Message(logLevel, CompiledLog())
    messages.clear()

def CompiledLog() -> str:
    log = ''
    for message in messages:
        log += message + '\n'
    return log.rstrip()