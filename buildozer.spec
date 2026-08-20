[app]
title = Guard App
package.name = guardapp
package.domain = org.guard

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

version = 0.1

requirements = kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
