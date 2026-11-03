import { build } from 'esbuild';
import { copyFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
await build({
    absWorkingDir: root,
    entryPoints: ['src/field-atlas.js'],
    bundle: true,
    minify: true,
    format: 'esm',
    target: 'es2022',
    outfile: 'static/js/field-atlas.js',
    legalComments: 'linked',
});
for (const dependency of ['three', 'lucide']) {
    await copyFile(new URL(`../node_modules/${dependency}/LICENSE`, import.meta.url),
        new URL(`../static/js/field-atlas.LICENSE-${dependency}.txt`, import.meta.url));
}
console.log('Built Field Atlas bundle and retained dependency licenses.');
