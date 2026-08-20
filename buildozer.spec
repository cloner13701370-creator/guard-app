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

android.api = 36
android.minapi = 21

android.ndk = 29

android.archs = armeabi-v7a, arm64-v8a

p4a.branch = develop

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
