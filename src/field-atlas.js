import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createElement, Pause, Play, RotateCcw } from 'lucide';

const root = document.querySelector('[data-field-atlas]');
if (root) boot(root);

async function boot(root) {
    const canvas = root.querySelector('canvas');
    const motion = root.querySelector('[data-atlas-motion]');
    const reset = root.querySelector('[data-atlas-reset]');
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = media.matches;
    let visible = true;
    let disposed = false;
    let frame = 0;
    let previous = 0;
    let activeTime = 0;
    let model;
    let renderer;
    let timeout;
    const markers = [];
    const projection = new THREE.Vector3();

    const icon = (button, node) => {
        button.replaceChildren(createElement(node, { width: 18, height: 18, 'aria-hidden': 'true' }));
    };
    function updateMotion() {
        const label = paused ? 'Resume landscape motion' : 'Pause landscape motion';
        motion.setAttribute('aria-label', label);
        motion.title = label;
        motion.setAttribute('aria-pressed', String(paused));
        root.dataset.atlasPaused = String(paused);
        icon(motion, paused ? Play : Pause);
    }
    icon(reset, RotateCcw);
    updateMotion();

    if (new URLSearchParams(location.search).get('atlas') === 'static' || navigator.connection?.saveData) {
        root.dataset.atlasState = 'fallback';
        return;
    }

    try {
        // Keep a paused scene intact when the browser composites or captures it.
        renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power', preserveDrawingBuffer: true });
    } catch {
        root.dataset.atlasState = 'fallback';
        return;
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-14, 14, 11, -11, .1, 150);
    const home = new THREE.Vector3(15, 15, 18);
    camera.position.copy(home);
    const target = new THREE.Vector3(0, 1.1, 0);
    camera.lookAt(target);
    scene.add(new THREE.HemisphereLight(0xe4f4e9, 0x18231c, .85));
    const key = new THREE.DirectionalLight(0xffedd5, 2.5);
    key.position.set(-6, 12, 8);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: .5, far: 60 });
    key.shadow.bias = -.0003;
    key.shadow.normalBias = .035;
    scene.add(key);
    const rim = new THREE.DirectionalLight(0x65e4bb, .4);
    rim.position.set(8, 8, -5);
    scene.add(rim);

    const controls = new OrbitControls(camera, canvas);
    controls.target.copy(target);
    controls.enablePan = false;
    controls.enableZoom = false;
    controls.enableDamping = false;
    controls.rotateSpeed = .38;
    controls.minPolarAngle = .55;
    controls.maxPolarAngle = 1.2;
    controls.minAzimuthAngle = -.2;
    controls.maxAzimuthAngle = 1.6;
    canvas.style.touchAction = 'pan-y';
    controls.update();

    function resize() {
        const { width, height } = canvas.getBoundingClientRect();
        if (!width || !height) return;
        const aspect = width / height;
        const halfHeight = Math.max(8.5, 10.5 / aspect);
        camera.left = -halfHeight * aspect;
        camera.right = halfHeight * aspect;
        camera.top = halfHeight;
        camera.bottom = -halfHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
        render();
    }

    function render() {
        if (disposed || !model) return;
        renderer.render(scene, camera);
        markers.forEach(({ object, link }) => {
            object.getWorldPosition(projection).project(camera);
            link.style.left = `${(projection.x + 1) * 50}%`;
            link.style.top = `${(1 - projection.y) * 50}%`;
        });
        if (!root.dataset.atlasPixelSamples) {
            const gl = renderer.getContext();
            const pixel = new Uint8Array(4);
            let painted = 0;
            for (let x = 1; x < 6; x += 1) {
                for (let y = 1; y < 6; y += 1) {
                    gl.readPixels(Math.floor(canvas.width*x/6), Math.floor(canvas.height*y/6), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
                    if (pixel[3] > 0) painted += 1;
                }
            }
            root.dataset.atlasPixelSamples = String(painted);
        }
        root.dataset.atlasFrames = String(Number(root.dataset.atlasFrames || 0) + 1);
        root.dataset.atlasAngle = model.rotation.y.toFixed(5);
        root.dataset.atlasCamera = camera.position.toArray().map(n => n.toFixed(3)).join(',');
    }

    function tick(now) {
        frame = 0;
        if (disposed || paused || !visible || document.hidden || !model) return;
        if (previous) activeTime += Math.min((now - previous) / 1000, .1);
        previous = now;
        model.rotation.y = Math.sin(activeTime * .23) * .065;
        render();
        frame = requestAnimationFrame(tick);
    }

    function reconcile() {
        cancelAnimationFrame(frame);
        frame = 0;
        previous = 0;
        updateMotion();
        if (!disposed && !paused && visible && !document.hidden && model) frame = requestAnimationFrame(tick);
        else render();
    }

    const resetView = () => {
        camera.position.copy(home);
        controls.target.copy(target);
        if (model) model.rotation.y = 0;
        activeTime = 0;
        controls.update();
        render();
    };
    const onMedia = event => { paused = event.matches; reconcile(); };
    const onVisibility = () => reconcile();
    const onMotion = () => { paused = !paused; reconcile(); };
    const onKey = event => {
        if (event.key === 'Home') { event.preventDefault(); resetView(); return; }
        const step = { ArrowLeft: -.12, ArrowRight: .12, ArrowUp: -.08, ArrowDown: .08 }[event.key];
        if (step === undefined) return;
        event.preventDefault();
        const offset = camera.position.clone().sub(controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') spherical.theta += step;
        else spherical.phi += step;
        spherical.theta = THREE.MathUtils.clamp(spherical.theta, -.2, 1.6);
        spherical.phi = THREE.MathUtils.clamp(spherical.phi, .55, 1.2);
        camera.position.copy(controls.target).add(offset.setFromSpherical(spherical));
        controls.update();
        render();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);
    const intersection = new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        reconcile();
    }, { threshold: .05 });
    intersection.observe(root);
    controls.addEventListener('change', render);
    motion.addEventListener('click', onMotion);
    reset.addEventListener('click', resetView);
    canvas.addEventListener('keydown', onKey);
    media.addEventListener('change', onMedia);
    document.addEventListener('visibilitychange', onVisibility);

    function dispose() {
        if (disposed) return;
        disposed = true;
        clearTimeout(timeout);
        cancelAnimationFrame(frame);
        resizeObserver.disconnect();
        intersection.disconnect();
        controls.dispose();
        motion.removeEventListener('click', onMotion);
        reset.removeEventListener('click', resetView);
        canvas.removeEventListener('keydown', onKey);
        media.removeEventListener('change', onMedia);
        document.removeEventListener('visibilitychange', onVisibility);
        scene.traverse(object => {
            object.geometry?.dispose();
            const materials = Array.isArray(object.material) ? object.material : [object.material];
            materials.forEach(material => material?.dispose());
        });
        markers.forEach(({ link }) => link.remove());
        renderer.dispose();
        renderer.forceContextLoss();
    }

    const fallback = () => {
        root.dataset.atlasState = 'fallback';
        canvas.tabIndex = -1;
        dispose();
    };
    canvas.addEventListener('webglcontextlost', fallback, { once: true });
    window.addEventListener('pagehide', event => { if (!event.persisted) dispose(); }, { once: true });

    try {
        timeout = setTimeout(fallback, 20000);
        const gltf = await new GLTFLoader().loadAsync(root.dataset.model);
        clearTimeout(timeout);
        if (disposed) {
            gltf.scene.traverse(object => { object.geometry?.dispose(); object.material?.dispose?.(); });
            return;
        }
        model = gltf.scene;
        scene.add(model);
        model.traverse(object => {
            if (object.isMesh) {
                object.castShadow = /Field.?Atlas.?terrain/.test(object.name);
                object.receiveShadow = !/contour|route|datum|Station|Survey station/.test(object.name);
            }
            if (object.userData.href) {
                const link = document.createElement('a');
                link.className = 'atlas-marker';
                link.href = object.userData.href;
                link.textContent = object.userData.label;
                root.querySelector('.atlas-visual').append(link);
                markers.push({ object, link });
            }
        });
        canvas.tabIndex = 0;
        root.dataset.atlasState = 'ready';
        root.dataset.atlasMeshes = String(model.children.length);
        resize();
        reconcile();
    } catch {
        fallback();
    }
}
