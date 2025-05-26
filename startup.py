import os, sys

def install_requirements():
    try:
        os.system(f"pip install -r req.txt")
    except Exception as e:
        print(f"Error installing requirements: {e}\n\nPlease install the requirements manually.")
        sys.exit(1)

try:
    import toml, subprocess
except ImportError:
    install_requirements()
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

def setup_derictories():
    CONFIG["paths"]["base_dir"] = BASE_DIR
    CONFIG["paths"]["res_dir"] = RES_DIR
    CONFIG["paths"]["data_dir"] = DATA_DIR
    CONFIG["paths"]["go_dir"] = GO_DIR
    CONFIG["paths"]["binary_dir"] = BINARY_DIR
    
    try:
        CONFIG["paths"]["compiler"] = (subprocess.run(read_key_config("go", "check_path_go_cmd"), shell=True, stdout=subprocess.PIPE)).stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error cheking which go is located: {e}")
        sys.exit(1)

    save_toml(CONFIG)

def setup_binary_backend_go():
    try:
        compile_cmd = f"{read_key_config("go", "go_flags")} {read_key_config("paths", "compiler")} {read_key_config("go", "go_build")} {read_key_config("paths", "binary_dir")}{read_key_config("go", "compiled_file")} {read_key_config("paths", "go_dir")}{read_key_config("go", "go_file")}"
        print(f"Compiling go code with command: {compile_cmd}")
        subprocess.run(compile_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling go code: {e}")
        sys.exit(1)

def setup_binary_backend_go_run():
    subprocess.run([f"{read_key_config("paths", "binary_dir")}{read_key_config("go", "compiled_file")}"])



if __name__ == "__main__":
    install_requirements()

    BASE_DIR = f"{os.path.abspath(os.path.dirname(__file__))}/"
    RES_DIR = f"{BASE_DIR}res/"
    DATA_DIR = f"{BASE_DIR}data/"
    GO_DIR = f"{RES_DIR}go/"
    BINARY_DIR = f"{GO_DIR}binary/"

    setup_derictories()
    setup_binary_backend_go()
    setup_binary_backend_go_run()