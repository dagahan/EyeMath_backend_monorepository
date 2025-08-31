import { authJson } from "../api/client.js";

export default function Solve(){
  const el = document.createElement("div");
  el.className = "grid";
  el.innerHTML = `
    <div style="text-align: center; margin-bottom: 32px;">
      <div class="h1">🧮 Решение математических выражений</div>
      <p class="muted">Введите математическое выражение в LaTeX и получите пошаговое решение</p>
    </div>
    
    <div class="card">
      <h3 style="margin: 0 0 20px; color: var(--text);">Введите выражение</h3>
      
      <div class="toolbar">
        <button class="toolbar-btn" data-insert="x^2">x²</button>
        <button class="toolbar-btn" data-insert="\\sqrt{x}">√x</button>
        <button class="toolbar-btn" data-insert="\\frac{a}{b}">a/b</button>
        <button class="toolbar-btn" data-insert="\\int_{a}^{b}">∫</button>
        <button class="toolbar-btn" data-insert="\\sum_{i=1}^{n}">∑</button>
        <button class="toolbar-btn" data-insert="\\lim_{x \\to \\infty}">lim</button>
        <button class="toolbar-btn" data-insert="\\sin(x)">sin</button>
        <button class="toolbar-btn" data-insert="\\cos(x)">cos</button>
        <button class="toolbar-btn" data-insert="\\log(x)">log</button>
        <button class="toolbar-btn" data-insert="\\pi">π</button>
        <button class="toolbar-btn" data-insert="\\infty">∞</button>
        <button class="toolbar-btn" data-insert="\\alpha">α</button>
        <button class="toolbar-btn" data-insert="\\beta">β</button>
        <button class="toolbar-btn" data-insert="\\gamma">γ</button>
      </div>
      
      <form id="solveForm">
        <textarea 
          class="math-editor" 
          name="latex_expression" 
          id="latexInput"
          placeholder="Введите математическое выражение в LaTeX формате, например: x^2 - 5x + 6 = 0"
          required
        ></textarea>
        
        <div style="margin: 20px 0; display: flex; gap: 16px; flex-wrap: wrap;">
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="show_solving_steps" checked />
            <span>Показать шаги решения</span>
          </label>
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="render_latex_expressions" checked />
            <span>Рендерить LaTeX выражения</span>
          </label>
        </div>
        
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button class="btn" type="submit" id="solveBtn">
            <span id="solveText">🧮 Решить</span>
          </button>
          <button class="btn secondary" type="button" id="clearBtn">
            🗑️ Очистить
          </button>
          <button class="btn secondary" type="button" id="exampleBtn">
            📝 Примеры
          </button>
        </div>
      </form>
      
      <div class="notice error" id="err" style="display:none"></div>
    </div>

    <div id="resultsContainer" style="display: none;">
      <div class="card" id="resultsCard">
        <h3 style="margin: 0 0 16px; color: var(--text);">Результаты</h3>
        <div id="results" style="display: flex; flex-wrap: wrap; gap: 8px;"></div>
      </div>
      
      <div class="card" id="stepsCard" style="display: none;">
        <h3 style="margin: 0 0 16px; color: var(--text);">Шаги решения</h3>
        <div id="steps"></div>
      </div>
      
      <div class="card" id="rendersCard" style="display: none;">
        <h3 style="margin: 0 0 16px; color: var(--text);">Визуализация</h3>
        <div id="renders" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;"></div>
      </div>
    </div>
  `;
  
  const form = el.querySelector("#solveForm");
  const latexInput = el.querySelector("#latexInput");
  const solveBtn = el.querySelector("#solveBtn");
  const solveText = el.querySelector("#solveText");
  const clearBtn = el.querySelector("#clearBtn");
  const exampleBtn = el.querySelector("#exampleBtn");
  const err = el.querySelector("#err");
  const resultsContainer = el.querySelector("#resultsContainer");
  const resultsCard = el.querySelector("#resultsCard");
  const results = el.querySelector("#results");
  const stepsCard = el.querySelector("#stepsCard");
  const steps = el.querySelector("#steps");
  const rendersCard = el.querySelector("#rendersCard");
  const renders = el.querySelector("#renders");
  
  // Toolbar buttons
  const toolbarBtns = el.querySelectorAll('.toolbar-btn');
  toolbarBtns.forEach(btn => {
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
  });
  
  // Examples
  const examples = [
    { name: "Квадратное уравнение", expr: "x^2 - 5x + 6 = 0" },
    { name: "Интеграл", expr: "\\int_0^1 x^2 dx" },
    { name: "Производная", expr: "\\frac{d}{dx}(x^3 + 2x^2 - 5x + 1)" },
    { name: "Лимит", expr: "\\lim_{x \\to 0} \\frac{\\sin(x)}{x}" },
    { name: "Система уравнений", expr: "\\begin{cases} x + y = 5 \\\\ 2x - y = 1 \\end{cases}" }
  ];
  
  exampleBtn.addEventListener('click', () => {
    const example = examples[Math.floor(Math.random() * examples.length)];
    latexInput.value = example.expr;
    latexInput.focus();
  });
  
  clearBtn.addEventListener('click', () => {
    latexInput.value = '';
    resultsContainer.style.display = 'none';
    err.style.display = 'none';
    latexInput.focus();
  });
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    err.style.display = 'none';
    resultsContainer.style.display = 'none';
    resultsCard.style.display = 'none';
    stepsCard.style.display = 'none';
    rendersCard.style.display = 'none';
    
    solveBtn.classList.add('loading');
    solveText.textContent = 'Решение...';
    
    const data = Object.fromEntries(new FormData(form).entries());
    const payload = {
      latex_expression: data.latex_expression,
      show_solving_steps: !!data.show_solving_steps,
      render_latex_expressions: !!data.render_latex_expressions,
    };
    
    try {
      const r = await authJson("POST", "/solver/solve", payload);
      
      resultsContainer.style.display = 'block';
      
      // Results
      if (r.results?.length) {
        results.innerHTML = r.results.map(result => 
          `<div class="tag" style="background: var(--accent); color: white; font-size: 14px; padding: 8px 12px;">${result}</div>`
        ).join('');
        resultsCard.style.display = 'block';
      }
      
      // Steps
      if (r.solving_steps?.length) {
        steps.innerHTML = r.solving_steps.map((step, i) => 
          `<div class="step-item">
            <strong>Шаг ${i + 1}:</strong> ${step}
          </div>`
        ).join('');
        stepsCard.style.display = 'block';
      }
      
      // Renders
      if (r.renders_urls?.length) {
        renders.innerHTML = r.renders_urls.map(url => 
          `<div style="text-align: center;">
            <img src="${url}" style="max-width: 100%; border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
          </div>`
        ).join('');
        rendersCard.style.display = 'block';
      }
      
    } catch (ex) {
      err.textContent = ex.message || "Ошибка решения";
      err.style.display = 'block';
    } finally {
      solveBtn.classList.remove('loading');
      solveText.textContent = '🧮 Решить';
    }
  });
  
  return el;
}
