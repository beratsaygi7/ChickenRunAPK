[app]
title = Chicken Run
package.name = chickenrun
package.domain = org.obs
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,json,txt
version = 0.8.2
requirements = python3,pygame
orientation = landscape
fullscreen = 1
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.accept_sdk_license = True
android.entrypoint = org.renpy.android.PythonActivity
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
