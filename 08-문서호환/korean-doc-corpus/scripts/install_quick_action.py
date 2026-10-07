#!/usr/bin/env python3
"""Finder 빠른 동작 '문서를 MD로 변환' 설치 (폴더·파일 우클릭 → 빠른 동작).
폴더 → <폴더>_md 로 일괄 변환 후 열기. 파일 → 같은 폴더에 이름.md.

기존 ~/Library/Services 의 Run Shell Script 워크플로 구조를 그대로 만든다.
다시 실행하면 덮어쓴다. 제거: ~/Library/Services/문서를 MD로 변환.workflow 삭제.
"""
import plistlib, shutil, subprocess, uuid
from pathlib import Path

NAME = "문서를 MD로 변환"
OLD = Path.home() / "Library/Services/문서를 MD로 일괄 변환.workflow"  # 이전 이름(폴더 전용)
WF = Path.home() / "Library/Services" / f"{NAME}.workflow" / "Contents"

COMMAND = 'zsh "$HOME/.claude/skills/korean-doc-corpus/scripts/convert.sh" "$@"'


def arg(i, name, default):
    return {"default value": default, "name": name, "required": "0", "type": "0", "uuid": str(i)}


action = {
    "AMAccepts": {"Container": "List", "Optional": True, "Types": ["com.apple.cocoa.string"]},
    "AMActionVersion": "2.0.3",
    "AMApplication": ["Automator"],
    "AMParameterProperties": {k: {} for k in ["COMMAND_STRING", "CheckedForUserDefaultShell", "inputMethod", "shell", "source"]},
    "AMProvides": {"Container": "List", "Types": ["com.apple.cocoa.string"]},
    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
    "ActionName": "Run Shell Script",
    "ActionParameters": {"COMMAND_STRING": COMMAND, "CheckedForUserDefaultShell": True,
                         "inputMethod": 1, "shell": "/bin/zsh", "source": ""},  # 1 = 인자로 전달
    "BundleIdentifier": "com.apple.RunShellScript",
    "CFBundleVersion": "2.0.3",
    "CanShowSelectedItemsWhenRun": False,
    "CanShowWhenRun": True,
    "Category": ["AMCategoryUtilities"],
    "Class Name": "RunShellScriptAction",
    "InputUUID": str(uuid.uuid4()).upper(),
    "Keywords": ["Shell", "Script", "Command", "Run", "Unix"],
    "OutputUUID": str(uuid.uuid4()).upper(),
    "UUID": str(uuid.uuid4()).upper(),
    "UnlocalizedApplications": ["Automator"],
    "arguments": {str(i): arg(i, n, v) for i, (n, v) in enumerate(
        [("inputMethod", 0), ("CheckedForUserDefaultShell", False), ("source", ""),
         ("COMMAND_STRING", ""), ("shell", "")])},
    "isViewVisible": 1,
}

INPUT = "com.apple.Automator.fileSystemObject"  # 파일+폴더
doc = {
    "AMApplicationBuild": "534", "AMApplicationVersion": "2.10", "AMDocumentVersion": "2",
    "actions": [{"action": action, "isViewVisible": 1}],
    "connectors": {},
    "workflowMetaData": {
        "applicationBundleIDsByPath": {}, "applicationPaths": [],
        "inputTypeIdentifier": INPUT, "outputTypeIdentifier": "com.apple.Automator.nothing",
        "presentationMode": 15, "processesInput": False,
        "serviceApplicationBundleID": "com.apple.finder", "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
        "serviceInputTypeIdentifier": INPUT, "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
        "serviceProcessesInput": False, "systemImageName": "NSActionTemplate",
        "useAutomaticInputType": False, "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
    },
}

info = {"NSServices": [{
    "NSBackgroundColorName": "background",
    "NSIconName": "NSActionTemplate",
    "NSMenuItem": {"default": NAME},
    "NSMessage": "runWorkflowAsService",
    "NSRequiredContext": {"NSApplicationIdentifier": "com.apple.finder"},
    # ponytail: HWP/HWPX UTI는 한컴 뷰어가 설치돼 있어야 잡힌다. 없는 맥이면 "public.data" 추가
    "NSSendFileTypes": ["public.folder", "com.adobe.pdf",
                        "org.openxmlformats.wordprocessingml.document", "org.openxmlformats.spreadsheetml.sheet",
                        "com.microsoft.excel.xls", "com.haansoft.hancomofficeviewer.mac.hwp",
                        "com.haansoft.hancomofficeviewer.mac.hwpx"],
}]}

shutil.rmtree(OLD, ignore_errors=True)
WF.mkdir(parents=True, exist_ok=True)
plistlib.dump(doc, open(WF / "document.wflow", "wb"))
plistlib.dump(info, open(WF / "Info.plist", "wb"))
subprocess.run(["/System/Library/CoreServices/pbs", "-update"])
print(f"설치됨: {WF.parent}")

# ── 바탕화면 앱(드롭렛): 아이콘에 끌어다 놓기 / 더블클릭 → 파일·폴더 선택 ──
APP = Path.home() / "Desktop" / f"{NAME}.app"
APPLESCRIPT = '''
on run
	set b to button returned of (display dialog "변환할 대상을 고르세요." & return & "(아이콘 위로 파일·폴더를 끌어다 놓아도 됩니다)" buttons {"취소", "파일", "폴더"} default button "폴더" with title "문서를 MD로 변환")
	if b is "폴더" then
		set xs to choose folder with prompt "MD로 변환할 폴더" with multiple selections allowed
	else if b is "파일" then
		set xs to choose file with prompt "MD로 변환할 파일 (hwp·hwpx·pdf·docx·xlsx·xls)" with multiple selections allowed
	else
		return
	end if
	convert(xs)
end run

on open xs
	convert(xs)
end open

on convert(xs)
	set cmd to "/bin/zsh " & quoted form of (POSIX path of (path to home folder) & ".claude/skills/korean-doc-corpus/scripts/convert.sh")
	repeat with x in xs
		set cmd to cmd & " " & quoted form of POSIX path of x
	end repeat
	do shell script cmd
end convert
'''
ICON = Path(__file__).with_name("icon.icns")
shutil.rmtree(APP, ignore_errors=True)
subprocess.run(["osacompile", "-o", str(APP), "-e", APPLESCRIPT], check=True)
if ICON.exists():
    shutil.copy(ICON, APP / "Contents/Resources/droplet.icns")
    (APP / "Contents/Resources/Assets.car").unlink(missing_ok=True)  # 있으면 이쪽 아이콘이 우선
    subprocess.run(["plutil", "-remove", "CFBundleIconName", str(APP / "Contents/Info.plist")])
    subprocess.run(["codesign", "--force", "--deep", "-s", "-", str(APP)], check=True)  # 아이콘 교체로 깨진 서명 복구
    subprocess.run(["touch", str(APP)])
print(f"설치됨: {APP}")
