import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const source = (await readFile(new URL('../src/field-atlas.js', import.meta.url), 'utf8'))
    .replace(/^import .*;\n/gm, '');

for (const mode of ['unsupported', 'static', 'save-data']) {
    let rendererCalls = 0;
    const button = () => ({ setAttribute() {}, replaceChildren() {} });
    const canvas = { tabIndex: -1 };
    const controls = [button(), button()];
    const root = {
        dataset: {},
        querySelector(selector) {
            return selector === 'canvas' ? canvas : selector === '[data-atlas-motion]' ? controls[0] : controls[1];
        },
    };
    const context = {
        document: { querySelector: () => root },
        matchMedia: () => ({ matches: false }),
        THREE: {
            Vector3: class {},
            WebGLRenderer: class { constructor() { rendererCalls += 1; throw new Error('WebGL unavailable'); } },
        },
        URLSearchParams,
        location: { search: mode === 'static' ? '?atlas=static' : '' },
        navigator: { connection: { saveData: mode === 'save-data' } },
        createElement: () => ({}), Pause: [], Play: [], RotateCcw: [],
    };
    vm.runInNewContext(source, context);
    assert.equal(root.dataset.atlasState, 'fallback', mode);
    assert.equal(canvas.tabIndex, -1, mode);
    assert.equal(rendererCalls, mode === 'unsupported' ? 1 : 0, mode);
}
console.log('PASS: WebGL unavailable, explicit static mode, and data-saver fallback');
