import os, sys


BASE_DIR = f"{os.path.abspath(os.path.dirname(__file__))}/"
RES_DIR = f"{BASE_DIR}res/"
DATA_DIR = f"{BASE_DIR}data/"
CPP_DIR = f"{RES_DIR}cpp/"
BINARY_DIR = f"{CPP_DIR}binary/"


def install_requirements():
    try:
        os.system(f"pip install -r {RES_DIR}req.txt")
    except Exception as e:
        print(f"Error installing requirements: {e}\n\nPlease install the requirements manually.")
        sys.exit(1)

install_requirements()
import toml
import subprocess

config_path = "config.toml"
config = toml.load(config_path)

config["paths"]["base_dir"] = BASE_DIR
config["paths"]["res_dir"] = RES_DIR
config["paths"]["data_dir"] = DATA_DIR
config["paths"]["cpp_dir"] = CPP_DIR
config["paths"]["binary_dir"] = BINARY_DIR

with open(config_path, "w") as f:
    toml.dump(config, f)


compile_cmd = f"{config["cpp"]["compiler"]} {config["cpp"]["cpp_version"]} {config["paths"]["cpp_dir"]}{config["cpp"]["cpp_file"]} {config["cpp"]["compiler_flags"]} {config["paths"]["binary_dir"]}{config["cpp"]["compiled_file"]}"
subprocess.run(compile_cmd, shell=True, check=True)
subprocess.run([f"{BINARY_DIR}_Server_"])