/* Local archive search and division filters. No network requests. */
(function(){
 var buttons=Array.from(document.querySelectorAll('.filter'));
 if(!buttons.length)return;
 var field=document.querySelector('#archive-search'),status=document.querySelector('.result-count'),empty=document.querySelector('.empty-state');
 var entries=Array.from(document.querySelectorAll('.ev')),active='all';
 var records=entries.map(function(el){return {el:el,tags:(el.dataset.tags||'').split(' '),text:el.textContent.normalize('NFKC').toLocaleLowerCase('ja')};});
 var cEl=document.querySelector('#ev-count');if(cEl)cEl.textContent=String(document.querySelectorAll('.yr:not(.planned) .ev').length);
 function apply(){
  var words=(field.value||'').normalize('NFKC').toLocaleLowerCase('ja').trim().split(/\s+/).filter(Boolean),count=0;
  records.forEach(function(r){var show=(active==='all'||r.tags.indexOf(active)!==-1)&&words.every(function(w){return r.text.indexOf(w)!==-1;});r.el.hidden=!show;if(show)count++;});
  document.querySelectorAll('.yr').forEach(function(sec){sec.hidden=!sec.querySelector('.ev:not([hidden])');});
  buttons.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.filter===active));});
  status.textContent=count+' 件の出来事を表示 / 全 '+entries.length+' 件（予定を含む）';empty.hidden=count!==0;
 }
 buttons.forEach(function(b){b.addEventListener('click',function(){active=b.dataset.filter;apply();});});
 field.addEventListener('input',apply);apply();
})();
