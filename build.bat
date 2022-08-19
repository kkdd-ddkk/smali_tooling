@echo off

if [%BASE_DIR%]==[] (
    if not exist "%~1" (
        echo please provide base directory as the first argument
        exit 1111
    )
    echo setting BASE_DIR to %1
    set BASE_DIR=%1

)


for  %%A in (apktool zipalign apksigner) do (
    WHERE /q %%A || ECHO Please make sure that %%A is in %%PATH%%  && exit /b 4444
)


if ["%DO_EXIT%"] NEQ [""] exit %EXITCODE%



:check_args_loop
	::-------------------------- has argument ?
	if ["%~1"]==[""] (
	@REM echo done.
	goto check_args_end
	)

	::-------------------------- argument exist ?

	if [%~1] == [/noinstall] set NO_INSTALL=yes
	if [%~1] == [/output] (
		set OUT_DIR=%2
		goto check_args_end_loop
	)

	::--------------------------
	:check_args_end_loop
	shift
	goto check_args_loop
:check_args_end

if [%OUT_DIR%] NEQ [] cd %OUT_DIR%



@REM echo [90mDeleting old files...[0m 


if exist %BASE_DIR%_aligned.apk      del %BASE_DIR%_aligned.apk
if exist %BASE_DIR%.apk              del %BASE_DIR%.apk
if exist %BASE_DIR%.apk.apktool_temp del %BASE_DIR%.apk.apktool_temp 

if exist %BASE_DIR%.apk 		     goto exists
if exist %BASE_DIR%_aligned.apk      goto exists
if exist %BASE_DIR%.apk.apktool_temp goto exists


goto ok

:exists

	exit
	echo [95mcould not delete old apks and temp files \o/[0m 
 
:ok


if not [%PACKAGE_NAME%]==[] (
    echo [90mTrying to uninstall old apk...[0m  1>&2

    for /f %%A in ('adb shell pm list packages  ^| grep %PACKAGE_NAME%') do (
        if [%%A] == [] (
            echo [90mUninstalling apk[0m
            adb uninstall %PACKAGE_NAME%
        )
))


                                                                           


echo [101;30m...Running apktool...[0m  1>&2

@REM ←[101;30m NORMAL BACKGROUND COLORS ←[0m

@echo on
echo k | call apktool b -f %BASE_DIR%  -o %BASE_DIR%.apk
@echo off


rem IF NOT EXIST %BASE_DIR%.apk (
IF ERRORLEVEL 1 (
	echo.
	echo [95mbuild.bat:: SADGE... Could not assemble the apk with apktool[0m
	exit 3333
)



echo [42;30mApktool successfully finished (^^_^^)[0m  1>&2

if NOT ["%NO_INSTALL%"] == [""]  (
	exit 0
)

echo [101;30mCalling zipalign...[0m  1>&2

ping 127.0.0.1 -n 2 > nul


zipalign  -p -f -v 4  %BASE_DIR%.apk   %BASE_DIR%_aligned.apk 


echo [101;30mSigning the aligned apk...[0m  1>&2

echo 123456| call apksigner sign --ks release.keystore  %BASE_DIR%_aligned.apk 

echo [101;30mInstalling the aligned and signed apk...[0m  1>&2


adb install -t %BASE_DIR%_aligned.apk



