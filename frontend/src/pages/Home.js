import { isAuthenticated } from "../auth.js";
import { createElement } from "../core/utils.js";

export default function Home() {
  const el = createElement("div", "grid");
  const isAuth = isAuthenticated();
  
  el.innerHTML = `
    <div style="text-align: center; margin-bottom: 40px;">
      <div class="h1" style="background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;">eye.math</div>
      <p class="muted" style="font-size: 18px; max-width: 600px; margin: 0 auto;">Open Source AI-powered mathematical problem solver. Recognition, solving and visualization in LaTeX at lightning speed.</p>
      <div style="display: flex; gap: 8px; justify-content: center; margin-top: 16px; flex-wrap: wrap;">
        <span class="tag" style="background: var(--primary); color: white; border-color: var(--primary);">Open Source</span>
        <span class="tag" style="background: var(--accent); color: white; border-color: var(--accent);">AI Powered</span>
        <span class="tag" style="background: #8b5cf6; color: white; border-color: #8b5cf6;">LaTeX Ready</span>
      </div>
    </div>
    
    <!-- Performance Metrics -->
    <div class="card" style="margin-bottom: 40px; background: linear-gradient(135deg, var(--surface), var(--elevated));">
      <h2 style="text-align: center; margin: 0 0 24px; color: var(--text);">Platform Performance</h2>
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px;">
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <div style="font-size: 32px; font-weight: 800; color: var(--primary); margin-bottom: 8px;">95%</div>
          <div style="color: var(--muted); font-size: 14px;">Recognition Accuracy</div>
        </div>
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <div style="font-size: 32px; font-weight: 800; color: var(--accent); margin-bottom: 8px;">&lt;2s</div>
          <div style="color: var(--muted); font-size: 14px;">Processing Time</div>
        </div>
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <div style="font-size: 32px; font-weight: 800; color: #8b5cf6; margin-bottom: 8px;">1000+</div>
          <div style="color: var(--muted); font-size: 14px;">Equations Solved</div>
        </div>
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <div style="font-size: 32px; font-weight: 800; color: #f59e0b; margin-bottom: 8px;">24/7</div>
          <div style="color: var(--muted); font-size: 14px;">Availability</div>
        </div>
      </div>
    </div>
    
    <!-- Demo Section -->
    <div class="card" style="margin-bottom: 40px;">
      <h2 style="text-align: center; margin: 0 0 24px; color: var(--text);">Live Demo</h2>
      <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 24px; align-items: center;">
        <div style="padding: 20px; background: var(--surface); border-radius: 12px; border: 2px dashed var(--border); text-align: center;">
          <div style="font-size: 48px; margin-bottom: 16px;">📷</div>
          <h4 style="margin: 0 0 8px; color: var(--text);">Input: Handwritten Math</h4>
          <p style="margin: 0; color: var(--muted); font-size: 14px;">Upload your handwritten equation</p>
        </div>
        <div style="padding: 20px; background: var(--surface); border-radius: 12px; border: 2px dashed var(--border); text-align: center;">
          <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
          <h4 style="margin: 0 0 8px; color: var(--text);">Output: LaTeX + Solution</h4>
          <p style="margin: 0; color: var(--muted); font-size: 14px;">Get instant recognition and solving</p>
        </div>
      </div>
    </div>
    
    ${isAuth ? `
    <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 40px;">
      <a class="card" href="#/recognize" style="text-decoration: none; transition: all 0.3s ease; border: 2px solid var(--border);">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">📷</div>
          <div>
            <h3 style="margin: 0; color: var(--text);">Recognition</h3>
            <p style="margin: 4px 0 0; color: var(--muted); font-size: 14px;">Image → LaTeX</p>
          </div>
        </div>
        <p style="color: var(--muted); margin: 0; line-height: 1.5;">Upload an image with a mathematical expression and get LaTeX code with high recognition accuracy.</p>
      </a>
      
      <a class="card" href="#/solve" style="text-decoration: none; transition: all 0.3s ease; border: 2px solid var(--border);">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--accent), var(--primary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">🧮</div>
          <div>
            <h3 style="margin: 0; color: var(--text);">Solving</h3>
            <p style="margin: 4px 0 0; color: var(--muted); font-size: 14px;">LaTeX → Solution</p>
          </div>
        </div>
        <p style="color: var(--muted); margin: 0; line-height: 1.5;">Enter a mathematical expression in LaTeX and get step-by-step solution with visualization.</p>
      </a>
      
      <a class="card" href="#/render" style="text-decoration: none; transition: all 0.3s ease; border: 2px solid var(--border);">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #8b5cf6, var(--primary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">🎨</div>
          <div>
            <h3 style="margin: 0; color: var(--text);">Rendering</h3>
            <p style="margin: 4px 0 0; color: var(--muted); font-size: 14px;">LaTeX → PNG</p>
          </div>
        </div>
        <p style="color: var(--muted); margin: 0; line-height: 1.5;">Convert LaTeX expressions into beautiful high-quality images for presentations.</p>
      </a>
    </div>
    ` : `
    <div style="text-align: center; margin: 60px 0; padding: 40px; background: var(--surface); border-radius: 16px; border: 1px solid var(--border);">
      <h2 style="margin: 0 0 16px; color: var(--text);">Get Started with eye.math</h2>
      <p style="margin: 0 0 24px; color: var(--muted); font-size: 16px; max-width: 500px; margin-left: auto; margin-right: auto;">
        Sign in or create an account to access all platform features.
      </p>
      <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
        <a href="#/login" class="btn" style="text-decoration: none;">
          🔑 Sign In
        </a>
        <a href="#/register" class="btn secondary" style="text-decoration: none;">
          📝 Create Account
        </a>
      </div>
    </div>
    `}
    
    <div style="margin-top: 60px; text-align: center; padding: 40px; background: var(--surface); border-radius: 16px; border: 1px solid var(--border);">
      <h2 style="margin: 0 0 16px; color: var(--text);">How It Works</h2>
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-top: 24px;">
        <div style="text-align: center;">
          <div style="width: 60px; height: 60px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: white; font-size: 24px;">1</div>
          <h4 style="margin: 0 0 8px; color: var(--text);">Upload</h4>
          <p style="margin: 0; color: var(--muted); font-size: 14px;">Take a photo or upload an image with a mathematical expression</p>
        </div>
        <div style="text-align: center;">
          <div style="width: 60px; height: 60px; background: var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: white; font-size: 24px;">2</div>
          <h4 style="margin: 0 0 8px; color: var(--text);">Recognize</h4>
          <p style="margin: 0; color: var(--muted); font-size: 14px;">AI recognizes the text and converts it to LaTeX code</p>
        </div>
        <div style="text-align: center;">
          <div style="width: 60px; height: 60px; background: #8b5cf6; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: white; font-size: 24px;">3</div>
          <h4 style="margin: 0 0 8px; color: var(--text);">Solve</h4>
          <p style="margin: 0; color: var(--muted); font-size: 14px;">Get step-by-step solution with visualization</p>
        </div>
      </div>
    </div>
    
    <!-- Contact & Open Source Section -->
    <div style="margin-top: 60px; text-align: center; padding: 40px; background: linear-gradient(135deg, var(--surface), var(--elevated)); border-radius: 16px; border: 1px solid var(--border);">
      <h2 style="margin: 0 0 16px; color: var(--text);">Open Source Project</h2>
      <p style="margin: 0 0 24px; color: var(--muted); font-size: 16px; max-width: 600px; margin-left: auto; margin-right: auto;">
        eye.math is an open source project. Contribute, report issues, or get in touch with the developer.
      </p>
      <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-bottom: 24px;">
        <a href="https://github.com/dagahan/EyeMath_backend_monorepository" target="_blank" class="btn" style="text-decoration: none; display: inline-flex; align-items: center; gap: 8px;">
          <span>🐙</span> GitHub Repository
        </a>
        <a href="https://t.me/usov_nikita" target="_blank" class="btn secondary" style="text-decoration: none; display: inline-flex; align-items: center; gap: 8px;">
          <span>📱</span> Telegram Contact
        </a>
      </div>
      <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
        <span class="tag" style="background: #24292e; color: white; border-color: #24292e;">MIT License</span>
        <span class="tag" style="background: #28a745; color: white; border-color: #28a745;">Contributions Welcome</span>
        <span class="tag" style="background: #0366d6; color: white; border-color: #0366d6;">Issues & Discussions</span>
      </div>
    </div>
  `;
  
  // Add hover effects
  const cards = el.querySelectorAll('.card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-4px)';
      card.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.15)';
      card.style.borderColor = 'var(--primary)';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
      card.style.boxShadow = 'none';
      card.style.borderColor = 'var(--border)';
    });
  });
  
  return el;
}
