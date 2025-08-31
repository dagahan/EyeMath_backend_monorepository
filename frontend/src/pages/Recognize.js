import { authForm, authJson } from "../api/client.js";

export default function Recognize(){
  const el = document.createElement("div");
  el.className = "grid";
  el.innerHTML = `
    <div style="text-align: center; margin-bottom: 32px;">
      <div class="h1">📷 Распознавание математики</div>
      <p class="muted">Загрузите изображение с математическим выражением и получите LaTeX код</p>
    </div>
    
    <div class="card" style="padding: 0; overflow: hidden;">
      <div class="drop-zone" id="dropZone">
        <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
        <h3 style="margin: 0 0 8px; color: var(--text);">Перетащите изображение сюда</h3>
        <p style="margin: 0 0 16px; color: var(--muted);">или нажмите для выбора файла</p>
        <input type="file" id="fileInput" accept="image/*" style="display: none;" />
        <button class="btn secondary" type="button" onclick="document.getElementById('fileInput').click()">
          Выбрать файл
        </button>
        <p style="margin: 16px 0 0; font-size: 12px; color: var(--muted);">
          Поддерживаемые форматы: JPG, PNG, GIF, WebP
        </p>
      </div>
      
      <div id="imagePreview" style="display: none; padding: 20px; text-align: center;">
        <img id="previewImg" class="image-preview" alt="Предпросмотр" />
        <div id="progressContainer" style="display: none; margin: 16px 0;">
          <div style="background: var(--border); border-radius: 8px; height: 8px; overflow: hidden;">
            <div id="progressBar" style="background: linear-gradient(90deg, var(--primary), var(--accent)); height: 100%; width: 0%; transition: width 0.3s ease;"></div>
          </div>
          <div id="progressText" style="margin-top: 8px; font-size: 14px; color: var(--muted);">Обработка...</div>
        </div>
        <div style="margin-top: 16px;">
          <button class="btn" id="recognizeBtn" type="button">
            <span id="recognizeText">Распознать</span>
          </button>
          <button class="btn secondary" type="button" onclick="document.getElementById('fileInput').click()" style="margin-left: 8px;">
            Выбрать другой файл
          </button>
        </div>
      </div>
    </div>
    
    <div class="notice error" id="err" style="display:none"></div>
    
    <div class="card" id="resultCard" style="display:none">
      <h3 style="margin: 0 0 16px; color: var(--text);">Результат распознавания</h3>
      
      <div class="result-card">
        <h4 style="margin: 0 0 12px; color: var(--text);">Исходный LaTeX:</h4>
        <div style="background: var(--elevated); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-break: break-all;" id="latex"></div>
        <button class="btn secondary" id="copyLatexBtn" type="button" style="margin-top: 12px;">
          📋 Копировать LaTeX
        </button>
      </div>
      
      <div class="result-card">
        <h4 style="margin: 0 0 12px; color: var(--text);">Нормализованный LaTeX (SymPy):</h4>
        <div style="background: var(--elevated); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; min-height: 60px; display: flex; align-items: center; justify-content: center; color: var(--muted);" id="norm">
          Нажмите "Нормализовать" для получения SymPy-LaTeX
        </div>
        <div style="margin-top: 12px;">
          <button class="btn secondary" id="normalizeBtn" type="button">
            🔄 Нормализовать
          </button>
          <button class="btn secondary" id="copyNormBtn" type="button" style="margin-left: 8px; display: none;">
            📋 Копировать нормализованный
          </button>
        </div>
      </div>
      
      <div style="margin-top: 24px; text-align: center;">
        <button class="btn" onclick="location.hash='#/solve'" style="margin-right: 8px;">
          🧮 Решить это выражение
        </button>
        <button class="btn secondary" onclick="location.hash='#/render'">
          🎨 Рендерить в изображение
        </button>
      </div>
    </div>
  `;
  
  const dropZone = el.querySelector("#dropZone");
  const fileInput = el.querySelector("#fileInput");
  const imagePreview = el.querySelector("#imagePreview");
  const previewImg = el.querySelector("#previewImg");
  const recognizeBtn = el.querySelector("#recognizeBtn");
  const recognizeText = el.querySelector("#recognizeText");
  const err = el.querySelector("#err");
  const resultCard = el.querySelector("#resultCard");
  const latexEl = el.querySelector("#latex");
  const normEl = el.querySelector("#norm");
  const normalizeBtn = el.querySelector("#normalizeBtn");
  const copyLatexBtn = el.querySelector("#copyLatexBtn");
  const copyNormBtn = el.querySelector("#copyNormBtn");
  const progressContainer = el.querySelector("#progressContainer");
  const progressBar = el.querySelector("#progressBar");
  const progressText = el.querySelector("#progressText");
  
  let currentFile = null;
  
  // Drag and drop functionality
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });
  
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  });
  
  dropZone.addEventListener('click', () => {
    fileInput.click();
  });
  
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });
  
  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      showError('Пожалуйста, выберите изображение');
      return;
    }
    
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      dropZone.style.display = 'none';
      imagePreview.style.display = 'block';
      resultCard.style.display = 'none';
    };
    reader.readAsDataURL(file);
  }
  
  recognizeBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    
    // Prevent multiple clicks
    if (recognizeBtn.classList.contains('loading')) return;
    
    recognizeBtn.classList.add('loading');
    recognizeText.textContent = 'Распознавание...';
    err.style.display = 'none';
    resultCard.style.display = 'none';
    
    try {
      // Show progress
      progressContainer.style.display = 'block';
      updateProgress(10, 'Оптимизация изображения...');
      
      // Optimize image before sending
      const optimizedFile = await optimizeImage(currentFile);
      updateProgress(30, 'Отправка на сервер...');
      
      const fd = new FormData();
      fd.append('file', optimizedFile);
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      updateProgress(50, 'Распознавание...');
      const res = await authForm("/recognizer/image", fd, controller.signal);
      clearTimeout(timeoutId);
      
      updateProgress(90, 'Обработка результата...');
      
      latexEl.textContent = res.latex || "";
      resultCard.style.display = 'block';
      
      // Reset normalize section
      normEl.textContent = 'Нажмите "Нормализовать" для получения SymPy-LaTeX';
      normEl.style.color = 'var(--muted)';
      copyNormBtn.style.display = 'none';
      
      updateProgress(100, 'Готово!');
      setTimeout(() => {
        progressContainer.style.display = 'none';
      }, 1000);
      
    } catch (ex) {
      progressContainer.style.display = 'none';
      if (ex.name === 'AbortError') {
        showError('Превышено время ожидания. Попробуйте еще раз.');
      } else {
        showError(ex.message || "Ошибка распознавания");
      }
    } finally {
      recognizeBtn.classList.remove('loading');
      recognizeText.textContent = 'Распознать';
    }
  });
  
  normalizeBtn.addEventListener('click', async () => {
    const latex = latexEl.textContent;
    if (!latex) return;
    
    normalizeBtn.classList.add('loading');
    normalizeBtn.textContent = '🔄 Нормализация...';
    
    try {
      const res = await authJson("POST", "/recognizer/normalize", { expression: latex });
      normEl.textContent = res.normalized || "";
      normEl.style.color = 'var(--text)';
      copyNormBtn.style.display = 'inline-block';
    } catch (ex) {
      normEl.textContent = "Ошибка нормализации: " + (ex.message || "");
      normEl.style.color = '#ef4444';
    } finally {
      normalizeBtn.classList.remove('loading');
      normalizeBtn.textContent = '🔄 Нормализовать';
    }
  });
  
  copyLatexBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(latexEl.textContent);
    copyLatexBtn.textContent = '✅ Скопировано!';
    setTimeout(() => {
      copyLatexBtn.textContent = '📋 Копировать LaTeX';
    }, 2000);
  });
  
  copyNormBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(normEl.textContent);
    copyNormBtn.textContent = '✅ Скопировано!';
    setTimeout(() => {
      copyNormBtn.textContent = '📋 Копировать нормализованный';
    }, 2000);
  });
  
  function showError(message) {
    err.textContent = message;
    err.style.display = 'block';
  }
  
  function updateProgress(percent, text) {
    progressBar.style.width = percent + '%';
    progressText.textContent = text;
  }
  
  // Image optimization function
  async function optimizeImage(file) {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        // Calculate optimal dimensions (max 1920x1080)
        const maxWidth = 1920;
        const maxHeight = 1080;
        let { width, height } = img;
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width *= ratio;
          height *= ratio;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        // Draw and compress
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob((blob) => {
          const optimizedFile = new File([blob], file.name, {
            type: 'image/jpeg',
            lastModified: Date.now()
          });
          resolve(optimizedFile);
        }, 'image/jpeg', 0.8); // 80% quality
      };
      
      img.src = URL.createObjectURL(file);
    });
  }
  
  return el;
}
