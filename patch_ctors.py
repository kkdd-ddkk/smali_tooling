import re
import  os 
import  sys
import random
import  string
import argparse
import itertools
import subprocess


btclass = """
.class public static Lo/MyKek;
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

PATCHED = "# PATCHED_LOL"

CTOR_PATCH = """
{patched}_START

    invoke-static {{}}, Lo/MyKek;->printBacktrace()V

{patched}_END
""".format (patched=PATCHED)

DLV_TYPE_PATTERN = "L[a-zA-Z\$/]+;|[?[A-Z]" # better not change the order
DLV_CTOR_MODIFIER = "(?P<modifier>public |static |protected |private )constructor"
DLV_CTOR_NAME = "<(cl)?init>"

ctor_re   = re.compile ( f"""\
(^\.method {DLV_CTOR_MODIFIER} {DLV_CTOR_NAME}\((?P<args>({DLV_TYPE_PATTERN})*)\)(?P<retval>{DLV_TYPE_PATTERN})
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


def _gray(s):
    return f"\x1b[90m{s}\x1b[0m"

def myexit():
    print("\x1b[101;93m   THIS IS  THE END   \x1b[0m")
    print("\x1b[101;93m   BEAUTIFUL FRIEND   \x1b[0m")

    exit()
    
def update_progress(percent):
    if args.verbose <= 0:
        return
    twidth = os.get_terminal_size().columns

    percent_f = "{:.2f}%".format(percent)
    msg = _gray(f"[*] working ({percent_f}) on {fname}")
    msg += ' ' * (twidth - len(msg))
    if args.verbose == 1:
        print (msg, end="\r", flush=True)
    else:
        print (msg)


def print_v (*argv):
    if args.verbose > 0:
        print(*argv)

def print_vv (*argv):
    if args.verbose > 1:
        print(*argv)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_uppercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def patch_file(fname):

    with open (f"{fname}", "r+") as smali:
        contents = smali.read()
        if re.search (PATCHED, contents, flags=re.MULTILINE):
            print_vv(_gray(f"[!] this file is already patched: {fname}"))
            return
        
        print_vv(_gray("[*] grepping for constructors..."))
        locations = list(ctor_re.finditer(contents))
        
        if len(locations) == 0:
            print_vv(_gray("[*] did not find any ctros"))
            return 


        parts = [0] + [m.span("PATCH_ME_HERE")[0] for m in locations] + [len(contents)]
        sliced_contents = [contents[parts[idx]:parts[idx+1]] for idx in range(len(parts)-1)]

        patches = []

        for m in locations:
            patches.append ( CTOR_PATCH ) 
            
            if args.verbose>=2:
                print_vv(_gray("[*]captured ctor body:"))
                print_vv("\x1b[36m")
                for key in m.groupdict(): print_vv ("\t{}{}: {}".format (key, m.span(key), m.groupdict()[key]))
                print_vv("\x1b[0m")
                print_vv(_gray("[*]appending the new patch" + ":" if args.verbose > 1 else ""))
                print_vv( f"\x1b[33m\"\"\"{CTOR_PATCH}\"\"\"\x1b[0m")


        patches.append ("") # needed for zipping, cuz sliced_contents and patches arrays should have amount of elements

        print_vv(_gray("[*] patching..."))
        new_contents = ''.join(itertools.chain.from_iterable(zip (sliced_contents, patches)))
        print_vv(_gray("[*] done, now writing to the file..."))

        smali.seek(0)
        smali.write(new_contents)
        smali.truncate()
        print_vv(_gray("[*] done! patch was applied"))

    return







if __name__== "__main__":

    import colorama
    colorama.init()
    
    # Example:
    # tool.py  -d apktool_result_directory  -f  file_list_to_patch.txt   -c smali_classes4/o

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--base-dir", required=True, help="base directory of 'apktool d' result (decompiled apk). Please create a git repo in that folder, so that I can rollback the patches.")
    parser.add_argument("-c", "--class-dir", required=True, help="relatively to the BASE_DIR, where should I put my logging class (better not contradict with Lo/MyKek namespace, so choose something like smali_classes4/o)")
    parser.add_argument("-f", "--file", help="file with list of files to patch. If not set, will patch all smalis, I don't care.")
    parser.add_argument("-n", "--no-install", action="store_true", help="no installation, only build")
    parser.add_argument(      "--skip-reset", action="store_true", help="skip git reset in the BASE_DIR")
    parser.add_argument("-v", "--verbose", action='count', default=0,  help="guess what, verbosity level")

    args = parser.parse_args()
    print_vv ("[*] Script arguments:\n{}".format(args))






    if not args.skip_reset:
        print("[*] starting git reset --hard...")
        try: subprocess.run(["git","reset", "--hard"], cwd=args.base_dir, stderr=sys.stderr, stdout=sys.stdout)
        except subprocess.CalledProcessError as e:
            print(r"[X] git reset failed \o/")
            myexit()
        print("[*] done!")







    print("[*] adding my class >:-)")
    with open ( f"{args.base_dir}/{args.class_dir}/MyKek.smali", "w") as myclass:     myclass.write(btclass)    
    print("[*] done!")





    print("[*] start patching...")

    file_list=""
    if not args.file:
        file_list = [os.path.join(dp, f).replace("\\","/") for dp, dn, filenames in os.walk(args.base_dir) for f in filenames if os.path.splitext(f)[1] == '.smali']

    else: 
        with open (args.file, "r") as flist: 
            file_list = flist.read().replace("\\","/").split('\n')
    
  

    nfiles = len(file_list)
    for idx, fname in enumerate(file_list):
       
        update_progress( idx * 100 / nfiles)

        patch_file(fname)
    print("[*] done patching!")







    print("[*] running build task...")
    try: subprocess.run([ "build.bat", "/noinstall" if args.no_install else "" ], cwd=".", stderr=sys.stderr, stdout=sys.stdout)
    except subprocess.CalledProcessError as e:
        print("[X] build task \x1b[96m\\o/\x1b[91mFAILED\x1b[96m\\o/\x1b[0m")
        myexit()
    print("[*] build task" +'\x1b[92m SUCCESSFULLY \x1b[0m' + "finished")



    myexit()
