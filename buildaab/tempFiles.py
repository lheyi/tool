import tempfile
import os
import shutil
import random
import string


# class FileMapping:
#     tmp_path: str
#     real_name: str
#
#     def __init__(self, tmp_path, real_name):
#         self.tmp_path = tmp_path
#         self.real_name = real_name


def mkTempPath(base_dir='/tmp', prefix='', suffix=''):
    return tempfile.mkdtemp(prefix=prefix, dir=base_dir, suffix=suffix)


def removeTemp(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


# out
def mkTmpOutPath():
    return mkTempPath()


# apk_source
def mkTmpApkSourcePath(base_path):
    return mkTempPath(base_path)


# compiled_resources
def mkTmpCompiledResourcesPath(base_path):
    return mkTempPath(base_path)


# output_apk_data
def mkTmpOutputApkDataPath(base_path):
    return mkTempPath(base_path)


# base
def mkTmpAABBasePath(base_path):
    return mkTempPath(base_path)


def generate_file_name(min_len=5, max_len=12, suffix=""):
    # 合法的文件名字符集，包括字母、数字、下划线和破折号
    legal_chars = string.ascii_letters + string.digits + '_-'
    length = random.randint(min_len, max_len)
    return (''.join(random.choice(legal_chars) for _ in range(length))) + suffix


# if __name__ == '__main__':
    # 创建一个临时文件
    # dir_path = mkTempPath()
    # print(dir_path)
    # dir_path2 = mkTempPath(dir_path)
    # print(dir_path2)
    # removeTemp(dir_path)
    #
    # f = mkTmpOutPath()
    # print(f.tmp_path)
    # print(f.real_name)
    #
    # 生成长度为10的随机文件名
    # f = mkTmpOutPath()
    # base = mkTmpAABBasePath(f)
    # print(mkTmpAABBaseZipPath(base))