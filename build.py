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

def check_status(status, msg):
    if status != 0:
        sys.stderr.write(msg)
        exit(status)


def get_build_dir():
    current_platform = platform.system()
    build_dir = "./build/"

    if current_platform == "Windows": build_dir += "windows-latest"
    elif current_platform == "Linux": build_dir += "ubuntu-latest"
    elif current_platform == "Darwin": build_dir += "macos-latest"
    else: raise OSError("Platform %s is not supported!" % (current_platform))

    return build_dir

def get_package_name():
    # if platform.system() == "Windows": package_name += ".exe"

    return "kubescape"


def main():
    print("Building Kubescape")

    # Set some variables
    package_name = get_package_name()
    release_version = os.getenv("RELEASE")
    armo_be_server = os.getenv("ArmoBEServer")
    armo_er_server = os.getenv("ArmoERServer")
    armo_website = os.getenv("ArmoWebsite")
    armo_auth_server = os.getenv("ArmoAuthServer")

    client_name = os.getenv("CLIENT")

    # Create build directory
    build_dir = get_build_dir()

    ks_file = os.path.join(build_dir, package_name)
    hash_file = f"{ks_file}.sha256"

    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)

    # Build kubescape
    ldflags = "-w -s"
    if release_version:
        build_url = "github.com/armosec/kubescape/v2/core/cautils.BuildNumber"
        ldflags += f" -X {build_url}={release_version}"
    if client_name:
        client_var = "github.com/armosec/kubescape/v2/core/cautils.Client"
        ldflags += f" -X {client_var}={client_name}"
    if armo_be_server:
        ldflags += f" -X {BE_SERVER_CONST}={armo_be_server}"
    if armo_er_server:
        ldflags += f" -X {ER_SERVER_CONST}={armo_er_server}"
    if armo_website:
        ldflags += f" -X {WEBSITE_CONST}={armo_website}"
    if armo_auth_server:
        ldflags += f" -X {AUTH_SERVER_CONST}={armo_auth_server}"

    build_command = ["go", "build", "-o", ks_file, "-ldflags" ,ldflags]

    print(f"Building kubescape and saving here: {ks_file}")
    print(f'Build command: {" ".join(build_command)}')

    status = subprocess.call(build_command)
    check_status(status, "Failed to build kubescape")

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
