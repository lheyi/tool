# This is a sample Python script.
import os
import sys
import re

origin = sys.stdout
global outlog_file


class ResItem:
    id: str = ...
    name: str = ...
    type: str = ...

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type


class DiffResItem:
    id_old: str = ...
    id_new: str = ...
    name: str = ...
    type: str = ...

    def __init__(self, type_name, name, id_old, id_new):
        self.type = type_name
        self.name = name
        self.id_old = id_old
        self.id_new = id_new


def parseRes(file_path):
    resMapping = {}
    with open(file_path) as file:
        content = file.read()
        file.close()
        types = content.split("  type ")
        for i in range(1, len(types)):
            t = types[i]
            type_name = t[0:t.index(" ")]
            # resource 0x7f010000 anim/abc_fade_in 解析格式
            rex = r"resource (0x[a-fA-F0-9]*) {}/([A-Za-z0-9_$.]*)".format(type_name)
            # log(type_name + ":")
            data = re.search(rex, t, flags=re.I)
            resItems = {}
            while data:
                # log("\t{}/{}:{}".format(type_name, data.group(2), data.group(1)))
                resItems[data.group(2)] = ResItem(data.group(1), data.group(2), type_name)
                group_str = data.group()
                t = t[t.index(group_str) + len(group_str):]
                data = re.search(rex, t)
            resMapping[type_name] = resItems
    return resMapping


def log(text: str, end="\n"):
        print(text, end=end)
        sys.stdout = outlog_file
        print(text, end=end)
        sys.stdout = origin


# 检查文件是否是R文件
def isRFile(content):
    #  .field public static final abc_action_bar_home_description:I
    rex = r".field public static final ([a-zA-Z0-9_]+):I"
    match = re.search(rex, content)
    return match is not None


def replaceSmali(file_path, diffMapping: dict):
    with open(file_path) as f:
        content = f.read()
        f.close()
        first_line = True
        rex = r"0x[0-9a-fA-F]{8,}"
        if re.search(rex, content) is None:
            # print("W:ignore this file [{}]".format(file_path))
            f.close()
            return  # 不用遍历了 直接结束
        # log("{} ".format(file_path))
        types = list(diffMapping.keys())
        lines = content.split("\n")
        line_replace = False
        for index in range(3, len(lines)):
            line = lines[index]
            if re.search(rex, line) is None:
                continue
            for type_key in types:
                if line_replace:
                    break
                diffItems = diffMapping[type_key]
                for diffItem in reversed(diffItems):
                    if line_replace:
                        break
                    if line.__contains__(diffItem.id_old):
                        if first_line:
                            first_line = False
                            log("{} ".format(file_path))
                        line = line.replace(diffItem.id_old, diffItem.id_new)
                        lines[index] = line
                        log(f"\t[{index + 1}] {diffItem.type}_{diffItem.name}: {diffItem.id_old} => {diffItem.id_new}")
                        line_replace = True
                        break
            line_replace = False
        content = "\n".join(lines)
    with open(file_path, mode="w") as f:
        f.write(content)
        f.flush()
        f.close()


def replaceAllSmali(file_path, diffMapping: dict):
    for file in os.listdir(file_path):
        path = os.path.join(file_path, file)
        if os.path.isdir(path):
            replaceAllSmali(path, diffMapping)
        else:
            if path.endswith(".smali"):
                replaceSmali(path, diffMapping)


def getSmaliDir(project_dir, dex_count):
    return project_dir + "/{}/".format(("smali_classes{}".format(dex_count)) if (dex_count > 1) else "smali")


def replaceResId(project_dir, diffMapping: dict):
    dex_count = 1
    smali_path = getSmaliDir(project_dir, dex_count)
    while os.path.exists(smali_path):
        log(">> start replace[{}]".format(smali_path))
        replaceAllSmali(smali_path, diffMapping)
        dex_count += 1
        smali_path = getSmaliDir(project_dir, dex_count)


def fixSmaliResID(resmas_old_, resmas_new_, apk_project_dir, out_path):
    global outlog_file
    outlog_file = open(os.path.join(out_path, 'diff.log'), 'w')
    
    project_dir = apk_project_dir
    resfile_new = resmas_new_
    resfile_old = resmas_old_

    resMapping1 = parseRes(resfile_new)
    resMapping2 = parseRes(resfile_old)

    diffMapping = {}
    types = list(resMapping1.keys())
    for type_name_key in reversed(types):
        diffItems = list()
        res1 = resMapping1[type_name_key]
        res2 = resMapping2[type_name_key]
        for name_key in res1.keys():
            if res2.__contains__(name_key):
                id_new_ = res1[name_key].id
                id_old_ = res2[name_key].id
                if id_new_ != id_old_:
                    log("diff => {}/{}".format(type_name_key, name_key))
                    diffItems.append(DiffResItem(type_name_key, name_key, id_old_, id_new_))
            else:
                log("W:waring: not found {}/{} !".format(type_name_key, name_key))
        if len(diffItems) > 0:
            diffMapping[type_name_key] = diffItems
    diff_len = len(diffMapping)
    log("\n>> diffRes count={}\n".format(diff_len))
    if diff_len > 0:
        replaceResId(project_dir, diffMapping)
        log("fix smali resId done.")
        return True
    else:
        log("no need to fix resource id !")
        return False


# if __name__ == '__main__':
#     # base_path = "D:\\反编译\\杨凯斌\\out"
#     base_path = "/mnt/d/反编译/杨凯斌/out"
#     apk_project_dir = f"{base_path}/apk_source"
#     resold = f"{base_path}/resmap_old.txt"
#     resnew = f"{base_path}/resmap_new.txt"
#     out_path = base_path
#
#     fixSmaliResID(resold, resnew, apk_project_dir, out_path)
