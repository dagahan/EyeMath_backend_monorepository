// /src/logo.js — СИЛУЭТ + ШИММЕР
(async () => {
  const canvas = document.getElementById("cornerLogo");
  const ctx = canvas.getContext("2d");
  const svgUrl = "/src/icons/portrait.svg"; // проверь путь под твой дев-сервер

  // Геометрия: внутренние поля и бокс для логотипа (в относительных долях)
  const INSET_X = 0.12, INSET_Y = 0.14;
  const BOX_W = 0.76,   BOX_H = 0.72;

  // 1) Грузим SVG в <img>
  const svgText = await fetch(svgUrl).then(r => {
    if (!r.ok) throw new Error(`SVG fetch failed: ${r.status}`);
    return r.text();
  });
  const svgDoc = new DOMParser().parseFromString(svgText, "image/svg+xml");
  const svgEl = svgDoc.documentElement;

  // viewBox (нужен, чтобы правильно вписать)
  const vb = (svgEl.getAttribute("viewBox") || "").trim().split(/\s+/).map(Number);
  let vbX = 0, vbY = 0, vbW = 100, vbH = 100;
  if (vb.length === 4 && vb.every(Number.isFinite)) [vbX, vbY, vbW, vbH] = vb;
  else {
    vbW = parseFloat(svgEl.getAttribute("width"))  || 100;
    vbH = parseFloat(svgEl.getAttribute("height")) || 100;
  }

  const img = new Image();
  const blob = new Blob([svgText], { type: "image/svg+xml" });
  const url  = URL.createObjectURL(blob);
  img.decoding = "async";
  img.src = url;
  await img.decode();

  // 2) Маска-силуэт на отдельном оффскрин-канвасе (белый силуэт на прозрачном фоне)
  let maskCanvas = document.createElement("canvas");
  let maskCtx    = maskCanvas.getContext("2d", { willReadFrequently: false });

  function rebuildMask() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    maskCanvas.width  = w; maskCanvas.height = h;
    maskCtx.setTransform(1,0,0,1,0,0);
    maskCtx.clearRect(0,0,w,h);

    // внутренние поля карточки
    const insetX = w * INSET_X, insetY = h * INSET_Y;
    const boxW   = w * BOX_W,   boxH   = h * BOX_H;

    // вписываем SVG по центру
    const scale = Math.min(boxW / vbW, boxH / vbH);
    const dw = vbW * scale, dh = vbH * scale;
    const dx = insetX + (boxW - dw)/2 - vbX * scale;
    const dy = insetY + (boxH - dh)/2 - vbY * scale;

    // рисуем SVG-картинку
    maskCtx.drawImage(img, dx, dy, dw, dh);

    // превратим картинку в ЧИСТЫЙ БЕЛЫЙ силуэт, сохранив альфу
    maskCtx.globalCompositeOperation = "source-in";
    maskCtx.fillStyle = "#fff";
    maskCtx.fillRect(0,0,w,h);
    maskCtx.globalCompositeOperation = "source-over";
  }

  // 3) HiDPI-скейл основного канваса
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth, h = canvas.clientHeight;
    canvas.width  = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    rebuildMask();
  }
  resize();
  addEventListener("resize", resize);

  // 4) Анимация
  let speed = 0.06, hoverBoost = 1;
  canvas.parentElement.addEventListener("pointerenter", () => hoverBoost = 1.8);
  canvas.parentElement.addEventListener("pointerleave", () => hoverBoost = 1);

  // helper: рисуем слой «подложки» и возвращаем его как картинку, уже обрезанную маской
  function buildMaskedLayer(painter) {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    const layer = document.createElement("canvas");
    layer.width = w; layer.height = h;
    const lctx = layer.getContext("2d");
    painter(lctx, w, h);                   // 1) рисуем что угодно
    lctx.globalCompositeOperation = "destination-in";
    lctx.drawImage(maskCanvas, 0, 0);      // 2) обрезаем по маске
    lctx.globalCompositeOperation = "source-over";
    return layer;
  }

  function frame(now) {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    ctx.clearRect(0,0,w,h);

    // фон карточки (еле заметный вертикальный градиент)
    const bg = ctx.createLinearGradient(0,0,0,h);
    bg.addColorStop(0,"rgba(255,255,255,0.06)");
    bg.addColorStop(1,"rgba(255,255,255,0.00)");
    ctx.fillStyle = bg;
    ctx.fillRect(0,0,w,h);

    // === 1) СКОЛЬЗЯЩИЙ БЛИК внутри силуэта ===
    const t = (now * speed * hoverBoost) % 2000;
    const stripeX = (t / 2000) * (w + 200) - 100;

    const shimmerLayer = buildMaskedLayer((lctx, W, H) => {
      const grad = lctx.createLinearGradient(stripeX - 100, 0, stripeX + 100, 0);
      grad.addColorStop(0.00, "rgba(255,255,255,0)");
      grad.addColorStop(0.40, "rgba(255,255,255,0)");
      grad.addColorStop(0.47, "rgba(255,120,0,0.55)");
      grad.addColorStop(0.50, "rgba(255,255,255,0.95)");
      grad.addColorStop(0.53, "rgba(90,180,255,0.55)");
      grad.addColorStop(0.60, "rgba(255,255,255,0)");
      grad.addColorStop(1.00, "rgba(255,255,255,0)");
      lctx.fillStyle = grad;
      lctx.fillRect(0,0,W,H);
    });
    // кладём блик сверху
    ctx.globalCompositeOperation = "source-over";
    ctx.drawImage(shimmerLayer, 0, 0);

    // === 2) МЕТАЛЛИЧЕСКАЯ ПОДЛОЖКА позади силуэта ===
    const baseLayer = buildMaskedLayer((lctx, W, H) => {
      const base = lctx.createLinearGradient(0,0,0,H);
      base.addColorStop(0,"rgba(255,255,255,0.65)");
      base.addColorStop(1,"rgba(255,255,255,0.28)");
      lctx.fillStyle = base;
      lctx.fillRect(0,0,W,H);
    });
    ctx.globalCompositeOperation = "destination-over";
    ctx.drawImage(baseLayer, 0, 0);

    // === 3) МЯГКОЕ СВЕЧЕНИЕ вокруг силуэта (только glow, без заливки!) ===
    ctx.globalCompositeOperation = "destination-over";
    ctx.filter = "blur(10px)";
    ctx.globalAlpha = 0.27;
    ctx.drawImage(maskCanvas, 0, 0);  // белый силуэт размывается позади
    ctx.filter = "none";
    ctx.globalAlpha = 1;

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();