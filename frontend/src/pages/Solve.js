import { authJson } from "../api/client.js";
import { exampleCategories, getRandomExample, getCategories, getExamplesForCategory } from "../examples.js";

export default function Solve(){
  const el = document.createElement("div");
  el.className = "grid";
  el.innerHTML = `
    <div style="text-align: center; margin-bottom: 32px;">
      <div class="h1">🧮 Mathematical Expression Solving</div>
      <p class="muted">Enter a mathematical expression in LaTeX and get step-by-step solution</p>
    </div>
    
    <div class="card">
      <h3 style="margin: 0 0 20px; color: var(--text);">Enter Expression</h3>
      
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
          placeholder="Enter mathematical expression in LaTeX format, e.g.: x^2 - 5x + 6 = 0"
          required
        ></textarea>
        
        <div style="margin: 20px 0; display: flex; gap: 16px; flex-wrap: wrap;">
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="show_solving_steps" checked />
            <span>Show solving steps</span>
          </label>
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="render_latex_expressions" checked />
            <span>Render LaTeX expressions</span>
          </label>
        </div>
        
        <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
          <button class="btn" type="submit" id="solveBtn">
            <span id="solveText">🧮 Solve</span>
          </button>
          <button class="btn secondary" type="button" id="clearBtn">
            🗑️ Clear
          </button>
          
          <!-- Examples Dropdown -->
          <div class="examples-dropdown" style="position: relative; display: inline-block;">
            <button class="btn secondary" type="button" id="examplesDropdownBtn">
              📝 Examples ▼
            </button>
            <div class="examples-menu" id="examplesMenu" style="display: none;">
              <div style="padding: 12px; border-bottom: 1px solid var(--border);">
                <input type="text" id="examplesSearch" placeholder="Search examples..." style="width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--elevated); color: var(--text); font-size: 14px;">
              </div>
              <div class="examples-categories" id="examplesCategories"></div>
            </div>
          </div>
        </div>
      </form>
      
      <div class="notice error" id="err" style="display:none"></div>
    </div>

    <div id="resultsContainer" style="display: none;">
      <div class="card" id="resultsCard">
        <h3 style="margin: 0 0 16px; color: var(--text);">Results</h3>
        <div id="results" style="display: flex; flex-wrap: wrap; gap: 8px;"></div>
      </div>
      
      <div class="card" id="stepsCard" style="display: none;">
        <h3 style="margin: 0 0 16px; color: var(--text);">Solving Steps</h3>
        <div id="steps"></div>
      </div>
      
      <div class="card" id="rendersCard" style="display: none;">
        <h3 style="margin: 0 0 16px; color: var(--text);">Visualization</h3>
        <div id="renders" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;"></div>
      </div>
    </div>
  `;
  
  const form = el.querySelector("#solveForm");
  const latexInput = el.querySelector("#latexInput");
  const solveBtn = el.querySelector("#solveBtn");
  const solveText = el.querySelector("#solveText");
  const clearBtn = el.querySelector("#clearBtn");
  const examplesDropdownBtn = el.querySelector("#examplesDropdownBtn");
  const examplesMenu = el.querySelector("#examplesMenu");
  const examplesCategories = el.querySelector("#examplesCategories");
  const examplesSearch = el.querySelector("#examplesSearch");
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
  
  // Initialize examples dropdown
  function initializeExamplesDropdown() {
    const categories = getCategories();
    examplesCategories.innerHTML = '';
    
    categories.forEach(category => {
      const categoryDiv = document.createElement('div');
      categoryDiv.className = 'examples-category';
      categoryDiv.dataset.category = category;
      
      const categoryHeader = document.createElement('div');
      categoryHeader.className = 'examples-category-header';
      categoryHeader.style.cssText = 'padding: 12px 16px; background: var(--elevated); border-bottom: 1px solid var(--border); cursor: pointer; font-weight: 600; color: var(--text); display: flex; justify-content: space-between; align-items: center;';
      categoryHeader.innerHTML = `${category} <span style="font-size: 12px;">▼</span>`;
      
      const examplesList = document.createElement('div');
      examplesList.className = 'examples-list';
      examplesList.style.cssText = 'display: none; max-height: 300px; overflow-y: auto;';
      
      const examples = getExamplesForCategory(category);
      examples.forEach(example => {
        const exampleItem = document.createElement('div');
        exampleItem.className = 'examples-item';
        exampleItem.dataset.name = example.name.toLowerCase();
        exampleItem.dataset.expr = example.expr.toLowerCase();
        exampleItem.style.cssText = 'padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background-color 0.2s;';

        exampleItem.innerHTML = `
          <div style="font-weight: 500; color: var(--text); margin-bottom: 4px;">${example.name}</div>
          <div style="font-size: 12px; color: var(--muted); font-family: monospace; background: var(--surface); padding: 4px 8px; border-radius: 4px; overflow-x: auto;">${example.expr}</div>
        `;
        
        exampleItem.addEventListener('click', () => {
          latexInput.value = example.expr;
          examplesMenu.style.display = 'none';
          examplesSearch.value = '';
          latexInput.focus();
        });
        
        exampleItem.addEventListener('mouseenter', () => {
          exampleItem.style.background = 'var(--elevated)';
        });
        
        exampleItem.addEventListener('mouseleave', () => {
          exampleItem.style.background = 'transparent';
        });
        
        examplesList.appendChild(exampleItem);
      });
      
      categoryHeader.addEventListener('click', () => {
        const isOpen = examplesList.style.display !== 'none';
        examplesList.style.display = isOpen ? 'none' : 'block';
        categoryHeader.querySelector('span').textContent = isOpen ? '▼' : '▲';
      });
      
      categoryDiv.appendChild(categoryHeader);
      categoryDiv.appendChild(examplesList);
      examplesCategories.appendChild(categoryDiv);
    });
  }
  
  // Examples dropdown functionality
  examplesDropdownBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = examplesMenu.style.display !== 'none';
    examplesMenu.style.display = isOpen ? 'none' : 'block';
    examplesDropdownBtn.innerHTML = isOpen ? '📝 Examples ▼' : '📝 Examples ▲';
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.examples-dropdown')) {
      examplesMenu.style.display = 'none';
      examplesDropdownBtn.innerHTML = '📝 Examples ▼';
    }
  });
  
  // Search functionality
  examplesSearch.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const categories = examplesCategories.querySelectorAll('.examples-category');
    
    categories.forEach(category => {
      const categoryName = category.dataset.category.toLowerCase();
      const examples = category.querySelectorAll('.examples-item');
      let hasVisibleExamples = false;
      
      examples.forEach(example => {
        const name = example.dataset.name;
        const expr = example.dataset.expr;
        
        if (searchTerm === '' || name.includes(searchTerm) || expr.includes(searchTerm) || categoryName.includes(searchTerm)) {
          example.style.display = 'block';
          hasVisibleExamples = true;
        } else {
          example.style.display = 'none';
        }
      });
      
      // Show/hide category based on whether it has visible examples
      if (hasVisibleExamples || searchTerm === '') {
        category.style.display = 'block';
        // Auto-expand categories when searching
        if (searchTerm !== '') {
          const examplesList = category.querySelector('.examples-list');
          const categoryHeader = category.querySelector('.examples-category-header span');
          examplesList.style.display = 'block';
          categoryHeader.textContent = '▲';
        }
      } else {
        category.style.display = 'none';
      }
    });
  });

  // Initialize the dropdown
  initializeExamplesDropdown();
  
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
    solveText.textContent = 'Solving...';
    
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
            <strong>Step ${i + 1}:</strong> ${step}
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
      err.textContent = ex.message || "Solving error";
      err.style.display = 'block';
    } finally {
      solveBtn.classList.remove('loading');
      solveText.textContent = '🧮 Solve';
    }
  });
  
  return el;
}
