class ConfigLoader {
    static #instance = null;
    static #config = {};

    constructor() {
        if (ConfigLoader.#instance) {
            return ConfigLoader.#instance;
        }
        ConfigLoader.#instance = this;
        this.#load();
    }

    #load() {
        try {
            this.#config = {
                API_BASE: import.meta.env.NGINX_API_BASE || "http://localhost:9998",
                APP_NAME: "eye.math",
                VERSION: "1.0.0",
                HOST: import.meta.env.FRONTEND_NGINX_HOST || "localhost",
                PORT: import.meta.env.FRONTEND_NGINX_PORT || "4173",
                DEV_HOST: import.meta.env.FRONTEND_NGINX_DEV_HOST || "localhost",
                DEV_PORT: import.meta.env.FRONTEND_NGINX_DEV_PORT || "5500"
            };
            
            console.log("Configuration loaded successfully");
        } catch (error) {
            console.error("Config load failed:", error);
            throw error;
        }
    }

    static get(section, key = "") {
        if (!ConfigLoader.#instance) {
            new ConfigLoader();
        }
        
        try {
            if (key === "") {
                return ConfigLoader.#config[section] || {};
            }
            return ConfigLoader.#config[section]?.[key];
        } catch (ex) {
            console.error(`Cannot get [${section}][${key}]:`, ex);
            throw ex;
        }
    }

    static getAll() {
        if (!ConfigLoader.#instance) {
            new ConfigLoader();
        }
        return { ...ConfigLoader.#config };
    }
}

export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: "/users/register",
    LOGIN: "/users/login",
    LOGOUT: "/users/logout"
  },
  TOKENS: {
    ACCESS: "/tokens/access",
    REFRESH: "/tokens/refresh"
  },
  RECOGNIZER: {
    IMAGE: "/recognizer/image",
    NORMALIZE: "/recognizer/normalize"
  },
  SOLVER: {
    SOLVE: "/solver/solve"
  },
  RENDERER: {
    RENDER: "/renderer/render",
    RENDER_BATCH: "/renderer/render/batch"
  }
};

export const CONFIG = {
  API_BASE: import.meta.env.NGINX_API_BASE || "http://localhost:9998",
  APP_NAME: "eye.math",
  VERSION: "1.0.0"
};

export default ConfigLoader;