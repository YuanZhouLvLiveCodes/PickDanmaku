import os
import subprocess


def os_system(*args, **kwargs):
    os.system(*args, **kwargs)


def subprocess_run(*args, **kwargs):
    result = subprocess.run(*args, **kwargs, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode("gbk", errors="ignore"))
    print(result.stderr.decode("gbk", errors="ignore"))
