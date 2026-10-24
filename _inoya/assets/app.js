/* HOUSE OF INOYA — 共通スクリプト
   ヒーローのある/ないページ、どちらでも動くようにガードしてあります。 */
(()=>{
  const $=(s,c=document)=>c.querySelector(s),$$=(s,c=document)=>[...c.querySelectorAll(s)];
  const root=document.documentElement,reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Menu ── */
  const header=$('.header'),menu=$('.menu'),nav=$('.nav');
  if(menu&&nav){
    const setNav=open=>{
      menu.setAttribute('aria-expanded',String(open));
      menu.setAttribute('aria-label',open?'メニューを閉じる':'メニューを開く');
      nav.classList.toggle('open',open);
      nav.setAttribute('aria-hidden',String(!open));
      nav.inert=!open;
      root.classList.toggle('nav-open',open);
    };
    menu.addEventListener('click',()=>setNav(menu.getAttribute('aria-expanded')!=='true'));
    $$('a',nav).forEach(a=>a.addEventListener('click',()=>setNav(false)));
    addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){setNav(false);menu.focus()}});
  }

  /* ── 現在ページをナビに反映 ── */
  const here=(location.pathname.split('/').pop()||'index.html').toLowerCase()||'index.html';
  $$('.nav a[href]').forEach(a=>{
    const t=a.getAttribute('href').split('/').pop().toLowerCase();
    if(t===here)a.setAttribute('aria-current','page');
  });

  /* ── Headline line masks (split at <br>) ── */
  $$('[data-lines]').forEach(el=>{
    el.innerHTML=el.innerHTML.split(/<br\s*\/?>/i).map((t,i)=>`<span class="ln"><span class="ln-in" style="--i:${i}">${t}</span></span>`).join('');
  });

  /* ── Stagger siblings ── */
  $$('.reveal').forEach(el=>{
    const i=$$(':scope > .reveal',el.parentElement).indexOf(el);
    if(i>0)el.style.setProperty('--d',Math.min(i,4)*.09+'s');
  });

  /* ── Reveal on scroll ── */
  const targets=$$('.reveal,[data-lines],.statement,.flow,.section-label,.page-head');
  if(reduce||!('IntersectionObserver' in window)){targets.forEach(el=>el.classList.add('on'))}
  else{
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}}),{threshold:.15,rootMargin:'0px 0px -6% 0px'});
    targets.forEach(el=>io.observe(el));
  }
  /* ページ見出しは最初から見えている位置にあるので即時 */
  const ph=$('.page-head'); if(ph)requestAnimationFrame(()=>ph.classList.add('on'));

  /* ── Scroll: progress bar / header / parallax ── */
  const hero=$('.hero'),statement=$('.statement'),progress=$('.progress');
  let raf=0;
  function update(){
    raf=0;
    const y=scrollY,max=root.scrollHeight-innerHeight;
    if(progress)progress.style.transform=`scaleX(${max>0?Math.min(y/max,1):0})`;
    if(header)header.classList.toggle('scrolled',y>8);
    if(reduce)return;
    if(statement){
      const r=statement.getBoundingClientRect();
      if(r.bottom>0&&r.top<innerHeight)statement.style.setProperty('--p',((innerHeight-r.top)/(innerHeight+r.height)).toFixed(3));
    }
  }
  addEventListener('scroll',()=>{if(!raf)raf=requestAnimationFrame(update)},{passive:true});
  addEventListener('resize',update);
  update();

  /* ── 数値のカウントアップ ── */
  const nums=$$('[data-count]');
  if(nums.length&&!reduce&&'IntersectionObserver' in window){
    const nio=new IntersectionObserver(es=>es.forEach(e=>{
      if(!e.isIntersecting)return;
      nio.unobserve(e.target);
      const el=e.target,end=parseFloat(el.dataset.count),t0=performance.now();
      const step=t=>{
        const p=Math.min(1,(t-t0)/900),v=end*(1-Math.pow(1-p,3));
        el.textContent=Math.round(v).toLocaleString('ja-JP');
        if(p<1)requestAnimationFrame(step);else el.textContent=Math.round(end).toLocaleString('ja-JP');
      };
      requestAnimationFrame(step);
    }),{threshold:.4});
    nums.forEach(n=>nio.observe(n));
  }

  /* ── 年号 ── */
  $$('[data-year]').forEach(el=>el.textContent=String(new Date().getFullYear()));

  /* ── Hero: intro + message switch（ヒーローのあるページのみ） ── */
  if(!hero)return;
  const heroArt=$('.hero-art'),heroCopy=$('.hero-copy'),heroFoot=$('.hero-foot'),
        heroLines=$$('.hero-line-in'),heroModes=$$('.hero-mode');
  if(!heroFoot||heroModes.length<2){          // 切り替えUIが無い場合はイントロだけ
    hero.classList.add('ready');
    if(heroArt)heroArt.classList.add('is-intro');
    if(heroCopy)heroCopy.classList.add('in');
    setTimeout(()=>{
      if(heroArt)heroArt.classList.remove('is-intro');
      if(heroCopy)heroCopy.classList.remove('in','first');
    },reduce?0:2000);
    return;
  }
  const heroMessages=[['突き進む者に、','戦略を。'],['人と地域の挑戦を、','形にする。']];
  const HERO_MS=6000;
  let heroIndex=0,heroBusy=true,heroTimer;

  function schedule(){
    clearTimeout(heroTimer);
    heroFoot.classList.remove('tick');
    if(reduce||document.hidden)return;
    void heroFoot.offsetWidth;
    heroFoot.classList.add('tick');
    heroTimer=setTimeout(()=>goHero((heroIndex+1)%heroMessages.length),HERO_MS);
  }
  function goHero(next){
    if(heroBusy||next===heroIndex)return;
    heroBusy=true;heroIndex=next;
    clearTimeout(heroTimer);heroFoot.classList.remove('tick');
    heroArt.classList.remove('is-shifting');void heroArt.offsetWidth;heroArt.classList.add('is-shifting');
    heroCopy.classList.remove('in');heroCopy.classList.add('out');
    setTimeout(()=>{
      heroLines.forEach((l,i)=>l.textContent=heroMessages[heroIndex][i]);
      heroModes.forEach((m,i)=>{m.classList.toggle('active',i===heroIndex);m.setAttribute('aria-pressed',String(i===heroIndex))});
      heroCopy.classList.remove('out');void heroCopy.offsetWidth;heroCopy.classList.add('in');
    },620);
    setTimeout(()=>{heroArt.classList.remove('is-shifting');heroCopy.classList.remove('in');heroBusy=false;schedule()},1850);
  }
  heroModes.forEach((m,i)=>m.addEventListener('click',()=>goHero(i)));
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){clearTimeout(heroTimer);heroFoot.classList.remove('tick')}
    else if(!heroBusy)schedule();
  });

  let started=false;
  function startHero(){
    if(started)return;started=true;
    hero.classList.add('ready');
    heroArt.classList.add('is-intro');
    heroCopy.classList.add('in');
    setTimeout(()=>{
      heroArt.classList.remove('is-intro');
      heroCopy.classList.remove('in','first');
      heroBusy=false;schedule();
    },reduce?0:2000);
  }
  requestAnimationFrame(()=>requestAnimationFrame(startHero));
  setTimeout(startHero,500);
})();
