#!/usr/bin/env python3
"""Static pre-build audit for the Android phone agent.

This audit checks mechanical build contracts only. It does not alter scientific
questions, endpoints, thresholds, hypotheses, or project data.
"""
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
WORKFLOW = ROOT.parent / ".github/workflows/build-phone-agent.yml"

errors = []

def require(path, text, label):
    if not path.exists():
        errors.append(f"{label}: missing {path}")
        return
    data = path.read_text(encoding="utf-8")
    if text not in data:
        errors.append(f"{label}: missing required contract {text!r}")

# Repository/build structure.
require(ROOT_BUILD, "com.chaquo.python", "root Gradle")
require(BUILD, "id 'com.chaquo.python'", "app Gradle plugin")
require(BUILD, "chaquopy {", "Chaquopy DSL")
require(BUILD, "version = '3.11'", "Python runtime version")
require(BUILD, "abiFilters 'arm64-v8a', 'x86_64'", "ABI contract")
require(SETTINGS, "mavenCentral()", "plugin repository")
require(MANIFEST, "android.permission.INTERNET", "network permission")

# Chaquopy 16.x + AGP 8.7.x compatibility guard.
root_build = ROOT_BUILD.read_text(encoding="utf-8")
m = re.search(r"com\.android\.application['\"]\s+version\s+['\"]([0-9.]+)", root_build)
c = re.search(r"com\.chaquo\.python['\"]\s+version\s+['\"]([0-9.]+)", root_build)
if not m or not c:
    errors.append("version contract: could not parse AGP/Chaquopy versions")
else:
    agp = tuple(map(int, m.group(1).split(".")))
    chaq = tuple(map(int, c.group(1).split(".")))
    if chaq[:2] == (16, 0) and not ((8, 6) <= agp[:2] <= (8, 8)):
        errors.append(f"Chaquopy 16.0 / AGP {m.group(1)} compatibility mismatch")

# Mechanical Kotlin duplicate-declaration guard: catches the exact failure
# that would otherwise only appear late in the Gradle compilation phase.
activity = ACTIVITY.read_text(encoding="utf-8")
decls = re.findall(r"\b(?:val|var|private\s+lateinit\s+var)\s+(\w+)\s*(?::|=)", activity)
seen = set()
dupes = []
for name in decls:
    if name in seen:
        dupes.append(name)
    seen.add(name)
if dupes:
    errors.append("Kotlin duplicate declarations: " + ", ".join(sorted(set(dupes))))

# Python bridge must expose exactly one callable entry point.
bridge = BRIDGE.read_text(encoding="utf-8")
if bridge.count("def handle_command(") != 1:
    errors.append("Python bridge: expected exactly one handle_command definition")

# CI must run the audit before assembleDebug.
workflow = WORKFLOW.read_text(encoding="utf-8")
audit_pos = workflow.find("python audit_phone_agent.py")
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
print("Mechanical contracts checked: Gradle/Chaquopy, Python DSL/version, ABIs, manifest permission, Kotlin duplicate declarations, bridge entry point, CI audit ordering.")
