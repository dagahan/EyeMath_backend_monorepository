import { authJson } from "../api/client.js";

export default function Render(){
  const el = document.createElement("div");
  el.className = "grid";
  el.innerHTML = `
    <div style="text-align: center; margin-bottom: 32px;">
      <div class="h1">🎨 LaTeX Rendering</div>
      <p class="muted">Convert LaTeX expressions into beautiful high-quality images</p>
    </div>
    
    <div class="card">
      <h3 style="margin: 0 0 20px; color: var(--text);">Enter LaTeX Expression</h3>
      
      <div class="toolbar">
        <button class="toolbar-btn" data-insert="\\int_{a}^{b} f(x) dx">∫</button>
        <button class="toolbar-btn" data-insert="\\sum_{i=1}^{n} x_i">∑</button>
        <button class="toolbar-btn" data-insert="\\prod_{i=1}^{n} x_i">∏</button>
        <button class="toolbar-btn" data-insert="\\lim_{x \\to \\infty}">lim</button>
        <button class="toolbar-btn" data-insert="\\frac{a}{b}">a/b</button>
        <button class="toolbar-btn" data-insert="\\sqrt{x}">√x</button>
        <button class="toolbar-btn" data-insert="\\sqrt[n]{x}">ⁿ√x</button>
        <button class="toolbar-btn" data-insert="\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}">Matrix</button>
        <button class="toolbar-btn" data-insert="\\begin{cases} x & \\text{if } y \\\\ z & \\text{otherwise} \\end{cases}">Cases</button>
        <button class="toolbar-btn" data-insert="\\alpha, \\beta, \\gamma, \\delta">Greek</button>
        <button class="toolbar-btn" data-insert="\\infty, \\pm, \\mp">Symbols</button>
      </div>
      
      <form id="renderForm">
        <textarea 
          class="math-editor" 
          name="latex_expression" 
          id="latexInput"
          placeholder="Enter LaTeX expression, e.g.: \\int_0^1 x^2 dx = \\frac{1}{3}"
          required
        ></textarea>
        
        <div style="margin: 20px 0;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">DPI (Image Quality)</label>
          <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
            <input 
              class="input" 
              name="dpi" 
              type="number" 
              min="90" 
              max="600" 
              step="10" 
              value="300"
              style="width: 120px;"
            />
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button type="button" class="toolbar-btn" data-dpi="150">150 DPI</button>
              <button type="button" class="toolbar-btn" data-dpi="300">300 DPI</button>
              <button type="button" class="toolbar-btn" data-dpi="600">600 DPI</button>
            </div>
          </div>
          <p style="margin: 8px 0 0; font-size: 12px; color: var(--muted);">
            Recommended: 150 DPI for web, 300 DPI for print, 600 DPI for high quality
          </p>
        </div>
        
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button class="btn" type="submit" id="renderBtn">
            <span id="renderText">🎨 Render</span>
          </button>
          <button class="btn secondary" type="button" id="clearBtn">
            🗑️ Clear
          </button>
          <button class="btn secondary" type="button" id="exampleBtn">
            📝 Examples
          </button>
        </div>
      </form>
      
      <div class="notice error" id="err" style="display:none"></div>
    </div>

    <div class="card" id="resultCard" style="display: none;">
      <h3 style="margin: 0 0 16px; color: var(--text);">Rendering Result</h3>
      
      <div style="text-align: center; margin-bottom: 20px;">
        <img id="renderedImg" alt="Rendered LaTeX" style="max-width: 100%; border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);" />
      </div>
      
      <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
        <a id="downloadLink" class="btn" target="_blank" style="text-decoration: none;">
          📥 Download Image
        </a>
        <button class="btn secondary" id="copyUrlBtn">
          📋 Copy Link
        </button>
        <button class="btn secondary" id="newRenderBtn">
          🆕 New Render
        </button>
      </div>
      
      <div style="margin-top: 20px; padding: 16px; background: var(--elevated); border-radius: 8px; border: 1px solid var(--border);">
        <h4 style="margin: 0 0 8px; color: var(--text);">Image Information:</h4>
        <div id="imageInfo" style="font-size: 14px; color: var(--muted);"></div>
      </div>
    </div>
  `;
  
  const form = el.querySelector("#renderForm");
  const latexInput = el.querySelector("#latexInput");
  const dpiInput = el.querySelector('input[name="dpi"]');
  const renderBtn = el.querySelector("#renderBtn");
  const renderText = el.querySelector("#renderText");
  const clearBtn = el.querySelector("#clearBtn");
  const exampleBtn = el.querySelector("#exampleBtn");
  const err = el.querySelector("#err");
  const resultCard = el.querySelector("#resultCard");
  const renderedImg = el.querySelector("#renderedImg");
  const downloadLink = el.querySelector("#downloadLink");
  const copyUrlBtn = el.querySelector("#copyUrlBtn");
  const newRenderBtn = el.querySelector("#newRenderBtn");
  const imageInfo = el.querySelector("#imageInfo");
  
  // Toolbar buttons
  const toolbarBtns = el.querySelectorAll('.toolbar-btn');
  toolbarBtns.forEach(btn => {
    if (btn.dataset.insert) {
      btn.addEventListener('click', () => {
        const insert = btn.dataset.insert;
        const start = latexInput.selectionStart;
        const end = latexInput.selectionEnd;
        const text = latexInput.value;
        const before = text.substring(0, start);
        const after = text.substring(end);
        latexInput.value = before + insert + after;
        latexInput.focus();
        latexInput.setSelectionRange(start + insert.length, start + insert.length);
      });
    } else if (btn.dataset.dpi) {
      btn.addEventListener('click', () => {
        dpiInput.value = btn.dataset.dpi;
      });
    }
  });
  
  // Examples
  const examples = [
    { name: "Integral", expr: "\\int_0^1 x^2 dx = \\frac{1}{3}" },
    { name: "Quadratic Formula", expr: "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" },
    { name: "Matrix", expr: "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix} = \\begin{pmatrix} ax + by \\\\ cx + dy \\end{pmatrix}" },
    { name: "Sum", expr: "\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}" },
    { name: "Limit", expr: "\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1" },
    { name: "Derivative", expr: "\\frac{d}{dx}[x^n] = nx^{n-1}" }
  ];
  
  exampleBtn.addEventListener('click', () => {
    const example = examples[Math.floor(Math.random() * examples.length)];
    latexInput.value = example.expr;
    latexInput.focus();
  });
  
  clearBtn.addEventListener('click', () => {
    latexInput.value = '';
    resultCard.style.display = 'none';
    err.style.display = 'none';
    latexInput.focus();
  });
  
  newRenderBtn.addEventListener('click', () => {
    resultCard.style.display = 'none';
    latexInput.focus();
  });
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    err.style.display = 'none';
    resultCard.style.display = 'none';
    
    renderBtn.classList.add('loading');
    renderText.textContent = 'Rendering...';
    
    const formData = Object.fromEntries(new FormData(form).entries());
    const payload = { 
      latex_expression: formData.latex_expression, 
      dpi: formData.dpi ? Number(formData.dpi) : null 
    };
    
    try {
      const r = await authJson("POST", "/renderer/render", payload);
      
      renderedImg.src = r.image_url;
      downloadLink.href = r.image_url;
      downloadLink.download = `latex-render-${Date.now()}.png`;
      
      // Get image info
      renderedImg.onload = () => {
        const dpi = payload.dpi || 300;
        const width = Math.round(renderedImg.naturalWidth * 96 / dpi);
        const height = Math.round(renderedImg.naturalHeight * 96 / dpi);
        imageInfo.innerHTML = `
          <strong>Size:</strong> ${renderedImg.naturalWidth} × ${renderedImg.naturalHeight} pixels<br>
          <strong>DPI:</strong> ${dpi}<br>
          <strong>Screen Size:</strong> ${width} × ${height} pixels<br>
          <strong>Format:</strong> PNG
        `;
      };
      
      resultCard.style.display = 'block';
      
    } catch (ex) {
      err.textContent = ex.message || "Rendering error";
      err.style.display = 'block';
    } finally {
      renderBtn.classList.remove('loading');
      renderText.textContent = '🎨 Render';
    }
  });
  
  copyUrlBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(renderedImg.src);
    copyUrlBtn.textContent = '✅ Copied!';
    setTimeout(() => {
      copyUrlBtn.textContent = '📋 Copy Link';
    }, 2000);
  });
  
  return el;
}
