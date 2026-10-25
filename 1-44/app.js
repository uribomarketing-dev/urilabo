const menu=document.querySelector('.menu'),nav=document.querySelector('nav');menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);menu.querySelector('span').textContent=open?'−':'＋'});nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.querySelector('span').textContent='＋'}));
const form=document.querySelector('#contact-form');let mailBody='';form?.addEventListener('submit',e=>{e.preventDefault();const kind=document.querySelector('#kind').value,name=document.querySelector('#name').value,email=document.querySelector('#mail').value,msg=document.querySelector('#msg').value;mailBody=`お問い合わせ区分：${kind}\nお名前・団体名：${name}\nメールアドレス：${email}\n\n${msg}`;location.href=`mailto:info@urilabo.com?subject=${encodeURIComponent('[1-44] '+kind)}&body=${encodeURIComponent(mailBody)}`;document.querySelector('#form-result').textContent='メールアプリで内容を確認して送信してください。開かない場合は、内容をコピーして info@urilabo.com にお送りください。';document.querySelector('#copy-message').hidden=false});document.querySelector('#copy-message')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(mailBody);document.querySelector('#form-result').textContent='お問い合わせ内容をコピーしました。'}catch{document.querySelector('#form-result').textContent='コピーできませんでした。入力内容を選択してコピーしてください。'}});


(()=>{const d=document;
d.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.querySelector('span').textContent='＋';menu.focus()}});
const rem=d.querySelector('.remaining-processes');
d.querySelectorAll('[data-open-remaining]').forEach(b=>b.addEventListener('click',()=>{if(!rem)return;rem.open=true;rem.scrollIntoView({behavior:'smooth',block:'start'})}));
const openHash=()=>{let id='';try{id=decodeURIComponent(location.hash.slice(1))}catch{}if(!id)return;const t=d.getElementById(id);if(!t)return;const p=t.closest('.remaining-processes');if(p)p.open=true;if(t.tagName==='DETAILS')t.open=true;requestAnimationFrame(()=>t.scrollIntoView({block:'center'}))};
addEventListener('hashchange',openHash);openHash();
if('IntersectionObserver'in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
const els=[...d.querySelectorAll('.section-label,.story-body,.process-heading,.featured-caption,.featured-processes .process-card,.remaining-processes,.product-layout,.news-row,.future,.contact-band>div,.detail>*,.contact-layout>*,.open-heading,.promises .promise,.tracker,.open-log,.passport-intro>*,.passport-lookup')].filter(el=>el.getBoundingClientRect().top>innerHeight*.92);
if(els.length){d.documentElement.classList.add('js');
const io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}}),{rootMargin:'0px 0px -8% 0px',threshold:.05});
els.forEach((el,i)=>{el.classList.add('reveal');if(el.classList.contains('process-card'))el.style.transitionDelay=(i%2)*.08+'s';io.observe(el)})}}
})();

/* ============================================================
   v9 : OPEN MAKING（44工程の地図／やさしい日本語）  ※運用・更新は不要
   ============================================================ */
(()=>{const d=document,esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ---------- やさしい日本語モード ---------- */
const toggles=[...d.querySelectorAll('.easy-toggle')],cards=[...d.querySelectorAll('.easy-toggle-card')];
if(toggles.length||cards.length){
  const apply=on=>{
    d.body.classList.toggle('easy-mode',on);
    d.querySelectorAll('[data-easy]').forEach(el=>{
      if(!el.dataset.orig)el.dataset.orig=el.innerHTML;
      el.innerHTML=on?el.dataset.easy:el.dataset.orig;
    });
    toggles.forEach(t=>{t.setAttribute('aria-pressed',String(on));t.textContent=on?'もとの ひょうじに もどす':'やさしい日本語'});
    try{localStorage.setItem('easy144',on?'1':'0')}catch(e){}
  };
  const flip=()=>apply(!d.body.classList.contains('easy-mode'));
  toggles.forEach(t=>t.addEventListener('click',flip));
  cards.forEach(c=>c.addEventListener('click',flip));
  let saved=null;try{saved=localStorage.getItem('easy144')}catch(e){}
  if(saved==='1')apply(true);
}


/* ---------- お問い合わせ：?kind=rescue で素材提供を選択済みに ---------- */
try{const k=new URLSearchParams(location.search).get('kind'),sel=d.querySelector('#kind');
if(k==='rescue'&&sel){[...sel.options].forEach((o,i)=>{if(o.text.includes('レスキュー素材'))sel.selectedIndex=i});
const m=d.querySelector('#msg');if(m)m.placeholder='素材の種類・数量・状態・保管場所をお知らせください。写真は、メールアプリでの送信時に添付できます。'}}catch(e){}
})();
