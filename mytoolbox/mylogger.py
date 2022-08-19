LOGGING_CLASS = """\
.class public static Lhenlofren/MyKek;
.super Ljava/lang/Object;

.method public static log_kek(Ljava/lang/String;)V
    .locals 1
    .param p0, "message"
    const-string v0, "KEK MYLOG"
    invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    return-void
.end method

.method public static printBacktrace()V
    .locals 2

    const-string v0, "KEKW"
    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/Thread;->getStackTrace()[Ljava/lang/StackTraceElement;
    move-result-object v1
    invoke-static {v1}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    return-void

.end method
"""