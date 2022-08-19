import re
from .mylogger import *

APKT_ERROR_re = re.compile(b"""\
I: Smaling (?P<dir>(smali(_classes[0-9]+)?)|(smali)) folder into (?P<nclasses>classes([0-9]+)?.dex)...\r
Exception in thread "main" org.jf.util.ExceptionWithContext: Exception occurred while writing code_item for method .+\r
([ -~]+\r\n)+\
Caused by: org.jf.util.ExceptionWithContext: Unsigned short value out of range: (?P<nmethods>[0-9]+)\
""", re.MULTILINE)

APKT_ERROR_smol_re = re.compile(b"""Caused by: org.jf.util.ExceptionWithContext: Unsigned short value out of range: (?P<nmethods>[0-9]+)""", re.MULTILINE)


PATCHED = "# PATCHED_LOL"

CTOR_PATCH = """
{patched}_START

    invoke-static {{}}, L{namespace}/{name};->printBacktrace()V

{patched}_END
""".format (patched=PATCHED, namespace=LOGGER_NAMESPACE, name=LOGGER_NAME)







SMALI_TYPE_PATTERN = "L[a-zA-Z0-9\$/]+;|[?[A-Z]" # better not change the order
SMALI_CTOR_MODIFIER = "(?P<modifier>public |static |protected |private |synthetic )?constructor"
SMALI_CTOR_NAME = "<(cl)?init>"

ctor_re   = re.compile ( f"""\
(^\.method {SMALI_CTOR_MODIFIER} {SMALI_CTOR_NAME}\((?P<args>({SMALI_TYPE_PATTERN})*)\)(?P<retval>{SMALI_TYPE_PATTERN})
    \.locals (?P<locals>[0-9]+)\
(?P<annotation>
    \.annotation .+
(?P<annotation_values>\
        value = {{\n((\
            .+,?\n)+)\
        }}
)?\
    .end annotation\
)?
)(?P<PATCH_ME_HERE>)\
(    [ -~]+[^ ]\n|\n)+\
.end method\
""", re.MULTILINE)

method_re   = re.compile ( f"""\
(^\.method {SMALI_CTOR_MODIFIER} {SMALI_CTOR_NAME}\((?P<args>({SMALI_TYPE_PATTERN})*)\)(?P<retval>{SMALI_TYPE_PATTERN})
    \.locals (?P<locals>[0-9]+)\
(?P<annotation>
    \.annotation .+
(?P<annotation_values>\
        value = {{\n((\
            .+,?\n)+)\
        }}
)?\
    .end annotation\
)?
)(?P<PATCH_ME_HERE>)\
(    [ -~]+[^ ]\n|\n)+\
.end method\
""", re.MULTILINE)


dir_meth_re = re.compile ("""\
^# direct methods
(?P<PATCH_ME_HERE>)\
""", re.MULTILINE)

CLASS_PATCH = """

{patched}_CLASS
.method static constructor <clinit>()V
    .locals 0

    invoke-static {{}}, L{namespace}/{name};->printBacktrace()V

    return-void
.end method
{patched}_CLASS_END

""".format (patched=PATCHED, namespace=LOGGER_NAMESPACE, name=LOGGER_NAME)
