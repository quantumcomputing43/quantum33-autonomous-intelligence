#!/usr/bin/env python3
"""Static pre-build audit for the Android phone agent."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app"
BUILD = APP / "build.gradle"
ROOT_BUILD = ROOT / "build.gradle"
SETTINGS = ROOT / "settings.gradle"
MANIFEST = APP / "src/main/AndroidManifest.xml"
ACTIVITY = APP / "src/main/java/org/quantum33/autonomousagent/MainActivity.kt"
BRIDGE = APP / "src/main/python/phone_agent_bridge.py"
RUNTIME = APP / "src/main/python/program/runtime.py"
TOOL_EXECUTOR = APP / "src/main/python/program/tool_executor.py"
WORKFLOW = ROOT.parent / ".github/workflows/build-phone-agent.yml"

errors = []

def require(path, text, label):
    if not path.exists():
        errors.append(f"{label}: missing {path}")
        return
    data = path.read_text(encoding="utf-8")
    if text not in data:
        errors.append(f"{label}: missing required contract {text!r}")

contracts = [
    (ROOT_BUILD, "com.chaquo.python", "root Gradle"),
    (BUILD, "id 'com.chaquo.python'", "app Gradle plugin"),
    (BUILD, "chaquopy {", "Chaquopy DSL"),
    (BUILD, "version = '3.11'", "Python runtime version"),
    (BUILD, "buildPython 'python3.11'", "Python build interpreter"),
    (BUILD, "jvmToolchain(17)", "Kotlin JVM target"),
    (BUILD, "JavaVersion.VERSION_17", "Java JVM target"),
    (BUILD, "abiFilters 'arm64-v8a', 'armeabi-v7a'", "RMX3690 ABI contract"),
    (SETTINGS, "mavenCentral()", "plugin repository"),
    (MANIFEST, "android.permission.INTERNET", "network permission"),
    (MANIFEST, 'android:windowSoftInputMode="adjustResize"', "keyboard resize contract"),
    (ACTIVITY, "SAVE CONFIGURATION SECURELY", "configuration persistence UI"),
    (ACTIVITY, "VALIDATE CONFIGURATION", "configuration validation UI"),
    (ACTIVITY, "SEND COMMAND TO AGENT", "command action UI"),
    (BRIDGE, "def validate_configuration(", "configuration validation bridge"),
    (BRIDGE, "def handle_command(", "Python command bridge"),
    (RUNTIME, "MAX_STEPS = 6", "bounded autonomous loop"),
    (RUNTIME, "validate_configuration", "runtime configuration validation"),
    (TOOL_EXECUTOR, "class ToolExecutor", "allow-listed tool executor"),
    (TOOL_EXECUTOR, "self._write()", "write authorization gate"),
    (APP / "src/main/python/program/memory.py", "class MemoryStore", "persistent local memory"),
    (WORKFLOW, "actions/setup-python@v5", "CI Python provisioning"),
    (WORKFLOW, "zipalign", "APK alignment verification"),
    (WORKFLOW, "sha256sum", "APK digest verification"),
    (WORKFLOW, "pytest -q tests", "runtime safety tests"),
]

for item in contracts:
    require(*item)

root_build = ROOT_BUILD.read_text(encoding="utf-8")
m = re.search(r"com\\.android\\.application[\\'\\\"]\\s+version\\s+[\\'\\\"]([0-9.]+)", root_build)
c = re.search(r"com\\.chaquo\\.python[\\'\\\"]\\s+version\\s+[\\'\\\"]([0-9.]+)", root_build)
if not m or not c:
    errors.append("version contract: could not parse AGP/Chaquopy versions")
else:
    agp = tuple(map(int, m.group(1).split(".")))
    chaq = tuple(map(int, c.group(1).split(".")))
    if chaq[:2] == (16, 0) and not ((8, 6) <= agp[:2] <= (8, 8)):
        errors.append(f"Chaquopy 16.0 / AGP {m.group(1)} compatibility mismatch")

activity = ACTIVITY.read_text(encoding="utf-8")
decls = re.findall(r"\\b(?:val|var|private\\s+lateinit\\s+var)\\s+(\\w+)\\s*(?::|=)", activity)
seen = set()
dupes = []
for name in decls:
    if name in seen:
        dupes.append(name)
    seen.add(name)
if dupes:
    errors.append("Kotlin duplicate declarations: " + ", ".join(sorted(set(dupes))))

bridge = BRIDGE.read_text(encoding="utf-8")
if bridge.count("def handle_command(") != 1 or bridge.count("def validate_configuration(") != 1:
    errors.append("Python bridge: expected exactly one command and validation entrypoint")

workflow = WORKFLOW.read_text(encoding="utf-8")
audit_pos = workflow.find("audit_phone_agent.py")
build_pos = workflow.find("gradle assembleDebug")
if audit_pos < 0:
    errors.append("CI: pre-build audit step is missing")
elif build_pos >= 0 and audit_pos > build_pos:
    errors.append("CI: audit must run before assembleDebug")

if errors:
    print("PHONE_AGENT_AUDIT: FAIL")
    for e in errors:
        print(" - " + e)
    sys.exit(1)

print("PHONE_AGENT_AUDIT: PASS")
