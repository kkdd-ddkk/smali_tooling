# smali_tooling


Welcome to the smali_tooling wiki!

This tool is created to patch constructors of smali classes. A new class called `customlogger.BacktraceLogger` is added to the code tree, and every constructor of every class (depending on the file list that you provide) is patched to call a method that prints backtrace to logcat. This tool patches `static`/`public`/`protected`/`private` constructors. 

## What for?

If you want to see which classes in which order are created, or want to use Frida Gadget and don't know where to patch (again, aim for the most early loaded classes.

## How to use?

Take an APK, decompile it with APKtool into BASE_DIR:

```
apktool d -r some.apk -o BASE_DIR
```

-r is preferred, not to have a headache with compiling the resources back.

Create a git repo in the BASE_DIR, and make a local commit, so that the script can revert to it after unsuccesful patching. You can skip resetting with `--skip-reset` argument.

Make the following tools accesible in your `%PATH%`:
* git
* apktool
* zipalign
* apksigner


Connect your phone with USB debugging enabled

Run `patch_methods.py -d BASE_DIR  [-v] [-f list_of_smalis.txt]`

It will patch whatever it can find, and will run `build.bat`

`build.bat` will try to assemble the apk back, to sign it and install on the phone.

Don't forget to run `adb logcat | grep "KEKW"` before you start the app.

Example output would be:

```
08-19 19:34:32.299 26546 26546 D RLOGGER : STACKTRACE:customlogger.BacktraceLogger.printBacktrace(Unknown Source:73)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.fromStatus.<clinit>(Unknown Source:0)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.fromStatus.INotificationSideChannel$Default(Unknown Source:0)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.checkNull.<init>(:67)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.getViewForPopups.<clinit>(:3074)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.getViewForPopups.cancel(Unknown Source:0)
08-19 19:34:32.299 26546 26546 D RLOGGER :      o.KeepForSdkWithFieldsAndMethods.attachBaseContext(Unknown Source:27)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.Application.attach(Application.java:338)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.Instrumentation.newApplication(Instrumentation.java:1190)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.LoadedApk.makeApplication(LoadedApk.java:1356)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.ActivityThread.handleBindApplication(ActivityThread.java:6723)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.ActivityThread.access$1500(ActivityThread.java:256)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.ActivityThread$H.handleMessage(ActivityThread.java:2091)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.os.Handler.dispatchMessage(Handler.java:106)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.os.Looper.loopOnce(Looper.java:201)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.os.Looper.loop(Looper.java:288)
08-19 19:34:32.299 26546 26546 D RLOGGER :      android.app.ActivityThread.main(ActivityThread.java:7870)
08-19 19:34:32.299 26546 26546 D RLOGGER :      java.lang.reflect.Method.invoke(Native Method)
08-19 19:34:32.299 26546 26546 D RLOGGER :      com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:548)
08-19 19:34:32.299 26546 26546 D RLOGGER :      com.android.internal.os.ZygoteInit.main(ZygoteInit.java:1003)
08-19 19:34:32.299 26546 26546 D RLOGGER :
```


You can use `build.bat` separately to rebuild, zipalign, sign and install the APK.

Have fun.

