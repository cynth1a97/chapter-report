/* ===========================================
   CLOUD EDITOR — edits are saved to Cloudflare KV (/api/edits)
   so every visitor sees the latest text.
   · E key, or hover the top-left corner and click EDIT (detail pages: the 編輯 button in the top bar)
   · Anyone can edit (no password); the server keeps the last 30 versions for rollback
   · Each change autosaves about 1 s after you stop typing
   · Esc (or the EDIT button) leaves edit mode; Cmd/Ctrl+S downloads a backup copy
   <body data-page="slides|detail"> decides which document is stored.
   <meta name="build"> (written by stamp.py) ties saved edits to one page version:
   edits from another version are ignored, and a stale tab is not allowed to save.
   =========================================== */
class Editor{
  constructor(){
    this.page=document.body.dataset.page||'slides';
    this.api='/api/edits?page='+encodeURIComponent(this.page);
    this.on=false;this.timer=null;this.pw=null;
    this.build=(document.querySelector('meta[name=build]')||{}).content||'';
    try{this.pw=sessionStorage.getItem('edit-pw')}catch(e){}
    this.collect();
    this.ui();
    this.load();
  }
  /* editable text blocks, keyed "group:index" so keys stay stable per slide/section */
  collect(){
    const SEL='h1,h2,h3,p,li,td,th,.pair,.who,.name,.kicker,.kicker-zh,.en,.en-display,.lede,.src,.quote,.ledger .r>div,.presenters>span,.mono,.num,.era,.what,.why,.small,.body';
    const groups=document.querySelectorAll('.slide, main section');
    this.map=new Map();
    groups.forEach((g,gi)=>{
      const gk=g.id||((g.classList.contains('slide')?'s':'g')+gi);
      let els=[...g.querySelectorAll(SEL)].filter(el=>!el.closest('.glitch,.qr,.band,.layers,[data-noedit]'));
      els=els.filter(el=>!els.some(o=>o!==el&&o.contains(el)));
      els.forEach((el,i)=>{const k=gk+':'+i;el.dataset.eid=k;this.map.set(k,el)});
    });
    this.orig=new Map([...this.map].map(([k,el])=>[k,el.innerHTML]));
  }
  ui(){
    const st=document.createElement('style');
    st.textContent=`
.edit-hotzone{position:fixed;top:0;left:0;width:90px;height:90px;z-index:10000;cursor:pointer}
.edit-toggle{position:fixed;top:16px;left:16px;z-index:10001;opacity:0;pointer-events:none;transition:opacity .3s;cursor:pointer;
  font:500 13px ui-monospace,monospace;letter-spacing:.1em;background:var(--paper,#fff);color:var(--ink,var(--soil,#222));border:1.5px solid var(--ink,var(--soil,#222));padding:8px 12px}
.edit-toggle.show,.edit-toggle.active{opacity:1;pointer-events:auto}
.edit-toggle.active{background:var(--ink,var(--soil,#222));color:var(--paper,#fff)}
.edit-status{position:fixed;top:22px;left:110px;z-index:10001;font:500 12px ui-monospace,monospace;letter-spacing:.06em;padding:5px 10px;
  background:var(--paper,#fff);color:var(--ink,var(--soil,#222));border:1px solid currentColor;display:none}
body.editing .edit-status{display:block}
body.editing [contenteditable]{outline:1px dashed var(--ink-soft,var(--clay,#c00));outline-offset:4px;cursor:text}
body[data-page=detail] .edit-hotzone{display:none}
.bar-left .edit-toggle{position:static;opacity:1;pointer-events:auto;font:500 13px var(--f-mono,monospace);letter-spacing:.06em;padding:7px 12px;background:transparent;color:inherit;border:1.5px solid currentColor;white-space:nowrap}
body[data-page=detail] .edit-status{top:auto;bottom:22px}
@media (hover:none){.edit-toggle{opacity:.5;pointer-events:auto}}`;
    document.head.appendChild(st);
    let t=document.getElementById('editToggle'),z=document.querySelector('.edit-hotzone');
    if(!z){z=document.createElement('div');z.className='edit-hotzone';document.body.appendChild(z)}
    if(!t){t=document.createElement('button');t.id='editToggle';t.className='edit-toggle';t.textContent='EDIT';t.title='編輯模式 (E)';document.body.appendChild(t)}
    const bar=document.querySelector('.bar-left');
    if(bar&&document.body.dataset.page==='detail'){t.className='edit-toggle home';t.textContent='編輯';bar.insertBefore(t,bar.querySelector('.brand'))}
    this.status=document.createElement('div');this.status.className='edit-status';this.status.setAttribute('role','status');document.body.appendChild(this.status);
    let to;const show=()=>{clearTimeout(to);t.classList.add('show')},hide=()=>{to=setTimeout(()=>{if(!this.on)t.classList.remove('show')},400)};
    z.onmouseenter=show;z.onmouseleave=hide;t.onmouseenter=show;t.onmouseleave=hide;
    t.onclick=()=>this.toggle();z.onclick=()=>this.toggle();
    document.addEventListener('keydown',e=>{
      if((e.key==='e'||e.key==='E')&&!e.target.isContentEditable&&!/INPUT|TEXTAREA/.test(e.target.tagName)&&!e.metaKey&&!e.ctrlKey)this.toggle();
      if(e.key==='Escape'&&this.on){e.preventDefault();this.toggle()}
      if((e.metaKey||e.ctrlKey)&&e.key==='s'){e.preventDefault();this.download()}
    });
    document.addEventListener('input',e=>{if(this.on&&e.target.closest&&e.target.closest('[data-eid]'))this.queue()});
    addEventListener('beforeunload',e=>{if(this.timer){this.flush();e.preventDefault()}});
  }
  say(msg){this.status.textContent=msg}
  /* only b/strong/i/em/br/span/small with class attributes survive */
  clean(html){
    const t=document.createElement('template');t.innerHTML=html;const ok=['B','STRONG','I','EM','BR','SPAN','SMALL'];
    let bad;while((bad=[...t.content.querySelectorAll('*')].find(e=>!ok.includes(e.tagName))))bad.replaceWith(...bad.childNodes);
    t.content.querySelectorAll('*').forEach(e=>[...e.attributes].forEach(a=>{if(a.name!=='class')e.removeAttribute(a.name)}));
    return t.innerHTML;
  }
  async load(){
    try{
      const r=await fetch(this.api,{cache:'no-store'});if(!r.ok)return;
      const d=await r.json();const items=d.items||{};
      if(d.build&&this.build&&d.build!==this.build)return; // saved on another page version
      Object.entries(items).forEach(([k,v])=>{const el=this.map.get(k);if(el&&typeof v==='string')el.innerHTML=this.clean(v)});
    }catch(e){/* opened as a local file: no cloud edits */}
  }
  async login(){
    for(let n=0;n<3;n++){
      const pw=prompt(n?'密碼不對，請再輸入一次：':'請輸入編輯密碼：');if(pw===null)return false;
      try{
        const r=await fetch(this.api,{method:'POST',headers:{'x-edit-password':pw}});
        if(r.ok){this.pw=pw;try{sessionStorage.setItem('edit-pw',pw)}catch(e){}return true}
        if(r.status!==401){alert('無法連線到雲端存檔（只有部署後的網站能存檔）。');return false}
      }catch(e){alert('無法連線到雲端存檔（只有部署後的網站能存檔）。');return false}
    }
    return false;
  }
  async toggle(){
    this.on=!this.on;document.body.classList.toggle('editing',this.on);
    document.getElementById('editToggle').classList.toggle('active',this.on);
    this.map.forEach(el=>{if(this.on)el.setAttribute('contenteditable','true');else el.removeAttribute('contenteditable')});
    if(this.on)this.say('編輯中 · Esc 離開');
    else if(this.timer)this.flush();
  }
  queue(){this.say('尚未儲存…');clearTimeout(this.timer);this.timer=setTimeout(()=>this.flush(),1000)}
  async flush(){
    clearTimeout(this.timer);this.timer=null;
    if(await this.stale()){this.say('此頁已更新，請重新整理後再編輯');if(this.on)this.toggle();return}
    const items={};this.map.forEach((el,k)=>{const h=this.clean(el.innerHTML);if(h!==this.clean(this.orig.get(k)))items[k]=h});
    this.say('儲存中…');
    try{
      const r=await fetch(this.api,{method:'PUT',keepalive:true,headers:{'content-type':'application/json','x-edit-password':this.pw||''},body:JSON.stringify({items,build:this.build})});
      if(r.status===401){this.pw=null;try{sessionStorage.removeItem('edit-pw')}catch(e){}this.say('密碼失效，請重新進入編輯');return}
      if(!r.ok)throw 0;
      const t=new Date();this.say('已儲存 '+t.toTimeString().slice(0,5));
    }catch(e){this.say('儲存失敗，請稍後再改一下重試')}
  }
  /* true when the deployed page is a newer version than this tab */
  async stale(){
    if(!this.build)return false;
    try{
      const r=await fetch(location.pathname+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)return false;
      const m=(await r.text()).match(/<meta name="build" content="([^"]+)"/);
      return !!m&&m[1]!==this.build;
    }catch(e){return false}
  }
  download(){
    if(this.on)this.toggle();
    const c=document.documentElement.cloneNode(true);
    c.querySelectorAll('.glitch i,.qr b,.edit-status').forEach(n=>n.remove());
    c.querySelectorAll('.slide').forEach(s=>s.classList.remove('active','visible'));
    const a=document.createElement('a');
    a.href=URL.createObjectURL(new Blob(['<!DOCTYPE html>\n'+c.outerHTML],{type:'text/html'}));
    a.download=decodeURIComponent(location.pathname.split('/').pop()||'page.html');a.click();
  }
}
const editor=new Editor();
