import os
import sys
import hashlib
import platform
import subprocess

BASE_GETTER_CONST = "github.com/armosec/kubescape/v2/core/cautils/getter"
BE_SERVER_CONST = f"{BASE_GETTER_CONST}.ArmoBEURL"
ER_SERVER_CONST = f"{BASE_GETTER_CONST}.ArmoERURL"
WEBSITE_CONST = f"{BASE_GETTER_CONST}.ArmoFEURL"
AUTH_SERVER_CONST = f"{BASE_GETTER_CONST}.armoAUTHURL"

def checkStatus(status, msg):
    if status != 0:
        sys.stderr.write(msg)
        exit(status)


def getBuildDir():
    currentPlatform = platform.system()
    buildDir = "build/"

    if currentPlatform == "Windows": return os.path.join(buildDir, "windows-latest")
    if currentPlatform == "Linux": return os.path.join(buildDir, "ubuntu-latest")
    if currentPlatform == "Darwin": return os.path.join(buildDir, "macos-latest")
    raise OSError(f"Platform {currentPlatform} is not supported!")

def getPackageName():
    # if platform.system() == "Windows": packageName += ".exe"

    return "kubescape"


def main():
    print("Building Kubescape")

    # print environment variables
    # print(os.environ)

    # Set some variables
    packageName = getPackageName()
    releaseVersion = os.getenv("RELEASE")
    ArmoBEServer = os.getenv("ArmoBEServer")
    ArmoERServer = os.getenv("ArmoERServer")
    ArmoWebsite = os.getenv("ArmoWebsite")
    ArmoAuthServer = os.getenv("ArmoAuthServer")

    # Create build directory
    buildDir = getBuildDir()

    ks_file = os.path.join(buildDir, packageName)
    hash_file = f"{ks_file}.sha256"

    if not os.path.isdir(buildDir):
        os.makedirs(buildDir)

    # Build kubescape
    ldflags = "-w -s"
    if releaseVersion:
        buildUrl = "github.com/armosec/kubescape/v2/core/cautils.BuildNumber"
        ldflags += f" -X {buildUrl}={releaseVersion}"
    if ArmoBEServer:
        ldflags += f" -X {BE_SERVER_CONST}={ArmoBEServer}"
    if ArmoERServer:
        ldflags += f" -X {ER_SERVER_CONST}={ArmoERServer}"
    if ArmoWebsite:
        ldflags += f" -X {WEBSITE_CONST}={ArmoWebsite}"
    if ArmoAuthServer:
        ldflags += f" -X {AUTH_SERVER_CONST}={ArmoAuthServer}"

    build_command = ["go", "build", "-o", ks_file, "-ldflags" ,ldflags]

    print(f"Building kubescape and saving here: {ks_file}")
    print(f'Build command: {" ".join(build_command)}')

    status = subprocess.call(build_command)
    checkStatus(status, "Failed to build kubescape")

    sha256 = hashlib.sha256()
    with open(ks_file, "rb") as kube:
        sha256.update(kube.read())
        with open(hash_file, "w") as kube_sha:
            hash = sha256.hexdigest()
            print(f"kubescape hash: {hash}, file: {hash_file}")
            kube_sha.write(sha256.hexdigest())

    print("Build Done")
 
 
if __name__ == "__main__":
    main()
