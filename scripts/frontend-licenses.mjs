import { readFile, writeFile } from 'node:fs/promises';
const packages = ['react', 'react-dom', 'scheduler', 'lucide-react', 'vite'];
const sections = await Promise.all(packages.map(async name => {
  const root = new URL(`../frontend/node_modules/${name}/`, import.meta.url);
  const meta = JSON.parse(await readFile(new URL('package.json', root), 'utf8'));
  const license = await readFile(new URL(name === 'vite' ? 'LICENSE.md' : 'LICENSE', root), 'utf8');
  return `${name} ${meta.version}\n${'='.repeat(60)}\n${license}`;
}));
await writeFile(new URL('../src/email_in_chat/static/LICENSES.txt', import.meta.url), sections.join('\n\n').replace(/[ \t]+$/gm, '').trimEnd() + '\n');
