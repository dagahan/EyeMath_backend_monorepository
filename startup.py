import os, sys

def install_requirements():
    try:
        os.system(f"pip install -r req.txt")
    except Exception as e:
        print(f"Error installing requirements: {e}\n\nPlease install the requirements manually.")
        sys.exit(1)

import toml, subprocess


def load_toml():
    with open("config.toml", "r") as f:
        return toml.load(f)
    
def save_toml(config):
    with open("config.toml", "w") as f:
        toml.dump(config, f)

read_key_toml = lambda database, key: load_toml()[database][key]

def write_key_toml(database, key, value):
    toml = load_toml()
    toml[database][key] = value
    save_toml(toml)

CONFIG = load_toml()
read_key_config = lambda database, key: CONFIG[database][key]







if __name__ == "__main__":
    install_requirements()

    BASE_DIR = f"{os.path.abspath(os.path.dirname(__file__))}/"
    RES_DIR = f"{BASE_DIR}res/"
    DATA_DIR = f"{BASE_DIR}data/"
    CPP_DIR = f"{RES_DIR}cpp/"
    BINARY_DIR = f"{CPP_DIR}binary/"

    
    CONFIG["paths"]["base_dir"] = BASE_DIR
    CONFIG["paths"]["res_dir"] = RES_DIR
    CONFIG["paths"]["data_dir"] = DATA_DIR
    CONFIG["paths"]["cpp_dir"] = CPP_DIR
    CONFIG["paths"]["binary_dir"] = BINARY_DIR
    save_toml(CONFIG)


    compile_cmd = f"{read_key_config("paths", "compiler")} {read_key_config("cpp", "cpp_version")} {read_key_config("paths", "cpp_dir")}{read_key_config("cpp", "cpp_file")} {read_key_config("cpp", "compiler_flags")} {read_key_config("paths", "binary_dir")}{read_key_config("cpp", "compiled_file")}"
    try:
        print(f"Compiling C++ code with command: {compile_cmd}")
        subprocess.run(compile_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling C++ code: {e}")
        sys.exit(1)

    subprocess.run([f"{read_key_config("paths", "binary_dir")}_Server_"])