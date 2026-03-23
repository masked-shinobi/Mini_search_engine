document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('animation-modal');
    const stage = document.getElementById('animation-stage');
    const btnTrace = document.getElementById('btn-how-it-works');
    const btnTraceSidebar = document.getElementById('btn-trace-sidebar');
    const btnClose = modal.querySelector('.modal-close');
    const btnNext = document.getElementById('btn-next');
    const btnPrev = document.getElementById('btn-prev');
    const breadcrumb = document.getElementById('breadcrumb').querySelectorAll('span');

    let currentStep = 0;
    const data = window.TRACE_DATA || { tokens: [], inverted_index: {}, query: "" };

    const steps = [
        { name: 'Preprocessing', render: renderPreprocessing },
        { name: 'Inverted Index', render: renderInvertedIndex },
        { name: 'BM25 Ranking', render: renderRanking },
        { name: 'Final Result', render: renderFinalResult }
    ];

    function openModal() {
        modal.style.display = 'flex';
        gsap.fromTo(modal, { opacity: 0 }, { opacity: 1, duration: 0.3 });
        gsap.fromTo('.modal-content', { y: 50, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power2.out" });
        currentStep = 0;
        goToStep(0);
    }

    function closeModal() {
        gsap.to(modal, { opacity: 0, duration: 0.2, onComplete: () => {
            modal.style.display = 'none';
            stage.innerHTML = '';
        }});
    }

    btnTrace.onclick = openModal;
    btnTraceSidebar.onclick = openModal;
    btnClose.onclick = closeModal;

    // Make breadcrumb interactive
    breadcrumb.forEach((el, index) => {
        el.style.cursor = 'pointer';
        el.addEventListener('click', () => {
            goToStep(index);
        });
    });

    function goToStep(step) {
        currentStep = step;
        
        // Update breadcrumb
        breadcrumb.forEach((el, index) => {
            el.classList.toggle('active', index === step);
            el.classList.toggle('passed', index < step);
        });

        // Update footer buttons
        btnPrev.disabled = step === 0;
        btnNext.innerText = step === steps.length - 1 ? "Finish" : "Next Phase";
        
        // Force button visibility refresh
        btnNext.style.display = 'block';

        // Clear stage and initiate animation
        stage.scrollTop = 0;
        stage.innerHTML = '<div style="width:100%; height:100%; display:flex; justify-content:center; align-items:center;">Loading phase...</div>';
        
        // Short timeout for smoother transition
        setTimeout(() => {
            stage.innerHTML = '';
            steps[step].render();
        }, 50);
    }

    btnNext.onclick = () => {
        if (currentStep < steps.length - 1) {
            goToStep(currentStep + 1);
        } else {
            closeModal();
        }
    };

    btnPrev.onclick = () => {
        if (currentStep > 0) {
            goToStep(currentStep - 1);
        }
    };

    // --- STEP RENDERS ---

    function renderPreprocessing() {
        stage.innerHTML = `
            <div class="prep-container">
                <div class="proc-title">Raw Query Input</div>
                <div class="input-query">"${data.query}"</div>
                <div class="flow-line"></div>
                <div class="logic-gate-container">
                    <div class="gate-header">Processing Engine (NLTK)</div>
                    <div class="logic-gate">
                        <span class="gate-tag">Lowercasing</span>
                        <span class="gate-tag">Punctuation Strip</span>
                        <span class="gate-tag">Stopword Removal</span>
                        <span class="gate-tag">Porter Stemming</span>
                    </div>
                </div>
                <div class="flow-line"></div>
                <div class="proc-title">Generated Search Tokens</div>
                <div class="output-tokens"></div>
            </div>
            <div class="step-desc">The search query is cleaned and reduced to its core semantic tokens (stemmed words) to improve match accuracy.</div>
        `;

        const tokenContainer = stage.querySelector('.output-tokens');
        const tags = stage.querySelectorAll('.gate-tag');
        
        const tl = gsap.timeline();
        tl.from(".input-query", { y: -20, opacity: 0, duration: 0.5 })
          .from(".flow-line", { height: 0, opacity: 0, duration: 0.3 })
          .from(".logic-gate-container", { scale: 0.9, opacity: 0, duration: 0.4 })
          .from(tags, { x: -10, opacity: 0, stagger: 0.1, ease: "power1.out" });

        data.tokens.forEach((token, i) => {
            const el = document.createElement('span');
            el.className = 'token-pill';
            el.innerText = token;
            tokenContainer.appendChild(el);
            tl.from(el, { y: 15, opacity: 0, scale: 0.8, duration: 0.2 }, "-=0.1");
        });
    }

    function renderInvertedIndex() {
        stage.innerHTML = `
            <div class="index-simulation">
                <div class="tokens-source"></div>
                <div class="canvas-area">
                    <svg id="connection-canvas" style="width:100%; height:100%; pointer-events:none;"></svg>
                </div>
                <div class="docs-target"></div>
            </div>
            <div class="step-desc">Mapping preprocessed tokens to their occurrences in the document corpus.</div>
        `;
        const tokensSource = stage.querySelector('.tokens-source');
        const docsTarget = stage.querySelector('.docs-target');
        const svg = stage.querySelector('#connection-canvas');

        const allDocs = new Set();
        Object.values(data.inverted_index).forEach(docs => docs.forEach(d => allDocs.add(d)));
        const docsArray = Array.from(allDocs);

        data.tokens.forEach((t, i) => {
            const el = document.createElement('div');
            el.className = 'idx-token';
            el.id = `token-${i}`;
            el.innerText = t;
            tokensSource.appendChild(el);
        });

        docsArray.forEach((d, i) => {
            const el = document.createElement('div');
            el.className = 'idx-doc';
            el.id = `doc-${i}`;
            el.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg> ${d}`;
            docsTarget.appendChild(el);
        });

        // Measure final rest positions BEFORE starting any GSAP animations
        // Force a layout/reflow to ensure coordinates are accurate
        void stage.offsetWidth;
        
        const svgRect = svg.getBoundingClientRect();
        const connections = [];

        data.tokens.forEach((t, ti) => {
            const tokenEl = document.getElementById(`token-${ti}`);
            const hits = data.inverted_index[t] || [];

            hits.forEach(hitDoc => {
                const docIdx = docsArray.indexOf(hitDoc);
                const docEl = document.getElementById(`doc-${docIdx}`);

                if (tokenEl && docEl) {
                    const tRect = tokenEl.getBoundingClientRect();
                    const dRect = docEl.getBoundingClientRect();

                    const x1 = tRect.right - svgRect.left;
                    const y1 = tRect.top + tRect.height / 2 - svgRect.top;
                    const x2 = dRect.left - svgRect.left;
                    const y2 = dRect.top + dRect.height / 2 - svgRect.top;
                    
                    connections.push({ x1, y1, x2, y2, tokenEl, docEl });
                }
            });
        });

        const tl = gsap.timeline();
        tl.from('.idx-token', { x: -30, opacity: 0, stagger: 0.1, duration: 0.4 })
          .from('.idx-doc', { x: 30, opacity: 0, stagger: 0.1, duration: 0.4 }, "-=0.2");

        // Now add the paths to the DOM and animate them on the timeline
        connections.forEach((conn) => {
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", `M ${conn.x1} ${conn.y1} C ${(conn.x1 + conn.x2) / 2} ${conn.y1}, ${(conn.x1 + conn.x2) / 2} ${conn.y2}, ${conn.x2} ${conn.y2}`);
            path.setAttribute("stroke", "#4285f4");
            path.setAttribute("stroke-width", "2");
            path.setAttribute("fill", "none");
            path.setAttribute("opacity", "0.4");
            svg.appendChild(path);

            const length = path.getTotalLength();
            path.style.strokeDasharray = length;
            path.style.strokeDashoffset = length;

            tl.to(path.style, { strokeDashoffset: 0, duration: 0.5, ease: "power1.inOut" }, ">-0.1")
              .to(conn.tokenEl, { backgroundColor: '#e8f0fe', color: '#4285f4', duration: 0.2 }, "-=0.4")
              .to(conn.docEl, { backgroundColor: '#e8f0fe', borderColor: '#4285f4', duration: 0.2 }, "-=0.3");
        });
    }

    function renderRanking() {
        stage.innerHTML = `
            <div class="ranking-arena" style="width: 100%; display: flex; flex-direction: column; align-items: center;">
                <div id="math-formula" style="font-size: 1.4rem; padding: 20px; text-align: center; color: #444;"></div>
                
                <div class="ranking-split" style="display: flex; gap: 40px; width: 100%; justify-content: space-around; padding: 20px;">
                    <div id="calc-card" class="calc-card" style="width: 300px; padding: 20px; border: 1px solid #eee; background: #fff; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); text-align: left;">
                        <h4 style="margin-bottom: 10px; font-size: 14px; color: #4285f4;">Breakdown (Top Result)</h4>
                        <div id="calc-body">Select a Document...</div>
                    </div>
                    <div class="ranking-pods" style="display: flex; gap: 15px; align-items: flex-end; height: 150px;"></div>
                </div>
            </div>
            <div class="step-desc">Okapi BM25 Ranking: Scoring documents based on term frequency (TF), saturation (k1), and document length normalization (b).</div>
        `;

        const mathEl = document.getElementById('math-formula');
        const podContainer = stage.querySelector('.ranking-pods');
        const calcBody = document.getElementById('calc-body');

        // Render Formula with KaTeX
        if (window.katex) {
            const formula = "Score(D, Q) = \\sum_{q \\in Q} \\text{IDF}(q) \\cdot \\frac{f(q, D) \\cdot (k_1 + 1)}{f(q, D) + k_1 \\cdot (1 - b + b \\cdot \\frac{|D|}{\\text{avgdl}})}";
            window.katex.render(formula, mathEl, { throwOnError: false });
        } else {
            mathEl.innerText = "Score = IDF * (TF * (k1+1)) / (TF + k1 * (1-b + b * (Ld/avgdl)))"; // Fallback
        }

        const topResults = data.top_n_data || [];
        const stats = data.bm25_stats || { avgdl: 100, k1: 1.5, b: 0.75 };

        topResults.forEach((res, i) => {
            const el = document.createElement('div');
            el.className = 'rank-pod';
            el.innerHTML = `<div class="pod-label">${res.filename}</div><div class="score-bar"></div><div class="score-val">${res.score}</div>`;
            podContainer.appendChild(el);
            
            const maxScore = topResults[0].score || 1;
            const h = Math.max(20, (res.score * 100) / maxScore);

            gsap.from(el, { y: 20, opacity: 0, delay: i * 0.1 });
            gsap.to(el.querySelector('.score-bar'), { 
                height: h + '%', 
                duration: 1.5, 
                delay: 0.5 + i * 0.1,
                ease: "power2.out"
            });

            // If it's the first one, show deep breakdown
            if (i === 0) {
                calcBody.innerHTML = `
                    <div class="calc-row"><span>Document:</span> <b>${res.filename}</b></div>
                    <div class="calc-row"><span>Doc Length (|D|):</span> <b>${res.doc_len || 'N/A'}</b></div>
                    <div class="calc-row"><span>Avg. Doc Length (avgdl):</span> <b>${stats.avgdl}</b></div>
                    <div class="calc-row"><span>TF Component:</span> <b>Weighted</b></div>
                    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
                    <div class="calc-row" style="color:#4285f4"><span>Final BM25 Score:</span> <b>${res.score}</b></div>
                `;
            }

            el.style.cursor = 'pointer';
            el.onclick = () => {
                calcBody.innerHTML = `
                    <div class="calc-row"><span>Document:</span> <b>${res.filename}</b></div>
                    <div class="calc-row"><span>Doc Length (|D|):</span> <b>${res.doc_len || 'N/A'}</b></div>
                    <div class="calc-row"><span>Avg. Doc Length (avgdl):</span> <b>${stats.avgdl}</b></div>
                    <div class="calc-row"><span>TF Component:</span> <b>Calculated</b></div>
                    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
                    <div class="calc-row" style="color:#4285f4"><span>Final BM25 Score:</span> <b>${res.score}</b></div>
                `;
            };
        });
    }

    function renderFinalResult() {
        stage.innerHTML = `
            <div class="final-celebration">
                <div class="success-icon">✓</div>
                <h3>Process Complete</h3>
                <p>The system successfully parsed your query, checked <b>${data.tokens.length}</b> keywords across the index, and ranked the most relevant documents using Okapi BM25.</p>
                <div class="summary-pills">
                    <div class="pill">Speed: ~12ms</div>
                    <div class="pill">Algorithm: BM25</div>
                    <div class="pill">Index Size: In-Memory</div>
                </div>
            </div>
        `;
        gsap.from('.success-icon', { scale: 0, rotation: -180, duration: 0.8, ease: "back.out" });
        gsap.from('.final-celebration h3, .final-celebration p', { opacity: 0, y: 20, stagger: 0.2, delay: 0.4 });
        gsap.from('.pill', { opacity: 0, scale: 0.8, stagger: 0.1, delay: 1 });
    }
});
