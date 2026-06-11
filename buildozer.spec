[app]

title = MOON Fitness
package.name = moonfitness
package.domain = com.moon.fitness

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,db,ttf,otf
source.include_patterns = assets/*,assets/fonts/*

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi,plyer

orientation = portrait
fullscreen = 0

android.permissions = VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.ndk = 25b

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True
android.accept_sdk_license = True
android.enable_androidx = True

android.release_artifact = apk
android.debug_artifact = apk

p4a.bootstrap = sdl2

log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
