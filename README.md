# smali_tooling


Welcome to the smali_tooling wiki!

This tool is created to patch constructors of smali classes. A new class is added to the code tree, and every constructor of every class (depending on the file list that you provide) is patched to call a method that prints backtrace to logcat. This tool patches `static`/`public`/`protected`/`private` constructors. 

Take an APK, decompile it with APKtool into BASE_DIR:

```
apktool d some.apk -o BASE_DIR
```

Create a git repo in the BASE_DIR, and make a local commit, so that the script can revert to it after unsuccesful patching. You can skip resetting wyth `--skip-reset` argument.

Make `git.exe` accesible in your `%PATH%`.

Connect your phone with USB debugging enabled

Run `patch_ctors.py  -d BASE_DIR  -c smali_classes4/o  [-v] [-f list_of_smalis.txt]`

It will patch whatever it can find, and will run `build.bat`

`build.bat` will try to assemble the apk back, to sign it and install on the phone.

Don't forget to run `adb logcat | grep "KEKW"` before you start the app.

Have fun.