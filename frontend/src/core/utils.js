// Utility functions for frontend
import ConfigLoader from './config.js';

class MethodTools {
    static getMethodInfo(stackLevel = 1) {
        try {
            const stack = new Error().stack;
            const lines = stack.split('\n');
            if (lines.length <= stackLevel + 1) {
                return ["Unknown File", "Unknown Method", 0];
            }
            
            const line = lines[stackLevel + 1];
            const match = line.match(/at\s+(.+?)\s+\((.+?):(\d+):\d+\)/);
            if (match) {
                return [match[2], match[1], parseInt(match[3])];
            }
            return ["Unknown File", "Unknown Method", 0];
        } catch (ex) {
            console.error("Error getting method info:", ex);
            return ["Unknown File", "Unknown Method", 0];
        }
    }
}

class FileSystemTools {
    static async ensureDirectoryExists(directory) {
        try {
            // In browser environment, we can't create directories
            // This is a placeholder for consistency with backend
            console.log(`Directory check: ${directory}`);
        } catch (error) {
            console.error(`Error ensuring directory exists: ${directory}`, error);
        }
    }

    static async saveFile(filePath, data) {
        try {
            const blob = new Blob([data], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filePath.split('/').pop();
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error(`Error saving file: ${filePath}`, error);
        }
    }

    static async deleteFile(filePath) {
        try {
            // In browser environment, we can't delete files from filesystem
            // This is a placeholder for consistency with backend
            console.log(`File deletion requested: ${filePath}`);
        } catch (error) {
            console.error(`Error deleting file: ${filePath}`, error);
        }
    }
}

class EnvTools {
    static loadEnvVar(variableName) {
        try {
            const value = import.meta.env[`NGINX_${variableName}`] || 
                         import.meta.env[variableName] || 
                         null;
            
            if (!value) {
                console.warn(`Cannot load env var named '${variableName}'. returning null.`);
            }
            return value;
        } catch (ex) {
            console.error(`Error loading env variable '${variableName}':`, ex);
            return null;
        }
    }

    static requiredLoadEnvVar(variableName) {
        const value = this.loadEnvVar(variableName);
        if (!value) {
            throw new Error(`Missing required environment variable: ${variableName}`);
        }
        return value;
    }

    static setEnvVar(variableName, variableValue) {
        try {
            // In browser environment, we can't set environment variables
            // This is a placeholder for consistency with backend
            console.log(`Setting env var: ${variableName}=${variableValue}`);
        } catch (ex) {
            console.error(`Error setting env variable '${variableName}':`, ex);
        }
    }

    static isRunningInsideDocker() {
        try {
            return this.loadEnvVar("RUNNING_INSIDE_DOCKER") === "1";
        } catch (ex) {
            console.error("Error checking if running inside docker:", ex);
            return false;
        }
    }

    static getServiceUrl(serviceName) {
        try {
            if (this.isRunningInsideDocker()) {
                const project = this.requiredLoadEnvVar("COMPOSE_PROJECT_NAME");
                const port = this.loadEnvVar(`${serviceName.toUpperCase()}_PORT`);
                return `http://${serviceName}-${project}:${port}`;
            }
            
            const host = this.requiredLoadEnvVar(`${serviceName.toUpperCase()}_HOST`);
            const port = this.requiredLoadEnvVar(`${serviceName.toUpperCase()}_PORT`);
            return `http://${host}:${port}`;
        } catch (ex) {
            console.error(`Error getting service URL for ${serviceName}:`, ex);
            return null;
        }
    }

    static getServicePort(serviceName) {
        return this.loadEnvVar(`${serviceName.toUpperCase()}_PORT`);
    }
}

class JsonLoader {
    static async readJson(path) {
        try {
            const response = await fetch(path);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`Error reading JSON file ${path}:`, error);
            return {};
        }
    }

    static async writeJson(path, data) {
        try {
            const response = await fetch(path, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error(`Error writing JSON file ${path}:`, error);
        }
    }
}

class Filters {
    static filterStrings(list1, list2) {
        const set2 = new Set(list2);
        return list1.filter(s => !set2.has(s));
    }

    static personalizedLine(line, artifact, name) {
        return line.replace(new RegExp(artifact, 'g'), name);
    }
}

class StringTools {
    static async hashString(string) {
        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(string);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        } catch (error) {
            console.error("Error hashing string:", error);
            return null;
        }
    }
}

class TimeTools {
    static nowTimeZone() {
        const tzName = EnvTools.loadEnvVar("TZ") || "UTC";
        try {
            return new Date().toLocaleString("en-US", { timeZone: tzName });
        } catch (ex) {
            console.error(`Error getting time for zone ${tzName}:`, ex);
            return new Date().toLocaleString("en-US", { timeZone: "UTC" });
        }
    }

    static nowTimeStamp() {
        return Math.floor(Date.now() / 1000);
    }
}

class ValidatingTools {
    static validateModelsBySchema(models, schema) {
        if (!Array.isArray(models)) {
            models = [models];
        }

        const validModels = [];
        for (const model of models) {
            try {
                // Simple validation - in real app you'd use a proper validation library
                if (schema && typeof schema === 'function') {
                    const dto = new schema(model);
                    validModels.push(dto);
                } else {
                    validModels.push(model);
                }
            } catch (ex) {
                const modelId = model.id || 'unknown';
                console.warn(`Skipping invalid instance (id=${modelId}):`, ex);
            }
        }

        if (validModels.length === 1) {
            return validModels[0];
        }
        return validModels;
    }
}

// DOM utilities
class DOMTools {
    static createElement(tagName, className = '', content = '') {
        const element = document.createElement(tagName);
        if (className) {
            element.className = className;
        }
        if (content) {
            element.innerHTML = content;
        }
        return element;
    }

    static querySelector(selector) {
        return document.querySelector(selector);
    }

    static querySelectorAll(selector) {
        return document.querySelectorAll(selector);
    }

    static addEventListener(element, event, handler) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.addEventListener(event, handler);
        }
    }
}

// Notification system
class NotificationManager {
    static showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notice ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideIn 0.3s ease-out;
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);

        return notification;
    }
}

// Export all utility classes
export {
    MethodTools,
    FileSystemTools,
    EnvTools,
    JsonLoader,
    Filters,
    StringTools,
    TimeTools,
    ValidatingTools,
    DOMTools,
    NotificationManager
};

// Export showNotification function for convenience
export const showNotification = NotificationManager.showNotification;

// Export createElement function for convenience
export const createElement = DOMTools.createElement;

// Export default utility object
export default {
    MethodTools,
    FileSystemTools,
    EnvTools,
    JsonLoader,
    Filters,
    StringTools,
    TimeTools,
    ValidatingTools,
    DOMTools,
    NotificationManager
};