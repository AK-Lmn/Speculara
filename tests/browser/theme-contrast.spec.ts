import {test, expect} from '@playwright/test';
function luminance(c:number[]) { return c.map(v=>v/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0); }
function contrast(a:number[],b:number[]) { const x=luminance(a), y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); }
test('live primary gradients keep readable labels in every interaction state',async({page})=>{
 await page.goto('/', {waitUntil:'domcontentloaded'});
 await page.getByRole('button', {name:'Try synthetic demo data'}).click();
 await expect(page.getByRole('region', {name:'Dataset summary'})).toContainText('42 rows', {timeout:30000});
 await page.getByRole('button', {name:'Open chat',exact:true}).click();
 const buttons=await page.locator('.neu-btn:visible').all();
 expect(buttons.length).toBeGreaterThanOrEqual(3);
 for(const button of buttons) {
 for(const state of ['default','hover','focus','active']) {
  await page.mouse.move(0,0);
  if(state==='hover'||state==='active') await button.hover();
  if(state==='focus') { await page.keyboard.press('Tab'); await button.focus(); }
  if(state==='active') await page.mouse.down();
  const colors=await button.evaluate(el=>{const s=getComputedStyle(el);return {fg:s.color,bg:s.backgroundImage,outline:s.outlineStyle,focus:el.matches(':focus-visible'),active:el.matches(':active')};});
  const rgb=(s:string)=>s.match(/[\d.]+/g)!.slice(0,3).map(Number);
  const stops=colors.bg.match(/rgba?\([^)]+\)/g) || [];
  expect(stops.length,`${state} must inspect actual computed gradient`).toBeGreaterThanOrEqual(2);
  for(const stop of stops) expect(contrast(rgb(colors.fg),rgb(stop)),`${state}: ${stop}`).toBeGreaterThanOrEqual(7);
  if(state==='focus') { expect(colors.focus).toBe(true); expect(colors.outline).toBe('solid'); }
  if(state==='active') expect(colors.active).toBe(true);
  console.log(state,colors);
  if(state==='active') { await page.mouse.move(0,0); await page.mouse.up(); }
 }
 }
});
test('focus survives outline-none and sky outline utilities; secondary meets AAA',async({page})=>{
 await page.goto('/', {waitUntil:'domcontentloaded'});
 await page.evaluate(()=>{const b=document.createElement('button');b.id='focus-probe';b.className='outline-none focus-visible:outline-sky';b.textContent='Focus probe';document.body.append(b);});
 await page.locator('#focus-probe').focus();
 const sample=await page.locator('#focus-probe').evaluate(el=>{const s=getComputedStyle(el);return {style:s.outlineStyle,width:s.outlineWidth,color:s.outlineColor,surface:getComputedStyle(document.body).backgroundColor};});
 expect(sample.style).toBe('solid');expect(parseFloat(sample.width)).toBeGreaterThanOrEqual(3);
 const rgb=(s:string)=>s.match(/[\d.]+/g)!.slice(0,3).map(Number);
 expect(contrast(rgb(sample.color),rgb(sample.surface))).toBeGreaterThanOrEqual(3);
 const secondary=await page.locator('.text-slate-600').first().evaluate(el=>getComputedStyle(el).color);
 expect(contrast(rgb(secondary),rgb(sample.surface))).toBeGreaterThanOrEqual(7);
});

test('reduced motion disables animations and transitions',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto('/', {waitUntil:'domcontentloaded'});
 const motion=await page.locator('.neu-btn').last().evaluate(el=>{const s=getComputedStyle(el);return [s.transitionDuration,s.animationName];});
 expect(motion).toEqual(['0s','none']);
});

test('initial locked module list has a visible composited focus ring',async({page})=>{
 await page.goto('/', {waitUntil:'domcontentloaded'});
 const list=page.locator('ul.neu-scroll[tabindex="0"]');
 await page.keyboard.press('Tab');
 await list.focus();
 const sample=await list.evaluate(el=>{
  const style=getComputedStyle(el);
  let opacity=1;
  for(let node:Element|null=el;node;node=node.parentElement) opacity*=Number(getComputedStyle(node).opacity);
  return {focus:el.matches(':focus-visible'),outline:style.outlineColor,outlineStyle:style.outlineStyle,opacity,surface:getComputedStyle(document.body).backgroundColor};
 });
 expect(sample.focus).toBe(true);
 expect(sample.outlineStyle).toBe('solid');
 const rgb=(s:string)=>s.match(/[\d.]+/g)!.slice(0,3).map(Number);
 const surface=rgb(sample.surface);
 const composite=rgb(sample.outline).map((v,i)=>v*sample.opacity+surface[i]*(1-sample.opacity));
 const ratio=contrast(composite,surface);
 console.log('initial list focus', {...sample,composite,ratio});
 expect(ratio).toBeGreaterThanOrEqual(3);
 const buttons=await list.getByRole('button').all();
 expect(buttons).toHaveLength(6);
 for(const button of buttons) {
  await expect(button).toBeDisabled();
  expect(await button.evaluate(el=>Number(getComputedStyle(el).opacity))).toBeLessThan(1);
 }
});
