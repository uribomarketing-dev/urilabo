/* わかりやすい日本語 切り替えボタン（全ページ共通）
   使い方：切り替えたい文章に data-easy="わかりやすい版の文章" を付ける。
   ボタンは全ページの右下に出る。選んだ状態は、ほかのページでも覚えている。 */
(function () {
  'use strict';
  var KEY = 'easyja';
  var d = document;
  var on = false;
  var btn, note;

  function read() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function save(v) { try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) {} }

  function css() {
    var s = d.createElement('style');
    s.textContent =
      '#easyja-btn{position:fixed;right:16px;bottom:16px;z-index:2147483000;min-height:44px;padding:10px 18px;' +
      'border:2px solid #fff;border-radius:999px;background:#1f2a37;color:#fff;font:700 15px/1.3 "Noto Sans JP",system-ui,sans-serif;' +
      'box-shadow:0 2px 10px rgba(0,0,0,.35);cursor:pointer;max-width:calc(100vw - 32px)}' +
      '#easyja-btn:focus-visible{outline:3px solid #ffbf47;outline-offset:2px}' +
      '#easyja-btn[aria-pressed="true"]{background:#0b6b3a}' +
      '#easyja-note{position:fixed;left:12px;right:12px;bottom:72px;z-index:2147483000;margin:0 auto;max-width:560px;padding:12px 16px;' +
      'border-radius:10px;background:#fff;color:#1f2a37;border:2px solid #1f2a37;font:500 15px/1.6 "Noto Sans JP",system-ui,sans-serif;' +
      'box-shadow:0 2px 10px rgba(0,0,0,.25)}' +
      '@media print{#easyja-btn,#easyja-note{display:none!important}}';
    d.head.appendChild(s);
  }

  function swap(isOn) {
    var els = d.querySelectorAll('[data-easy]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.getAttribute('data-orig') === null) el.setAttribute('data-orig', el.innerHTML);
      el.innerHTML = isOn ? el.getAttribute('data-easy') : el.getAttribute('data-orig');
    }
    return els.length;
  }

  function showNote(msg) {
    if (!note) {
      note = d.createElement('p');
      note.id = 'easyja-note';
      note.setAttribute('role', 'status');
      d.body.appendChild(note);
    }
    note.textContent = msg;
  }
  function hideNote() { if (note && note.parentNode) { note.parentNode.removeChild(note); note = null; } }

  function apply(isOn, fromClick) {
    on = isOn;
    d.documentElement.classList.toggle('easy-mode', on);
    var n = swap(on);
    btn.setAttribute('aria-pressed', String(on));
    btn.textContent = on ? 'ふつうの ぶんしょうに もどす' : 'わかりやすい日本語';
    if (on && n === 0) {
      showNote('このページの「わかりやすい日本語」は、じゅんびちゅうです。ほかの ページは、よめます。');
    } else {
      hideNote();
    }
    if (fromClick) save(on);
  }

  function init() {
    css();
    btn = d.createElement('button');
    btn.type = 'button';
    btn.id = 'easyja-btn';
    btn.setAttribute('aria-pressed', 'false');
    btn.textContent = 'わかりやすい日本語';
    btn.addEventListener('click', function () { apply(!on, true); });
    d.body.appendChild(btn);
    if (read()) apply(true, false);
  }

  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', init); else init();
})();
