/* 社歴フィード（/history/feed.xml）から最新のお知らせを自動表示。失敗時は静的表示のまま */
(function(){
  function fmt(d){ return d ? d.slice(0,10).replace(/-/g,'.') : ''; }
  fetch('/history/feed.xml').then(function(r){ if(!r.ok) throw 0; return r.text(); }).then(function(xml){
    var doc = new DOMParser().parseFromString(xml, 'application/xml');
    if (doc.querySelector('parsererror')) return;
    var entries = Array.prototype.slice.call(doc.getElementsByTagName('entry')).map(function(e){
      var l = e.getElementsByTagName('link')[0];
      return {
        title: (e.getElementsByTagName('title')[0]||{}).textContent || '',
        href: l ? l.getAttribute('href') : '',
        date: (e.getElementsByTagName('updated')[0]||{}).textContent || ''
      };
    }).filter(function(x){ return x.title && x.href; });
    if (!entries.length) return;

    /* トップのNEWS一覧：最新3件に差し替え */
    var list = document.querySelector('.news-list');
    if (list) {
      list.innerHTML = '';
      entries.slice(0,3).forEach(function(x){
        var a = document.createElement('a');
        a.href = x.href;
        a.innerHTML = '<span class="nd"></span><span class="nt"></span><span class="nm">お知らせ</span>';
        a.querySelector('.nd').textContent = fmt(x.date);
        a.querySelector('.nt').textContent = x.title;
        list.appendChild(a);
      });
    }

    /* 各ページの「最新の動き」ブロック */
    Array.prototype.forEach.call(document.querySelectorAll('[data-autonews]'), function(box){
      var limit = parseInt(box.getAttribute('data-limit')||'3',10);
      var kw = box.getAttribute('data-filter');
      var picked = entries;
      if (kw) {
        var re = new RegExp(kw);
        var hit = entries.filter(function(x){ return re.test(x.title); });
        if (hit.length >= 2) picked = hit;
      }
      picked.slice(0,limit).forEach(function(x){
        var a = document.createElement('a');
        a.href = x.href;
        a.innerHTML = '<span class="pd en"></span><span class="pt"></span><span class="po">お知らせ ↗</span>';
        a.querySelector('.pd').textContent = fmt(x.date);
        a.querySelector('.pt').textContent = x.title;
        box.appendChild(a);
      });
      var sec = box.closest('section');
      if (sec && box.children.length) sec.hidden = false;
    });
  }).catch(function(){});
})();
