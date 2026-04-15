/* ========================================================
   E-Commerce Phishing Detector — Frontend Logic
   ======================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* -------- DOM References -------- */
  const urlInput = document.getElementById('url-input');
  const analyzeBtn = document.getElementById('analyze-btn');
  const resultContainer = document.getElementById('result-container');
  const resultBox = document.getElementById('result-box');
  const resultTitle = document.getElementById('result-title');
  const confidenceBadge = document.getElementById('confidence-badge');
  const explanationSection = document.getElementById('explanation-section');
  const explanationsList = document.getElementById('explanations-list');
  const rulesSection = document.getElementById('rules-section');
  const rulesList = document.getElementById('rules-list');
  const sampleButtons = document.querySelectorAll('.sample-btn');

  /* ========================================================
     DecryptedText — Vanilla JS port of the React component
     ======================================================== */
  class DecryptedText {
    constructor(element, options = {}) {
      this.el = element;
      this.text = options.text || element.textContent;
      this.speed = options.speed || 50;
      this.maxIterations = options.maxIterations || 10;
      this.sequential = options.sequential || false;
      this.revealDirection = options.revealDirection || 'start';
      this.useOriginalCharsOnly = options.useOriginalCharsOnly || false;
      this.characters = options.characters || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+';
      this.revealedClass = options.revealedClass || 'revealed';
      this.encryptedClass = options.encryptedClass || 'encrypted';
      this.animateOn = options.animateOn || 'hover';

      this.availableChars = this.useOriginalCharsOnly
        ? [...new Set(this.text.split(''))].filter(c => c !== ' ')
        : this.characters.split('');

      this.revealedIndices = new Set();
      this.isAnimating = false;
      this.isDecrypted = this.animateOn !== 'click';
      this.hasAnimated = false;
      this._interval = null;

      this._buildSpans();
      this._bindEvents();
    }

    /* Build individual <span> per character */
    _buildSpans() {
      this.el.innerHTML = '';
      this.spans = [];
      for (let i = 0; i < this.text.length; i++) {
        const span = document.createElement('span');
        span.textContent = this.text[i];
        span.className = this.isDecrypted ? this.revealedClass : this.encryptedClass;
        this.el.appendChild(span);
        this.spans.push(span);
      }
    }

    /* Bind hover / view events */
    _bindEvents() {
      if (this.animateOn === 'hover') {
        this.el.addEventListener('mouseenter', () => this._triggerHoverDecrypt());
        this.el.addEventListener('mouseleave', () => this._resetToPlainText());
      } else if (this.animateOn === 'view') {
        this._setupIntersectionObserver();
      }
    }

    _setupIntersectionObserver() {
      const observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting && !this.hasAnimated) {
              this.hasAnimated = true;
              this._triggerDecrypt();
            }
          });
        },
        { threshold: 0.1 }
      );
      observer.observe(this.el);
    }

    /* ---------- Animation methods ---------- */
    _randomChar() {
      return this.availableChars[Math.floor(Math.random() * this.availableChars.length)];
    }

    _shuffleDisplay() {
      for (let i = 0; i < this.text.length; i++) {
        if (this.text[i] === ' ') continue;
        if (this.revealedIndices.has(i)) {
          this.spans[i].textContent = this.text[i];
          this.spans[i].className = this.revealedClass;
        } else {
          this.spans[i].textContent = this._randomChar();
          this.spans[i].className = this.encryptedClass;
        }
      }
    }

    _getNextIndex() {
      const len = this.text.length;
      const size = this.revealedIndices.size;
      if (this.revealDirection === 'start') return size;
      if (this.revealDirection === 'end') return len - 1 - size;
      // center
      const mid = Math.floor(len / 2);
      const off = Math.floor(size / 2);
      const idx = size % 2 === 0 ? mid + off : mid - off - 1;
      if (idx >= 0 && idx < len && !this.revealedIndices.has(idx)) return idx;
      for (let i = 0; i < len; i++) { if (!this.revealedIndices.has(i)) return i; }
      return 0;
    }

    _triggerDecrypt() {
      if (this.isAnimating) return;
      this.revealedIndices.clear();
      this.isAnimating = true;
      this.isDecrypted = false;
      let iteration = 0;

      this._interval = setInterval(() => {
        if (this.sequential) {
          if (this.revealedIndices.size < this.text.length) {
            const idx = this._getNextIndex();
            this.revealedIndices.add(idx);
            this._shuffleDisplay();
          } else {
            this._finishDecrypt();
          }
        } else {
          this._shuffleDisplay();
          iteration++;
          if (iteration >= this.maxIterations) {
            this._finishDecrypt();
          }
        }
      }, this.speed);
    }

    _finishDecrypt() {
      clearInterval(this._interval);
      this.isAnimating = false;
      this.isDecrypted = true;
      // Show final text
      for (let i = 0; i < this.text.length; i++) {
        this.spans[i].textContent = this.text[i];
        this.spans[i].className = this.revealedClass;
      }
    }

    _triggerHoverDecrypt() {
      if (this.isAnimating) return;
      this.revealedIndices.clear();
      this.isDecrypted = false;
      this.isAnimating = true;
      let iteration = 0;

      this._interval = setInterval(() => {
        this._shuffleDisplay();
        iteration++;
        if (iteration >= this.maxIterations) {
          this._finishDecrypt();
        }
      }, this.speed);
    }

    _resetToPlainText() {
      clearInterval(this._interval);
      this.isAnimating = false;
      this.isDecrypted = true;
      this.revealedIndices.clear();
      for (let i = 0; i < this.text.length; i++) {
        this.spans[i].textContent = this.text[i];
        this.spans[i].className = this.revealedClass;
      }
    }
  }

  /* -------- Initialize DecryptedText elements -------- */
  document.querySelectorAll('[data-decrypt]').forEach(el => {
    const opts = {
      text: el.getAttribute('data-decrypt-text') || el.textContent,
      speed: parseInt(el.getAttribute('data-decrypt-speed')) || 50,
      maxIterations: parseInt(el.getAttribute('data-decrypt-iterations')) || 10,
      sequential: el.hasAttribute('data-decrypt-sequential'),
      revealDirection: el.getAttribute('data-decrypt-direction') || 'start',
      animateOn: el.getAttribute('data-decrypt-animate') || 'view',
      revealedClass: el.getAttribute('data-decrypt-revealed-class') || 'revealed',
      encryptedClass: el.getAttribute('data-decrypt-encrypted-class') || 'encrypted',
    };
    new DecryptedText(el, opts);
  });

  /* ========================================================
     Matrix Rain Canvas (subtle background)
     ======================================================== */
  const canvas = document.getElementById('matrix-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let w, h, columns, drops;
    const chars = '01アイウエオカキクケコサシスセソタチツテト';

    function initMatrix() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
      const fontSize = 14;
      columns = Math.floor(w / fontSize);
      drops = new Array(columns).fill(1);

      function draw() {
        ctx.fillStyle = 'rgba(5, 8, 15, 0.06)';
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#00ff8844';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
          const text = chars[Math.floor(Math.random() * chars.length)];
          ctx.fillText(text, i * fontSize, drops[i] * fontSize);
          if (drops[i] * fontSize > h && Math.random() > 0.975) {
            drops[i] = 0;
          }
          drops[i]++;
        }
        requestAnimationFrame(draw);
      }
      draw();
    }

    initMatrix();
    window.addEventListener('resize', () => {
      initMatrix();
    });
  }

  /* ========================================================
     Staggered fade-in for cards
     ======================================================== */
  const staggerObserver = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in-up');
          staggerObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.info-card, .sample-btn').forEach(el => {
    el.style.opacity = '0';
    staggerObserver.observe(el);
  });

  /* ========================================================
     URL Analysis
     ======================================================== */
  analyzeBtn.addEventListener('click', analyzeUrl);

  urlInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') analyzeUrl();
  });

  sampleButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const url = this.getAttribute('data-url');
      urlInput.value = url;

      // Pulse effect on the input
      urlInput.style.borderColor = 'var(--clr-primary-dim)';
      urlInput.style.boxShadow = '0 0 0 3px var(--clr-primary-glow)';
      setTimeout(() => {
        urlInput.style.borderColor = '';
        urlInput.style.boxShadow = '';
      }, 600);

      analyzeUrl();
    });
  });

  function analyzeUrl() {
    const url = urlInput.value.trim();

    if (!url) {
      showError('Please enter a URL');
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="loading"></span>Scanning...';

    fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url }),
    })
      .then(response => response.json())
      .then(data => displayResult(data))
      .catch(error => showError('Error analyzing URL: ' + error.message))
      .finally(() => {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = 'Scan URL';
      });
  }

  function displayResult(data) {
    resultContainer.classList.remove('hidden');
    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    resultBox.classList.remove('legitimate', 'phishing', 'not-ecommerce');

    if (data.result === 'Legitimate E-commerce Website') {
      resultBox.classList.add('legitimate');
    } else if (data.result === 'Phishing E-commerce Website') {
      resultBox.classList.add('phishing');
    } else {
      resultBox.classList.add('not-ecommerce');
    }

    resultTitle.textContent = data.result;

    const confidence = data.confidence || 0;
    confidenceBadge.textContent = `${confidence.toFixed(0)}% Confidence`;

    if (confidence >= 80) {
      confidenceBadge.className = 'confidence-badge high';
    } else if (confidence >= 50) {
      confidenceBadge.className = 'confidence-badge medium';
    } else {
      confidenceBadge.className = 'confidence-badge low';
    }

    /* Explanations */
    explanationsList.innerHTML = '';
    if (data.explanations && data.explanations.length > 0) {
      data.explanations.forEach((exp, i) => {
        const item = document.createElement('div');
        item.className = `explanation-item ${exp.type}`;
        item.style.animationDelay = `${i * 0.08}s`;
        item.classList.add('fade-in-up');

        const icons = {
          danger: '⛔',
          warning: '⚡',
          success: '✓',
          info: '◈',
        };

        item.innerHTML = `
          <h4>${icons[exp.type] || '◈'} ${exp.title}</h4>
          <p>${exp.description}</p>
        `;
        explanationsList.appendChild(item);
      });
    }

    /* Triggered Rules */
    rulesList.innerHTML = '';
    if (data.triggered_rules && data.triggered_rules.length > 0) {
      data.triggered_rules.forEach((rule, i) => {
        const item = document.createElement('div');
        item.className = 'rule-item';
        item.style.animationDelay = `${i * 0.06}s`;
        item.classList.add('fade-in-up');
        item.innerHTML = `
          <span class="severity ${rule.severity}">${rule.severity}</span>
          <span class="rule-name">${rule.rule}</span>
        `;
        rulesList.appendChild(item);
      });
    } else {
      rulesList.innerHTML =
        '<p style="color: var(--text-dim); font-family: var(--font-mono); font-size: 0.8rem;">No security rules triggered</p>';
    }
  }

  function showError(message) {
    resultContainer.classList.remove('hidden');
    resultBox.classList.remove('legitimate', 'phishing', 'not-ecommerce');
    resultBox.classList.add('not-ecommerce');
    resultTitle.textContent = 'Error';
    confidenceBadge.textContent = '';
    explanationsList.innerHTML = `<p style="color: var(--text-secondary);">${message}</p>`;
    rulesList.innerHTML = '';
  }
});
