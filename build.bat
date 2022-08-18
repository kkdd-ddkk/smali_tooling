@echo off
set basename=base_apktool_dir
set appname=com.example.some.client
set ZIPALIGN=path/to/zipalign.exe
set APKSIGNER=path/to/apksigner.bat



:check_args_loop
	::-------------------------- has argument ?
	if ["%~1"]==[""] (
	echo done.
	goto check_args_end
	)

	::-------------------------- argument exist ?

	if [%~1] == [/noinstall] set NO_INSTALL=yes
	if [%~1] == [/output] (
		set OUTPUT=%2
		goto check_args_end_loop
	)

	::--------------------------
	:check_args_end_loop
	shift
	goto check_args_loop
:check_args_end

if not [%OUTPUT%] == [""] cd %OUTPUT%



@echo off
echo [90mDeleting old files...[0m 


if exist %basename%_aligned.apk      del %basename%_aligned.apk
if exist %basename%.apk              del %basename%.apk
if exist %basename%.apk.apktool_temp del %basename%.apk.apktool_temp 

if exist %basename%.apk 		     goto exists
if exist %basename%_aligned.apk      goto exists
if exist %basename%.apk.apktool_temp goto exists


goto ok

:exists

	exit
	echo [95mcould not delete old apks and temp files \o/[0m 
 
:ok


echo [90mTrying to uninstall old apk...[0m  1>&2


for /f %%A in ('adb shell pm list packages  ^| grep %appname%') do (
    if [%%A] == [] (
        echo [90mUninstalling apk[0m
		adb uninstall %appname%
    )
)


                                                                           


echo [101;30m...Running apktool...[0m  1>&2

@REM ←[101;30m NORMAL BACKGROUND COLORS ←[0m

echo k | call apktool b %basename%  -o %basename%.apk


rem IF NOT EXIST %basename%.apk (
IF ERRORLEVEL 1 (
	echo.
	echo [*] [95mbuild.bat:: SADGE... Could not assemble the apk with apktool[0m
	exit 1
)



echo [42;30mApktool successfully finished (^^_^^)[0m  1>&2

if NOT ["%NO_INSTALL%"] == [""]  (
	exit 0
)

echo [101;30mCalling zipalign...[0m  1>&2

ping 127.0.0.1 -n 2 > nul


%ZIPALIGN%  -p -f -v 4  %basename%.apk   %basename%_aligned.apk 


echo [101;30mSigning the aligned apk...[0m  1>&2

echo 123456| call %APKSIGNER% sign --ks release.keystore  %basename%_aligned.apk 

echo [101;30mInstalling the aligned and signed apk...[0m  1>&2


adb install -t %basename%_aligned.apk



