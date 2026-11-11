import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
test('generated theme is present and current', () => {
 const result = spawnSync(process.execPath, ['scripts/build-tokens.mjs', '--check'], {encoding:'utf8'});
 assert.equal(result.status, 0, result.stderr || result.stdout);
});
import {mkdtempSync, mkdirSync, copyFileSync, appendFileSync, writeFileSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
test('check rejects stale output and generation rejects broken aliases',()=>{
 const fixture=mkdtempSync(join(tmpdir(),'speculara-tokens-'));
 try {
  for(const dir of ['scripts','tokens','src']) mkdirSync(join(fixture,dir));
  for(const file of ['scripts/build-tokens.mjs','tokens/speculara.json','src/tokens.css']) copyFileSync(file,join(fixture,file));
  const run=(...args:string[])=>spawnSync(process.execPath,['scripts/build-tokens.mjs',...args],{cwd:fixture,encoding:'utf8'});
  appendFileSync(join(fixture,'src/tokens.css'),'/* stale */');
  assert.equal(run('--check').status,1);
  assert.equal(run().status,0);
  assert.equal(run('--check').status,0);
  const path=join(fixture,'tokens/speculara.json');
  const data=JSON.parse(readFileSync(path,'utf8'));
  data.semantic.focus.$value='{missing.focus}';
  writeFileSync(path,JSON.stringify(data));
  assert.match(run().stderr,/Unknown token: missing.focus/);
  data.semantic.focus.$value='{semantic.focus}';
  writeFileSync(path,JSON.stringify(data));
  assert.match(run().stderr,/Circular token alias/);
 } finally { rmSync(fixture,{recursive:true,force:true}); }
});
