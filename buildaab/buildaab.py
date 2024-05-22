import os
import shutil
import subprocess
import sys
import platform

import smaliResIdUtil
import tempFiles

# 请根据自己电脑系统环境配置相应的路径 (推荐Macos或Linux;不建议Windows环境,因为环境很蛋疼!)

aapt2: str = ...
bundletool: str = ...
android_jar_path: str = ...
apktool: str = ...
defaultPwd: str = ...


def isLinux():
    return platform.system().lower() == 'linux'


def loadEnv():
    envMap = dict()
    # path = "D:\\CodeSource\\buildaab\\dist"
    # if isLinux():
    path = os.path.realpath(os.path.join(sys.executable, "../"))
    LinuxPath = "/root/Desktop/tool/buildaab/dist/"
    with open(os.path.join(LinuxPath, "project.config")) as f:
        for l in f.readlines():
            l = l.replace("\n", "")
            kvs = l.split("=")
            envMap[kvs[0]] = kvs[1]
        f.close()
    global aapt2
    global bundletool
    global android_jar_path
    global apktool
    global defaultPwd
    aapt2 = envMap['aapt2']
    bundletool = envMap['bundletool']
    android_jar_path = envMap['android']
    apktool = envMap['apktool']
    if envMap.__contains__('pwd'):
        defaultPwd = envMap['pwd']
    else:
        defaultPwd = "123456"


class ApkVersionInfo:
    minSdkVersion: str = None
    targetSdkVersion: str = None
    versionCode: str = None
    versionName: str = None

    def isOk(self):
        return self.minSdkVersion is not None \
               and self.targetSdkVersion is not None \
               and self.versionCode is not None \
               and self.versionName is not None


def getApkVersionInfo(apktool_yml_path):
    if os.path.exists(apktool_yml_path) is False:
        return None
    versionInfo = ApkVersionInfo()
    with open(apktool_yml_path) as f:
        content = f.read()
        groups = content.split("\n")
        for item in groups:
            if versionInfo.isOk():
                break
            if item.__contains__("minSdkVersion"):
                kv = item.strip().split(":")
                versionInfo.minSdkVersion = kv[1].strip().replace("'", "")
                continue
            if item.__contains__("targetSdkVersion"):
                kv = item.strip().split(":")
                versionInfo.targetSdkVersion = kv[1].strip().replace("'", "")
                continue
            if item.__contains__("versionCode"):
                kv = item.strip().split(":")
                versionInfo.versionCode = kv[1].strip().replace("'", "")
                continue
            if item.__contains__("versionName"):
                kv = item.strip().split(":")
                versionInfo.versionName = kv[1].strip().replace("'", "")
        f.close()
    return versionInfo


def fixVersionInfo(apk_source_dir):
    apktool_yml_path = os.path.join(apk_source_dir, "apktool.yml")
    manifest_path = os.path.join(apk_source_dir, "AndroidManifest.xml")

    versionInfo = getApkVersionInfo(apktool_yml_path)
    if versionInfo:
        import xml.etree.ElementTree as ET

        uri = "http://schemas.android.com/apk/res/android"
        namespace = "{http://schemas.android.com/apk/res/android}"
        ET.register_namespace("android", uri)

        doc = ET.parse(manifest_path)
        manifestElement = doc.getroot()
        manifestElement.set(namespace + 'versionName', versionInfo.versionName)
        manifestElement.set(namespace + 'versionCode', versionInfo.versionCode)

        usesSdkElement = manifestElement.find("uses-sdk")
        if usesSdkElement is None:
            usesSdkElement = ET.SubElement(manifestElement, "uses-sdk")
            usesSdkElement.set(namespace + 'minSdkVersion', versionInfo.minSdkVersion)
            usesSdkElement.set(namespace + 'targetSdkVersion', versionInfo.targetSdkVersion)
        tree = ET.ElementTree(manifestElement)
        tree.write(manifest_path, encoding="utf-8")
        print("fix AndroidManifest.xml success.")
    else:
        print("ApkVersionInfo is None !")


# noinspection PyShadowingNames
def showAbout():
    highLightStart = "\033[1;32;40m"
    highLightEnd = "\033[0m"
    print("\n @Conykais")
    print(" \033[4;40;40m838437017@qq.com\033[0m")
    print(" Version {}buildaab-v2.7.3{} 2023-9-14\n".format(highLightStart, highLightEnd))


def argKeyValue(k, v):
    return f"{getGreenText(f'{k}=')}{getRedText(f'{v}')}"


"""
这里主要是描述各个工具使用说明,实际是不公开给使用者的，
至于为什么写这个？因为记性不好呀，当想不起来的时候 就用buildaab --readme 快速找到使用说明 OK？
"""


def showReadme():

    print(f"""\n  export aab:
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('build-bundle')} {argKeyValue('--modules', 'base.zip')} {argKeyValue('--output', 'base.aab')}""")

    print(f"""\n  aab sign:
        {getPurpleText('JarSigner')} {getGreenText('-verbose')} \\
        {getGreenText('keystore')} {getRedText('test.keystore')} \\
        {getGreenText('-storepass')} {getRedText(defaultPwd)} \\
        {getGreenText('-keypass')} {getRedText(defaultPwd)} \\
        {getGreenText('-digestalg SHA-256')} \\
        {getGreenText('-sigalg SHA256withRSA')} \\
        {getGreenText('-signedjar')} \\
        {getRedText('base_sign.aab')} \\
        {getRedText('base.aab')} \\
        {getRedText('test')}""")

    print(f"""\n  export apks(unsigned): 
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('build-apks')} \\
        {argKeyValue('--bundle', 'base.aab')} \\
        {argKeyValue('--output', 'app.apks')}""")

    print(f"""\n  export apks(signed): 
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('build-apks')} \\
        {argKeyValue('--bundle', 'base_sign.aab')} \\
        {argKeyValue('--output', 'app.apks')} \\ 
        {argKeyValue('--ks', 'test.keystore')} \\
        {argKeyValue('--ks-pass', f'pass:{defaultPwd}')} \\
        {argKeyValue('--ks-key-alias', 'test')} \\
        {argKeyValue('--key-pass', f'pass:{defaultPwd}')}""")

    print(f"""\n  install apks:
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('install-apks')} {argKeyValue('--apks', 'app.apks')}""")

    print(f"""\n  export device config:
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('get-device-spec')} {argKeyValue('--output', 'device.json')}""")

    print(f"""\n  export apks by device info(signed): 
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('build-apks')} \\
        {argKeyValue('--device-spec', 'device.json')} \\
        {argKeyValue('--bundle', 'base_sign.aab')} \\
        {argKeyValue('--output', 'app.apks')} \\ 
        {argKeyValue('--ks', 'test.keystore')} \\
        {argKeyValue('--ks-pass', f'pass:{defaultPwd}')} \\
        {argKeyValue('--ks-key-alias', 'test')} \\
        {argKeyValue('--key-pass', f'pass:{defaultPwd}')}""")

    print(f"""\n  compile res:
        {getGreenText(aapt2)} {getPurpleText('compile')} {getGreenText('--dir')} {getRedText('res/')} {getGreenText('-o')} {getRedText('compiled_resources/')} {getGreenText('--no-crunch')}""")

    print(f"""\n  dump config:
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('dump')} {getRedText('config')} {getGreenText('--bundle')} {getRedText('app.aab')}""")

    print(f"""\n  export universal apks:
        {getGreenText(f'java -jar {bundletool}')} {getPurpleText('build-apks')} \\
        {getGreenText('--mode=')}{getRedText('universal')} \\
        {getGreenText('--bundle=')}{getRedText('app.aab')} \\
        {getGreenText('--output=')}{getRedText('app.apks')}""")

    print(f"""\n  link res:
        {getGreenText(aapt2)} {getPurpleText('link')} {getGreenText('--proto-format')} \\
        {getGreenText('-o')} {getRedText('output.apk')} \\
        {getGreenText('-I')} {getRedText('android_jar_path')} \\
        {getGreenText('--manifest')} {getRedText('your_path/AndroidManifest.xml')} \\
        {getGreenText('-R')} {getRedText('your_path/compiled_resources/*.flat')} \\
        {getGreenText('--version-code')} {getRedText('1')} \\
        {getGreenText('--version-name')} {getRedText('v1.0')} \\
        {getGreenText('--output-text-symbols')} {getRedText('your_path/R.txt')} \\
        {getGreenText('--min-sdk-version')} {getRedText('21')} \\
        {getGreenText('--target-sdk-version')} {getRedText('30')} \\
        {getGreenText('--stable-ids')} {getRedText('your_path/public.txt')} \\
        {getGreenText('--auto-add-overlay')} \\
        {getGreenText('--no-auto-version')} \\
        {getGreenText('--no-resource-deduping')}""")


def printIllegalParameter(argv):
    ars = ""
    if type(argv) == list:
        for i in range(0, len(argv)):
            ars += "{} ".format(argv[i])
    else:
        ars += "{} ".format(argv)
    print(" illegal parameter : \033[1;31;40m {}\033[0m".format(ars))
    sys.exit(0)


def verifyArg(value, argv):
    if value == "" or value is None:
        printIllegalParameter(argv)


def obtainArgs(args):
    if args.lower().__contains__("=") is False:
        printIllegalParameter(args)
    else:
        return args.split("=")[1]


def obtainParams(arg):
    if arg.lower().__contains__("=") is False:
        printIllegalParameter(arg)
    else:
        arr = arg.split("=")
        return arr[0], arr[1]


def parseParams(args: list, emptyValue: dict = None):
    params = dict()
    for i in range(0, len(args)):
        if emptyValue and emptyValue.__contains__(args[i]):
            params[args[i]] = emptyValue[args[i]]
            continue
        name, value = obtainParams(args[i])
        params[name] = value
    return params


def checkFile(filePath, existsFile=True):
    filePath = getAbsPath(os.getcwd(), filePath)
    if existsFile:
        if os.path.exists(filePath) is False:
            print(f"\n not found \033[1;31;40m{filePath}\033[0m !\n")
            sys.exit(0)
    else:
        if os.path.exists(filePath):
            print(f"\n \033[1;31;40m{filePath}\033[0m already exists !! \n")
            sys.exit(0)


def getParam(params, name, defaultValue, isCheckFile=False, existsFile=True):
    result = defaultValue
    if params.__contains__(name):
        result = params[name]
    if isCheckFile and result is not None:
        if result.startswith("/"):
            checkFile(result, existsFile)
        else:
            result = getAbsPath(os.getcwd(), result)
            checkFile(result, existsFile)
    return result


def execCmd(cmd):
    print(f"\n{cmd}\n")
    print(os.popen(cmd).read())


def replaceBasename(path, name):
    return path.replace(os.path.basename(path), name)


def compiledRes(resPath, compiledPath):
    if os.path.exists(compiledPath):
        execCmd("rm -rf {}".format(compiledPath))
    os.makedirs(compiledPath)
    execCmd(f"{aapt2} compile --dir {resPath} --legacy -o {compiledPath} --no-crunch ")


def exportZIP(basePath, zipFile):
    cmd = f"cd {basePath} && zip -r {zipFile} ./ -x \"*.DS_Store\""
    execCmd(cmd)


def exportAAB(zipFile, aabFile, pbConfig):
    cmd = f"java -jar {bundletool} build-bundle --modules={zipFile} --output={aabFile} --config={pbConfig}"
    execCmd(cmd)


def exportApks():
    signPwd = defaultPwd
    params = dict()
    for i in range(2, len(sys.argv)):
        name, value = obtainParams(sys.argv[i])
        params[name] = value
    device_json = "device.json"
    if params.__contains__("--device"):
        device_json = params['--device']
    device_json = getAbsPath(os.getcwd(), device_json)
    checkFile(device_json)

    name = "test"
    signName = f"{name}.keystore"
    if params.__contains__('--sign'):
        signName = params['--sign']
        signName = getAbsPath(os.getcwd(), signName)
        checkFile(signName)
        if params.__contains__('--pwd'):
            signPwd = params['--pwd']

    if signName.__contains__("/"):
        arr = signName.split("/")
        alias = arr[-1].split(".")[0]
    else:
        alias = signName.split(".")[0]

    name = "base"
    aabFile = f"{name}.aab"
    if params.__contains__('--input'):
        aabFile = params['--input']
        aabFile = getAbsPath(os.getcwd(), aabFile)
        name = aabFile.split("/")[-1].split(".")[0]
        checkFile(aabFile)

    apksFile = f"{name}.apks"
    if params.__contains__('--output'):
        apksFile = params['--output']
        if os.path.exists(apksFile):
            print(f"\n \033[1;31;40m{apksFile}\033[0m already exists !! \n")
            sys.exit(0)
    cmd = f"java -jar {bundletool} build-apks \
        --device-spec={device_json} \
        --bundle={aabFile} \
        --output={apksFile} \
        --ks={signName} \
        --ks-pass=pass:{signPwd} \
        --ks-key-alias={alias} \
        --key-pass=pass:{signPwd}"
    execCmd(cmd)


def installApks(apksPath):
    cmd = f"java -jar {bundletool} install-apks --apks={apksPath}"
    execCmd(cmd)


def getDeviceJson(jsonPath):
    cmd = f"java -jar {bundletool} get-device-spec --output={jsonPath}"
    execCmd(cmd)


def signAAB(aab, aabSigned, signName, signPwd, alias):
    signTemple = """JarSigner -verbose \\
        -keystore {} \\
        -storepass {} \\
        -keypass {} \\
        -digestalg SHA-256 \\
        -sigalg SHA256withRSA \\
        -signedjar \\
        {} \\
        {} \\
        {}"""
    cmd = signTemple.format(signName, signPwd, signPwd, aabSigned, aab, alias)
    execCmd(cmd)


def linkRes(versionInfo: ApkVersionInfo, compiled_resources, manifest, output, stableIds=None):
    symbols_dir = os.path.join(os.path.dirname(output), "R.txt")
    stableIds = f' --stable-ids {stableIds}' if (stableIds is not None) else ''
    cmd = f"""{aapt2} link --proto-format \
        -o {output} \
        -I {android_jar_path} \
        --manifest {manifest} \
        -R {compiled_resources}/*.flat \
        --auto-add-overlay \
        --no-auto-version \
        --version-code {versionInfo.versionCode} \
        --version-name {versionInfo.versionName} \
        --no-resource-deduping \
        --output-text-symbols {symbols_dir} \
        --min-sdk-version {versionInfo.minSdkVersion} \
        --target-sdk-version {versionInfo.targetSdkVersion} {stableIds}"""
    execCmd(cmd)


def getGreenText(text: str):
    greenHighLightStart = "\033[1;32;40m"
    highLightEnd = "\033[0m"
    return f"{greenHighLightStart}{text}{highLightEnd}"


def getRedText(text: str):
    redHighLightStart2 = "\033[1;31;40m"
    highLightEnd = "\033[0m"
    return f"{redHighLightStart2}{text}{highLightEnd}"


def getPurpleText(text: str):
    purpleHighLightStart2 = "\033[1;35;40m"
    highLightEnd = "\033[0m"
    return f"{purpleHighLightStart2}{text}{highLightEnd}"


# noinspection PyShadowingNames
def showHelp():

    print("apk convert aab:")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {getPurpleText('--stable-ids')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {argKeyValue('--output','test_aab/')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {getPurpleText('--stable-ids')} {argKeyValue('--output','test_aab/')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {argKeyValue('--sign','test.keystore')} {argKeyValue('--pwd',f'{defaultPwd}')} {argKeyValue('--output','test_aab/')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {getPurpleText('--stable-ids')} {argKeyValue('--sign','test.keystore')} {argKeyValue('--pwd',f'{defaultPwd}')} {argKeyValue('--output','test_aab/')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {argKeyValue('--sign','test.keystore')} {argKeyValue('--pwd',f'{defaultPwd}')} {argKeyValue('--output','test_aab/')} {argKeyValue('--config','config.json')}")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('test.apk')} {getPurpleText('--stable-ids')} {argKeyValue('--sign', 'test.keystore')} {argKeyValue('--pwd', f'{defaultPwd}')} {argKeyValue('--output', 'test_aab/')} {argKeyValue('--config', 'config.json')}")

    print("\n compile res:")
    print(f"\t{getGreenText('buildaab')} {getPurpleText('--compile-res')} {getGreenText('--legacy')} {argKeyValue('--input','res/')} {argKeyValue('--output','compiled_resources/')}")

    #  buildaab --link-res --manifest=AndroidManifest.xml --res=compiled_resources/ --output=output.apk
    print("\n link res:")
    common_cmd = f"\t{getGreenText('buildaab')} {getPurpleText('--link-res')} {argKeyValue('--manifest','AndroidManifest.xml')} {argKeyValue('--res','compiled_resources/')} {argKeyValue('--output','output.apk')} " \
                 f"{argKeyValue('--minSdk','21')} {argKeyValue('--targetSdk','30')} " \
                 f"{argKeyValue('--versionCode','1')} {argKeyValue('--versionName','1.0')}"
    print("\n" + common_cmd + "\n")
    common_cmd += f" {argKeyValue('--stable-ids','public.txt')}"
    print(common_cmd + "\n")

    print("\n export zip:")
    print(f"\t{getGreenText('buildaab')} {getPurpleText('--export-zip')} {argKeyValue('--input','base/')} {argKeyValue('--output','base.zip')}")

    # buildaab --sign-aab --sign=xxxx.keystore --pwd=123456 --input=base.aab --output=base_signed.aab
    print("\n sign aab:")
    print(f"\t{getGreenText('buildaab')} {getPurpleText('--sign-aab')} {argKeyValue('--sign','test.keystore')} {argKeyValue('--pwd',f'{defaultPwd}')} {argKeyValue('--input','base.aab')} {argKeyValue('--output','base_signed.aab')}")

    print("\n export aab:")
    print(f"\t{getGreenText('buildaab')} {getPurpleText('--export-aab')} {argKeyValue('--input','base.zip')} {argKeyValue('--output','base.aab')} {argKeyValue('--config','config.json')}")

    # buildaab --export-apks --input=xxxx_signed.aab --sign=test.keystore --pwd=123456 --device=device.json --output=xxxx.apks
    print("\n export apks:")
    print(f"\t{getGreenText('buildaab')} "
          f"{getPurpleText('--export-apks')} "
          f"{argKeyValue('--input','base.aab')} "
          f"{argKeyValue('--sign','test.keystore')} "
          f"{argKeyValue('--pwd',f'{defaultPwd}')} "
          f"{argKeyValue('--device','device.json')} "
          f"{argKeyValue('--output','app.apks')}")

    # buildaab --get-device=mate30-pro.json
    print("\n get device json:")
    print(f"\n\t{getGreenText('buildaab')} {getPurpleText('--get-device')}")
    print(f"\n\t{getGreenText('buildaab')} {argKeyValue('--get-device','mate30-pro.json')}")

    # buildaab --install-apks=app.apks
    print("\n install apks:")
    print(f"\t{getGreenText('buildaab')} {argKeyValue('--install-apks','app.apks')}\n")

    # buildaab --dump-config --input=app.aab --output=config.json
    print("\n dump config:")
    print(f"\t{getGreenText('buildaab')} "
          f"{getPurpleText('--dump-config')} "
          f"{argKeyValue('--input', 'app.aab')} "
          f"{argKeyValue('--output', 'config.json')}\n")


def getPBConfig(params):
    pbConfig = os.path.join(os.path.realpath(os.path.join(sys.executable, "../")), "config.json")
    return getParam(params, '--config', pbConfig, True, True)


def processAAB(apkPath, signName=None, signPwd=f"{defaultPwd}", outDir="out",
               pbConfig=os.path.join(os.path.realpath(os.path.join(sys.executable, "../")), "config.json"), stableIds=False):

    highLightStart = "\033[1;32;40m"
    highLightEnd = "\033[0m"

    if apkPath.lower().endswith(".apk") is False:
        print(" brothers ? please enter the file path where the suffix is {}apk{} !"
              .format(highLightStart, highLightEnd))
        sys.exit(0)

    apk_path = apkPath
    context_path = os.getcwd()
    print("context_path: {}".format(context_path))

    if os.path.exists(os.path.join(context_path, apk_path)) is False:
        print(" {} This file is not found, Please enter the correct apk path !"
              .format(os.path.realpath(os.path.join(context_path, apk_path))))
        sys.exit(0)

    real_apk_path = os.path.realpath(os.path.join(context_path, apk_path))
    print("apk_path: {}".format(real_apk_path))

    result_out_path = getAbsPath(context_path, outDir)

    out_path = tempFiles.mkTmpOutPath()

    print("temp_out: {}".format(out_path))
    resmap_old_path = os.path.join(out_path, "resmap_old.txt")
    print("\n{} dump resources {} > {}".format(aapt2, real_apk_path, resmap_old_path))
    subprocess.call([aapt2, "dump", "resources", real_apk_path], stdout=open(resmap_old_path, mode="w"))

    apk_source = tempFiles.mkTmpApkSourcePath(out_path)

    print("\n{} d {}-f {} -o {}".format(apktool, '-s ' if stableIds else '', real_apk_path, apk_source))
    if stableIds:
        # 不解包dex文件
        subprocess.call([apktool, "d", "-f", real_apk_path, '-s', "-o", apk_source])
    else:
        # 会解包dex
        subprocess.call([apktool, "d", "-f", real_apk_path, "-o", apk_source])
    # 把 public.xml放到其他地方(因为appt2编译资源的时候不需要这个文件)
    public_xml_path = os.path.join(apk_source, "res/values/public.xml")
    out_path_public_xml = os.path.join(out_path, "public_old.xml")
    shutil.move(public_xml_path, out_path_public_xml)

    res_path = os.path.join(apk_source, "res")
    compiled_resources_dir = tempFiles.mkTmpCompiledResourcesPath(out_path)
    compiledRes(res_path, compiled_resources_dir)

    output_apk = os.path.join(out_path, tempFiles.generate_file_name(6, 10, ".apk"))
    android_manifest_path = os.path.join(apk_source, "AndroidManifest.xml")
    # flat_files = compiled_resources_dir + "/*.flat"

    # fixVersionInfo(apk_source)
    versionInfo = getApkVersionInfo(os.path.join(apk_source, "apktool.yml"))

    if stableIds:
        import xml.etree.ElementTree as ET
        tree = ET.parse(android_manifest_path)
        root = tree.getroot()
        apk_packageId = root.attrib['package']
        tree = ET.parse(out_path_public_xml)
        root = tree.getroot()
        s = []
        for i in root:
            x_type = i.attrib["type"]
            x_name = i.attrib["name"]
            x_id = i.attrib["id"]
            s.append(f"{apk_packageId}:{x_type}/{x_name} = {x_id}\n")
        public_txt_path = os.path.join(out_path, "public.txt")
        f = open(public_txt_path, mode='w')
        f.write(("".join(s)))
        f.close()
        linkRes(versionInfo, compiled_resources_dir, android_manifest_path, output_apk, stableIds=public_txt_path)
    else:
        linkRes(versionInfo, compiled_resources_dir, android_manifest_path, output_apk)

    resmap_new_path = os.path.join(out_path, "resmap_new.txt")
    print("\n{} dump resources {} > {}\n".format(aapt2, output_apk, resmap_new_path))
    subprocess.call([aapt2, "dump", "resources", output_apk], stdout=open(resmap_new_path, mode="w"))
    if stableIds is False:
        smaliResIdUtil.fixSmaliResID(resmap_old_path, resmap_new_path, apk_source, out_path)
        # 新编排的资源id映射表
        newResMapping = smaliResIdUtil.parseRes(resmap_new_path)
        content = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<resources>\n"
        for resType in newResMapping.items():
            for res in resType[1].values():
                content += f"    <public type=\"{res.type}\" name=\"{res.name}\" id=\"{res.id}\" />\n"
        content += "</resources>"
        f = open(public_xml_path, "w")
        f.write(content)
        f.flush()
        f.close()
        # 重新打包apk 以后续获得已修复资源id的classes.dex
        print("\n{} b -f {}".format(apktool, apk_source))
        subprocess.call([apktool, "b", "-f", apk_source])

    # 解包 output.apk (里面存放着新编译好的资源.pb)
    output_apk_unzip_data = tempFiles.mkTmpOutputApkDataPath(out_path)
    print("unzip -d {} {}".format(output_apk_unzip_data, output_apk))
    subprocess.call(["unzip", "-d", output_apk_unzip_data, output_apk])
    # 解压后的文件就这些
    output_apk_data_resources_pb = os.path.join(output_apk_unzip_data, "resources.pb")
    output_apk_data_manifest = os.path.join(output_apk_unzip_data, "AndroidManifest.xml")
    output_apk_data_res = os.path.join(output_apk_unzip_data, "res/")
    # 为生成base.zip 做准备
    base_data_dir = tempFiles.mkTmpAABBasePath(out_path)
    if os.path.exists(base_data_dir):
        shutil.rmtree(base_data_dir)
    os.mkdir(base_data_dir)
    # base目录的一级目录结构如下
    # .
    # ├── assets
    # ├── dex
    # ├── lib
    # ├── manifest
    # ├── res
    # ├── resources.pb
    # └── root
    base_root = os.path.join(base_data_dir, "root/")
    base_dex_dir = os.path.join(base_data_dir, "dex/")
    base_manifest_dir = os.path.join(base_data_dir, "manifest/")

    base_lib_dir = os.path.join(base_data_dir, "lib/")
    base_assets_dir = os.path.join(base_data_dir, "assets/")
    base_res_dir = os.path.join(base_data_dir, "res/")
    base_res_pb = os.path.join(base_data_dir, "resources.pb")

    if os.path.exists(base_root):
        shutil.rmtree(base_root)
    os.mkdir(base_root)

    if os.path.exists(base_dex_dir):
        shutil.rmtree(base_dex_dir)
    os.mkdir(base_dex_dir)

    if os.path.exists(base_manifest_dir):
        shutil.rmtree(base_manifest_dir)
    os.mkdir(base_manifest_dir)

    # 复制output.apk解压的东西到 base/对应目录
    shutil.copy(output_apk_data_resources_pb, base_res_pb)
    shutil.copy(output_apk_data_manifest, os.path.join(base_manifest_dir, "AndroidManifest.xml"))
    shutil.move(output_apk_data_res, base_res_dir)

    # 复制apk_source中的lib,assets,kotlin,unknown,build/apk/classes.dex.... 到base/对应目录
    dex_dir = apk_source if stableIds else os.path.join(apk_source, "build/apk/")
    # 如果有就复制  -> base/lib
    apk_source_build_apk_lib = os.path.join(apk_source, "lib/")
    # 如果有就复制 -> base/root/kotlin
    apk_source_build_apk_kotlin = os.path.join(apk_source, "kotlin/")
    apk_source_build_apk_meta_inf = os.path.join(apk_source, "original/META-INF")

    if os.path.exists(apk_source_build_apk_lib):
        shutil.move(apk_source_build_apk_lib, base_lib_dir)

    if os.path.exists(apk_source_build_apk_kotlin):
        shutil.move(apk_source_build_apk_kotlin, os.path.join(base_root, "kotlin/"))

    if os.path.exists(apk_source_build_apk_meta_inf):
        for file in os.listdir(apk_source_build_apk_meta_inf):
            if file.upper().endswith("RSA"):
                os.remove(os.path.join(apk_source_build_apk_meta_inf, file))
                continue
            if file.upper().endswith("SF"):
                os.remove(os.path.join(apk_source_build_apk_meta_inf, file))
                continue
            if file.upper().endswith("MF"):
                os.remove(os.path.join(apk_source_build_apk_meta_inf, file))
                continue
        shutil.move(apk_source_build_apk_meta_inf, os.path.join(base_root, "META-INF/"))

    for file in os.listdir(dex_dir):
        if os.path.isfile(os.path.join(dex_dir, file)) and file.endswith(".dex") and file.startswith("classes"):
            shutil.copy(os.path.join(dex_dir, file), base_dex_dir)

    apk_source_assets = os.path.join(apk_source, "assets/")
    apk_source_unknown = os.path.join(apk_source, "unknown/")

    if os.path.exists(apk_source_assets):
        shutil.move(apk_source_assets, base_assets_dir)

    if os.path.exists(apk_source_unknown):
        for file in os.listdir(apk_source_unknown):
            if os.path.isfile(os.path.join(apk_source_unknown, file)):
                shutil.copy(os.path.join(apk_source_unknown, file), base_root)
            else:
                shutil.move(os.path.join(apk_source_unknown, file), os.path.join(base_root, file))

    # zip -r ../base.zip ./ -x "*.DS_Store"
    # 生成base.zip
    base_zip_name = tempFiles.generate_file_name(suffix=".zip")
    cmd = "cd {} && zip -r ../{} ./ -x \"*.DS_Store\"".format(base_data_dir, base_zip_name)
    print("\n" + cmd)
    lines = os.popen(cmd).readlines()
    for line in lines:
        print(line, end="")

    # 用bundletool将base.zip转成base.aab
    # java -jar bundletool.jar build-bundle --modules=base.zip --output=wall.aab
    base_zip = os.path.join(out_path, base_zip_name)
    base_aab = os.path.join(out_path, tempFiles.generate_file_name(suffix=".aab"))
    # print("java -jar {} build-bundle --modules={} --output={}\n".format(bundletool, base_zip, base_aab))
    # subprocess.call(["java", "-jar", bundletool,
    #                  "build-bundle",
    #                  "--modules={}".format(base_zip),
    #                  "--output={}".format(base_aab)])
    tmp_json = os.path.join(out_path, tempFiles.generate_file_name(3, 9, ".json"))
    shutil.copy(pbConfig, tmp_json)
    exportAAB(base_zip, base_aab, tmp_json)
    print("\nbuild aab success.")

    if signName is not None:
        if signName.__contains__("/"):
            arr = signName.split("/")
            alias = arr[-1].split(".")[0]
        else:
            alias = signName.split(".")[0]
        base_aab_signed = os.path.join(out_path, tempFiles.generate_file_name(suffix=".aab"))
        signAAB(base_aab, base_aab_signed, signName, signPwd, alias)
        os.rename(base_aab_signed, os.path.join(out_path, "app_signed.aab"))

    os.rename(base_aab, replaceBasename(base_aab, "app.aab"))
    os.rename(base_zip, replaceBasename(base_zip, "base.zip"))
    os.rename(output_apk, replaceBasename(output_apk, "output.apk"))
    os.rename(output_apk_unzip_data, replaceBasename(output_apk_unzip_data, "output_apk_data"))
    os.rename(compiled_resources_dir, replaceBasename(compiled_resources_dir, "compiled_resources"))
    os.rename(apk_source, replaceBasename(apk_source, "apk_source"))
    os.rename(base_data_dir, replaceBasename(base_data_dir, "base"))
    os.rename(tmp_json, replaceBasename(tmp_json, "config.json"))
    shutil.move(out_path, result_out_path)


def getAbsPath(contextPath, fileName):
    result: str = fileName
    if fileName.__contains__("./"):
        result = os.path.realpath(os.path.join(contextPath, fileName))
    elif fileName == ".":
        result = os.path.join(contextPath)
    elif fileName.startswith("/") is False:
        result = os.path.join(contextPath, fileName)
    return result


# 仅编译资源 用于提取最新的资源id映射表
def aapt2CompileRes(apkPath, output):
    tmp_output = tempFiles.mkTmpOutPath()
    apk_source = tempFiles.mkTmpApkSourcePath(tmp_output)
    # 解包apk 只解包资源文件和manifest
    cmd = f"{apktool} d -f -s {apkPath} -o {apk_source}"
    execCmd(cmd)
    public_xml_path = os.path.join(apk_source, "res/values/public.xml")
    os.remove(public_xml_path)

    resPath = os.path.join(apk_source, "res")
    compiled_resources_dir = tempFiles.mkTmpCompiledResourcesPath(tmp_output)
    compiledRes(resPath, compiled_resources_dir)

    print(f" compile res {getGreenText('success')}")

    android_manifest_path = os.path.join(apk_source, "AndroidManifest.xml")
    output_apk_path = os.path.join(tmp_output, tempFiles.generate_file_name(6, 10, ".apk"))
    versionInfo = getApkVersionInfo(os.path.join(apk_source, "apktool.yml"))
    linkRes(versionInfo, compiled_resources_dir, android_manifest_path, output_apk_path)

    print(f" link res {getGreenText('done')}")

    shutil.move(apk_source, replaceBasename(apk_source, "apk_source"))
    shutil.move(compiled_resources_dir, replaceBasename(compiled_resources_dir, "compiled_resources"))
    shutil.move(output_apk_path, replaceBasename(output_apk_path, "output.apk"))
    shutil.move(tmp_output, output)


if __name__ == '__main__':

    # 加载上下文配置
    loadEnv()

    signName = None
    signPwd = defaultPwd

    if len(sys.argv) == 1:
        showHelp()
        sys.exit(0)

    argv1 = sys.argv[1]

    if argv1.lower() == "-v":
        showAbout()
        sys.exit(0)

    if argv1.lower() == "-h" or argv1.lower() == "--h":
        showHelp()
        sys.exit(0)

    if argv1.lower() == "--readme":
        showReadme()
        sys.exit(0)

    # buildaab xx.apk --sign=test.keystore --pwd=123456 --output=./out
    if argv1.endswith(".apk"):
        if len(sys.argv) > 2:
            if sys.argv[2] == "--just-link-res":
                if len(sys.argv) > 3:
                    params = parseParams(sys.argv[3:])
                    outPath = getParam(params, '--output', 'out', True, False)
                else:
                    outPath = getAbsPath(os.getcwd(), "out")
                aapt2CompileRes(argv1, outPath)
                sys.exit(0)
            params = parseParams(sys.argv[2:], {'--stable-ids': True})
            stableIds = getParam(params, '--stable-ids', False, False, False)
            outPath = getParam(params, '--output', 'out', True, False)
            if params.__contains__("--sign"):
                signName = getParam(params, '--sign', './test.keystore', True, True)
                signPwd = getParam(params, '--pwd', f'{defaultPwd}', False, False)
            processAAB(argv1, signName, signPwd, outPath, pbConfig=getPBConfig(params), stableIds=stableIds)
        else:
            outPath = getAbsPath(os.getcwd(), "out")
            checkFile(outPath, False)
            processAAB(argv1)
        sys.exit(0)

    # buildaab --sign=xxxx.keystore --pwd=123456 --input=base.aab --output=base_signed.aab
    if argv1.lower().startswith("--sign-aab"):
        if len(sys.argv) > 2:
            params = parseParams(sys.argv[2:])
            signName = getParam(params, '--sign', './test.keystore', True, True)
            signPwd = getParam(params, '--pwd', f'{defaultPwd}', False, False)
            alias = signName.split("/")[-1].split(".")[0]

            input_aab = getParam(params, '--input', 'base.aab', True, True)
            output_aab = getParam(params, '--output', f'{input_aab.split("/")[-1].split(".")[0]}_signed.aab', True, False)

            signAAB(input_aab, output_aab, signName, signPwd, alias)
            sys.exit(0)
        else:
            printIllegalParameter(sys.argv)

    # buildaab --export-zip --input=./ --output
    if argv1.lower().startswith("--export-zip"):
        if len(sys.argv) > 2:
            params = parseParams(sys.argv[2:])
            inputPath = getParam(params, '--input', './', True, True)
            zipFile = getParam(params, '--output', 'base.zip', True, False)
            exportZIP(inputPath, zipFile)
            sys.exit(0)
        else:
            printIllegalParameter(sys.argv)

    # java -jar bundletool build-bundle --modules=base.zip --output=base.aab
    # buildaab --export-aab --input=base.zip --output=base_signed.aab
    if argv1.lower().startswith("--export-aab"):
        if len(sys.argv) > 2:
            params = parseParams(sys.argv[2:])
            zipFile = getParam(params, '--input', 'base.zip', True, True)
            aabFile = getParam(params, '--output', f'{zipFile.split("/")[-1].split(".")[0]}.aab', True, False)
            exportAAB(zipFile, aabFile, getPBConfig(params))
            sys.exit(0)
        else:
            printIllegalParameter(sys.argv)

    # buildaab --install-apks=app.apks
    if argv1.lower().startswith("--install-apks"):
        if argv1.lower().__contains__("=") is False:
            print("\nwhere is the \033[1;31;40mapks\033[0m ? brother ??\n")
            sys.exit(0)
        apksPath = obtainArgs(sys.argv[1])
        verifyArg(apksPath, sys.argv[1])
        apksPath = getAbsPath(os.getcwd(), apksPath)
        if os.path.exists(apksPath) is False:
            print(f"\nnot found \033[1;31;40m{apksPath}\033[0m !\n")
        else:
            installApks(apksPath)
        sys.exit(0)

    # /mnt/d/CodeSource/buildaab/bin/Linux/aapt2 compile --dir res/ -o compiled_resources/
    # buildaab --compile-res --input=../res/ --output=./compiled_resources/
    if argv1.lower().startswith("--compile-res"):
        if len(sys.argv) > 2:
            params = parseParams(sys.argv[2:])
            resPath = getParam(params, '--input', 'res/', True, True)
            compiledPath = getParam(params, '--output', 'compiled_resources/', True, False)
            tmp_out_path = tempFiles.mkTmpOutPath()
            tmp_res_path = os.path.join(tmp_out_path, "res")
            shutil.copytree(resPath, tmp_res_path)
            public_xml_path = os.path.join(tmp_res_path, "values/public.xml")
            tmp_compiled_path = tempFiles.mkTmpCompiledResourcesPath(tmp_out_path)
            if os.path.exists(tmp_compiled_path):
                os.removedirs(tmp_compiled_path)
            compiledRes(tmp_res_path, tmp_compiled_path)
            shutil.rmtree(tmp_res_path)
            shutil.move(tmp_compiled_path, compiledPath)
            sys.exit(0)
        else:
            printIllegalParameter(sys.argv)
    # /mnt/d/CodeSource/buildaab/bin/Linux/aapt2 link --proto-format \
    #         -o output.apk \
    #         -I /mnt/d/CodeSource/buildaab/bin/android.jar \
    #         --manifest your_path/AndroidManifest.xml \
    #         -R your_path/compiled_resources/*.flat \
    #         --auto-add-overlay
    # buildaab --link-res --manifest=AndroidManifest.xml --res=compiled_resources/ --output=output.apk
    if argv1.lower().startswith("--link-res"):
        if len(sys.argv) > 2:
            params = parseParams(sys.argv[2:])
            manifest = getParam(params, '--manifest', 'AndroidManifest.xml', True, True)
            compiled_resources = getParam(params, '--res', 'compiled_resources', True, True)
            output = getParam(params, '--output', 'output.apk', True, False)
            print(params)
            if params.__contains__("--minSdk") is False:
                print(f"{getRedText('Missing parameter --minSdk')}")
                sys.exit(0)
            if params.__contains__("--targetSdk") is False:
                print(f"{getRedText('Missing parameter --targetSdk')}")
                sys.exit(0)

            stableIds = getParam(params, '--stable-ids', None, True, True)

            versionInfo = ApkVersionInfo()
            versionInfo.versionCode = getParam(params, '--versionCode', '1', False, False)
            versionInfo.versionName = getParam(params, '--versionName', '1.0', False, False)
            versionInfo.minSdkVersion = getParam(params, '--minSdk', None, False, False)
            versionInfo.targetSdkVersion = getParam(params, '--targetSdk', None, False, False)
            temp_out_path = tempFiles.mkTmpOutPath()
            temp_compiled_resources = tempFiles.mkTmpCompiledResourcesPath(temp_out_path)
            if os.path.exists(temp_compiled_resources):
                os.removedirs(temp_compiled_resources)
            shutil.copytree(compiled_resources, temp_compiled_resources)
            temp_manifest = os.path.join(temp_out_path, 'AndroidManifest.xml')
            shutil.copy(manifest, temp_manifest)
            temp_output = os.path.join(temp_out_path, tempFiles.generate_file_name(suffix=".apk"))
            linkRes(versionInfo, temp_compiled_resources, temp_manifest, temp_output, stableIds=stableIds)
            shutil.move(temp_output, output)
            shutil.rmtree(temp_out_path)
            sys.exit(0)
        else:
            printIllegalParameter(sys.argv)

    # buildaab --export-apks --input=xxxx_signed.aab --sign=test.keystore --pwd=123456 --device=device.json --output=xxxx.apks
    if argv1.lower().startswith("--export-apks"):
        exportApks()
        sys.exit(0)

    # buildaab --get-device=mate30-pro.json
    if argv1.lower().startswith("--get-device"):
        # 默认json文件名;路径在当前上下文目录
        jsonPath = os.path.join(os.getcwd(), "device.json")
        if argv1.__contains__("="):
            jsonPath = argv1.split("=")[1]
            if jsonPath.__contains__("./"):
                jsonPath = os.path.realpath(os.path.join(os.getcwd(), jsonPath))
        if os.path.exists(jsonPath):
            # 删除已存在的json文件
            os.remove(jsonPath)
        getDeviceJson(jsonPath)
        sys.exit(0)

    # java -jar bundletool-all-1.13.0.jar dump config --bundle app.aab
    if argv1.lower().startswith("--dump-config"):
        params = parseParams(sys.argv[2:])
        config_path = getParam(params, '--output', 'config.json', True, False)
        aab_path = getParam(params, '--input', 'app.aab', True, True)
        cmd = f"java -jar {bundletool} dump config --bundle {aab_path} > {config_path}"
        execCmd(cmd)
        sys.exit(0)

    if argv1.lower().startswith("-"):
        print(" illegal parameter : \033[1;31;40m {}\033[0m".format(argv1))
        sys.exit(0)