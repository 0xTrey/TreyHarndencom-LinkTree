(function () {
    'use strict';

    const root = document.querySelector('[data-hero-field]');
    const canvas = root?.querySelector('.hero-field-canvas');
    const toggle = root?.querySelector('[data-hero-motion-toggle]');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    if (!root || !canvas) return;

    const gl = canvas.getContext('webgl', {
        alpha: true,
        antialias: false,
        depth: false,
        powerPreference: 'high-performance',
    });

    function updateToggle(paused, unsupported = false) {
        if (!toggle) return;

        const label = toggle.querySelector('.sr-only');
        const nextLabel = unsupported
            ? 'Ambient motion unavailable'
            : paused
                ? 'Resume ambient motion'
                : 'Pause ambient motion';

        toggle.disabled = unsupported;
        toggle.setAttribute('aria-pressed', String(paused));
        toggle.setAttribute('title', nextLabel);
        toggle.dataset.unsupported = String(unsupported);
        if (label) label.textContent = nextLabel;
    }

    if (!gl) {
        canvas.hidden = true;
        root.dataset.heroFieldReady = 'false';
        updateToggle(true, true);
        return;
    }

    const rippleCount = 16;
    const vertexSource = [
        'attribute vec2 aPosition;',
        'varying vec2 vUv;',
        'void main(){',
        '  vUv = aPosition * 0.5 + 0.5;',
        '  gl_Position = vec4(aPosition, 0.0, 1.0);',
        '}',
    ].join('\n');

    const fragmentSource = [
        'precision highp float;',
        'varying vec2 vUv;',
        'uniform vec2 uResolution;',
        'uniform float uTime;',
        `uniform vec4 uRipples[${rippleCount}];`,
        `uniform vec2 uFlowVelocity[${rippleCount}];`,
        'float gridLine(vec2 uv){',
        '  vec2 cell = abs(fract(uv) - 0.5);',
        '  float edge = max(cell.x, cell.y);',
        '  return smoothstep(0.465, 0.498, edge);',
        '}',
        'void main(){',
        '  float aspect = uResolution.x / max(uResolution.y, 1.0);',
        '  vec2 displacement = vec2(0.0);',
        '  float flowGlow = 0.0;',
        `  for(int i = 0; i < ${rippleCount}; i++){`,
        '    vec4 ripple = uRipples[i];',
        '    vec2 velocity = uFlowVelocity[i];',
        '    float age = uTime - ripple.z;',
        '    if(age > 0.0 && age < 3.25 && ripple.w > 0.0){',
        '      float fadeOut = 1.0 - smoothstep(2.03, 3.13, age);',
        '      float decay = exp(-age * 0.8965) * fadeOut;',
        '      vec2 carriedOrigin = ripple.xy + velocity * age * 0.0288;',
        '      vec2 flowDelta = (vUv - carriedOrigin) * vec2(aspect, 1.0);',
        '      vec2 direction = normalize(velocity + vec2(0.0001));',
        '      vec2 tangent = vec2(-direction.y, direction.x);',
        '      float alongFlow = dot(flowDelta, direction);',
        '      float acrossFlow = dot(flowDelta, tangent);',
        '      float velocityAmount = clamp(length(velocity) * 1.8, 0.0, 1.0);',
        '      float broadWake = exp(-(alongFlow * alongFlow * 5.0 + acrossFlow * acrossFlow * 70.2));',
        '      float wakeCore = exp(-(alongFlow * alongFlow * 9.1 + acrossFlow * acrossFlow * 179.4));',
        '      float curl = sin(alongFlow * 18.0 - acrossFlow * 11.0 + age * 1.8);',
        '      float flow = (broadWake * 0.82 + wakeCore * 0.18) * decay * ripple.w * (0.72 + velocityAmount * 0.28);',
        '      vec2 flowVector = direction * (0.76 + curl * 0.1) + tangent * (0.14 + curl * 0.24);',
        '      displacement += flowVector * flow * 0.01092;',
        '      flowGlow += (broadWake * 0.58 + wakeCore * 0.32) * decay * ripple.w * velocityAmount;',
        '    }',
        '  }',
        '  displacement *= min(1.0, 0.06 / max(length(displacement), 0.0001));',
        '  vec2 uv = vUv + displacement;',
        '  float currentA = sin(uv.x * 13.0 + sin(uv.y * 8.0 + uTime * 0.18) * 1.4 + uTime * 0.24);',
        '  float currentB = sin(uv.y * 16.0 - sin(uv.x * 7.0 - uTime * 0.14) * 1.6 - uTime * 0.19);',
        '  vec2 idleWarp = vec2(currentA, currentB) * 0.0035;',
        '  vec2 tiledUv = (uv + idleWarp) * vec2(7.2, 5.2);',
        '  float tile = gridLine(tiledUv);',
        '  float causticA = abs(sin((uv.x * 8.0 + sin(uv.y * 9.0 + uTime * 0.22)) * 2.2));',
        '  float causticB = abs(sin((uv.y * 7.0 - sin(uv.x * 11.0 - uTime * 0.16)) * 2.0));',
        '  float caustic = pow(max(0.0, 1.0 - abs(causticA - causticB)), 8.0);',
        '  vec3 deep = vec3(0.004, 0.018, 0.014);',
        '  vec3 mid = vec3(0.008, 0.16, 0.115);',
        '  vec3 glow = vec3(0.03, 0.87, 0.68);',
        '  float depthGradient = smoothstep(-0.1, 1.05, uv.y);',
        '  vec3 color = mix(deep, mid, depthGradient * 0.72);',
        '  color += glow * caustic * 0.07;',
        '  color += glow * tile * 0.055;',
        '  float liquidWake = min(0.62, 1.0 - exp(-flowGlow * 0.42));',
        '  color += glow * liquidWake * 0.36;',
        '  float vignette = 1.0 - smoothstep(0.28, 0.86, length((vUv - 0.5) * vec2(0.8, 1.0)));',
        '  color *= 0.66 + vignette * 0.42;',
        '  gl_FragColor = vec4(color, 1.0);',
        '}',
    ].join('\n');

    function compile(type, source) {
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            throw new Error(gl.getShaderInfoLog(shader) || 'Shader compilation failed');
        }
        return shader;
    }

    let program;
    try {
        program = gl.createProgram();
        gl.attachShader(program, compile(gl.VERTEX_SHADER, vertexSource));
        gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fragmentSource));
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            throw new Error(gl.getProgramInfoLog(program) || 'Shader link failed');
        }
    } catch (error) {
        canvas.hidden = true;
        root.dataset.heroFieldReady = 'false';
        updateToggle(true, true);
        return;
    }

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    gl.useProgram(program);

    const position = gl.getAttribLocation(program, 'aPosition');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

    const resolutionUniform = gl.getUniformLocation(program, 'uResolution');
    const timeUniform = gl.getUniformLocation(program, 'uTime');
    const rippleUniform = gl.getUniformLocation(program, 'uRipples[0]');
    const flowVelocityUniform = gl.getUniformLocation(program, 'uFlowVelocity[0]');
    const ripples = new Float32Array(rippleCount * 4);
    const flowVelocities = new Float32Array(rippleCount * 2);
    const startTime = performance.now();

    let rippleIndex = 0;
    let lastPoint = null;
    let lastWakeTime = 0;
    let frame = 0;
    let running = false;
    let inView = true;
    let userPaused = reduceMotion.matches;

    function clearWake() {
        for (let index = 0; index < rippleCount; index += 1) {
            const rippleOffset = index * 4;
            const velocityOffset = index * 2;
            ripples[rippleOffset + 2] = -1000;
            flowVelocities[velocityOffset] = 0;
            flowVelocities[velocityOffset + 1] = 0;
        }
    }

    function elapsed(now) {
        return (now - startTime) / 1000;
    }

    function resize() {
        const bounds = root.getBoundingClientRect();
        const density = Math.min(window.devicePixelRatio || 1, 1.35);
        const width = Math.max(1, Math.round(bounds.width * density));
        const height = Math.max(1, Math.round(bounds.height * density));
        if (canvas.width === width && canvas.height === height) return;

        canvas.width = width;
        canvas.height = height;
        gl.viewport(0, 0, width, height);
        gl.uniform2f(resolutionUniform, width, height);
    }

    function addWake(x, y, strength, now, velocityX, velocityY) {
        const offset = rippleIndex * 4;
        ripples[offset] = x;
        ripples[offset + 1] = y;
        ripples[offset + 2] = elapsed(now);
        ripples[offset + 3] = Math.min(1.45, Math.max(0.28, strength));

        const velocityOffset = rippleIndex * 2;
        flowVelocities[velocityOffset] = velocityX || 0;
        flowVelocities[velocityOffset + 1] = velocityY || 0;
        rippleIndex = (rippleIndex + 1) % rippleCount;
        root.dataset.heroFieldWakeCount = String(Number(root.dataset.heroFieldWakeCount || '0') + 1);
    }

    function shouldAnimate() {
        return !userPaused && inView && !document.hidden;
    }

    function render(now) {
        resize();
        gl.uniform1f(timeUniform, elapsed(now));
        gl.uniform4fv(rippleUniform, ripples);
        gl.uniform2fv(flowVelocityUniform, flowVelocities);
        gl.drawArrays(gl.TRIANGLES, 0, 6);

        if (shouldAnimate()) {
            frame = window.requestAnimationFrame(render);
            return;
        }

        running = false;
    }

    function reconcileAnimation() {
        updateToggle(userPaused);

        if (shouldAnimate()) {
            if (!running) {
                running = true;
                frame = window.requestAnimationFrame(render);
            }
            return;
        }

        window.cancelAnimationFrame(frame);
        running = false;
        render(performance.now());
    }

    function onPointerMove(event) {
        if (!shouldAnimate() || event.pointerType === 'touch') return;

        const now = performance.now();
        const bounds = root.getBoundingClientRect();
        const point = {
            x: event.clientX - bounds.left,
            y: event.clientY - bounds.top,
        };

        if (!lastPoint) {
            lastPoint = point;
            lastWakeTime = now;
            return;
        }

        const dx = point.x - lastPoint.x;
        const dy = point.y - lastPoint.y;
        const distance = Math.sqrt((dx * dx) + (dy * dy));
        if (distance < 10 && now - lastWakeTime <= 42) return;

        const directionScale = distance > 0 ? Math.min(distance / 34, 1) / distance : 0;
        addWake(
            point.x / Math.max(bounds.width, 1),
            1 - (point.y / Math.max(bounds.height, 1)),
            0.4 + Math.min(distance / 52, 0.72),
            now,
            dx * directionScale,
            -dy * directionScale,
        );
        lastPoint = point;
        lastWakeTime = now;
    }

    clearWake();
    root.dataset.heroFieldReady = 'true';
    root.dataset.heroFieldWakeCount = '0';
    resize();
    gl.clearColor(0.004, 0.018, 0.014, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    root.addEventListener('pointermove', onPointerMove, { passive: true });
    root.addEventListener('pointerleave', () => { lastPoint = null; }, { passive: true });
    toggle?.addEventListener('click', () => {
        userPaused = !userPaused;
        reconcileAnimation();
    });
    reduceMotion.addEventListener?.('change', event => {
        userPaused = event.matches;
        reconcileAnimation();
    });
    document.addEventListener('visibilitychange', reconcileAnimation);

    if ('ResizeObserver' in window) {
        new ResizeObserver(() => {
            resize();
            if (!running) render(performance.now());
        }).observe(root);
    } else {
        window.addEventListener('resize', () => {
            resize();
            if (!running) render(performance.now());
        }, { passive: true });
    }

    if ('IntersectionObserver' in window) {
        new IntersectionObserver(entries => {
            inView = entries[0]?.isIntersecting ?? true;
            reconcileAnimation();
        }, { threshold: 0.08 }).observe(root);
    }

    addWake(0.68, 0.36, 0.86, performance.now(), -0.58, 0.16);
    reconcileAnimation();
}());
