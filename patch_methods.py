import re
import  os 
import  sys
import random
import  string
import argparse
import itertools
import subprocess
import mytoolbox as mtb




import pdb

def _gray(s):
    return f"\x1b[90m{s}\x1b[0m"

    
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



def patch_file(fname):

    with open (f"{fname}", "r+") as smali:
        contents = smali.read()
        if re.search (mtb.PATCHED, contents, flags=re.MULTILINE):
            print_vv (_gray(f"[!] this file is already patched: {fname}"))
            return
        
        print_vv(_gray("[*] grepping for constructors..."))
        ctor_locations = list(mtb.ctor_re.finditer(contents))
        
      

        sliced_contents = ""
        patches = []

        if len(ctor_locations) > 0:
                 
            parts = [0] + [loc.span("PATCH_ME_HERE")[0] for loc in ctor_locations] + [len(contents)]
            sliced_contents = [contents[parts[idx]:parts[idx+1]] for idx in range(len(parts)-1)]

            for m in ctor_locations:

                patches.append ( mtb.CTOR_PATCH ) 

                if args.verbose>=2:
                    print_vv(_gray("[*]captured ctor body:"))
                    print_vv("\x1b[36m")
                    for key in m.groupdict(): print_vv ("\t{}{}: {}".format (key, m.span(key), m.groupdict()[key]))
                    print_vv("\x1b[0m")
                    print_vv(_gray("[*]appending the new patch" + ":" if args.verbose > 1 else ""))
                    print_vv( f"\x1b[33m\"\"\"{mtb.CTOR_PATCH}\"\"\"\x1b[0m")

        else:
            m = mtb.dir_meth_re.search (contents)
            if m == None: return
            loc = m.span("PATCH_ME_HERE")[0
            ]

            sliced_contents = [contents[:loc],  contents[loc:]]
            patches.append (mtb.CLASS_PATCH)


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
    # tool.py  -d apktool_result_directory  -f  file_list_to_patch.txt  

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--base-dir", required=True, help="base directory of 'apktool d' result (decompiled apk). Please create a git repo in that folder, so that I can rollback the patches.")
    parser.add_argument("-f", "--file", help="file with list of files to patch. If not set, will patch all smali files in BASE_DIR, I don't care.")
    parser.add_argument("-n", "--no-install", action="store_true", help="no installation, only build")
    parser.add_argument(      "--skip-reset", action="store_true", help="skip git reset in the BASE_DIR")
    parser.add_argument("-v", "--verbose", action='count', default=0,  help="guess what, verbosity level")
    parser.add_argument("-m", "--methods", choices =('ctors', 'add_ctors', 'all', ), default='ctors', help="TODO")
    parser.add_argument("--skip-patching", action="store_true", help="skip patching ")

    args = parser.parse_args()
    print_v ("[*] Script arguments: {}".format(args))

    if not args.skip_reset:
        print("[*] starting git reset --hard && git clean -df...")
        try:
            subprocess.run(["git","reset", "--hard"], cwd=args.base_dir, stderr=sys.stderr, stdout=sys.stdout)
            subprocess.run(["git","clean", "-df"], cwd=args.base_dir, stderr=sys.stderr, stdout=sys.stdout)
        except subprocess.CalledProcessError as e:
            print(r"[X] git reset failed \o/")
            mtb.myexit()
        print("[*] done!")




    if not args.skip_patching:

        print("[*] adding my class >:-) into ", end="")

        with mtb.chdir (args.base_dir) as _:

            ndexes = len([smalidir \
                        for root, dirs, files in os.walk(".")        \
                        for smalidir in dirs if "smali_classes" in smalidir or "smali" == smalidir  \
            ])

            lastdir = f'smali_classes{ndexes}' if ndexes > 1 else "smali"
            namespace = "henlofren"
            namespacedir = f"{lastdir}/{namespace}"
            if not os.path.exists(namespacedir): os.makedirs(namespacedir)

            print (f"\x1b[33m{namespacedir}/MyKek.smali\x1b[0m")
            with open ( f"{namespacedir}/MyKek.smali", "w") as myclass:     myclass.write(mtb.LOGGING_CLASS)    
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

    else: 
        print("[*] skipped patching")
            









    print("[*] starting build task...")
    
    try: 
        args = [ "build.bat", args.base_dir,"/noinstall" if args.no_install else "", "/output out" ]
        print ("[*] args: "+ str(args))
        cmd = subprocess.Popen(args, cwd=".", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout = b""
        for b in cmd.stdout:
        
            pretty = ">\t" + b.decode("utf-8").rstrip()
            print  (pretty)
            stdout += b
        
        cmd.wait()
        
        print("\n[*] The task finished, analyzing  output...")

        if cmd.returncode != 0:
            # msg = "Error occured, the task returned {}\nOUTPUT:\n{}".format ( cmd.returncode,  pretty_output)
            msg = "[!] Error occured, the task returned {}".format ( cmd.returncode)

            if mtb.APKT_ERROR_smol_re.search( stdout ):
                msg+= """
[!] "\x1b[33mUnsigned short value out of range:...\x1b[0m" error was detected.
[!] Please move some classes from the overcrowded folder into a new 
[!] smali_classesN folder to reduce the number of methods per DEX file. 
[!] Please look in the output to find which dex file was compiling.
[!] Then please  rerun the tool with --skip-patch and --skip-reset arguments
"""
            raise mtb.BuildFailedError(msg)
   

        print("[*] build task" +'\x1b[92m SUCCESSFULLY \x1b[0m' + "finished")
        
        
    except (mtb.BuildFailedError, subprocess.CalledProcessError) as e:
        print (e)
        mtb.myexit()


       




    mtb.myexit()
