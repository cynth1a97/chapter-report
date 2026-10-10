/* ===========================================
   SLIDE PRESENTATION CONTROLLER
   Keys: ← → Space PageUp/PageDown Home End · wheel · swipe
   =========================================== */
class SlidePresentation{
  constructor(){
    this.slides=[...document.querySelectorAll('.slide')];
    this.stage=document.getElementById('deckStage');
    this.bar=document.getElementById('progress');
    this.i=0;this.lock=false;
    this.decorate();this.scale();this.keys();this.wheel();this.touch();
    addEventListener('resize',()=>this.scale());
    const h=parseInt(location.hash.slice(1));this.show(isNaN(h)?0:h-1);
  }
  scale(){
    const k=Math.min(innerWidth/1920,innerHeight/1080);
    this.stage.style.transform=`translate(${(innerWidth-1920*k)/2}px,${(innerHeight-1080*k)/2}px) scale(${k})`;
  }
  show(n){
    this.i=Math.max(0,Math.min(n,this.slides.length-1));
    this.slides.forEach((s,j)=>{s.classList.toggle('active',j===this.i);s.classList.toggle('visible',j===this.i)});
    this.bar.style.width=((this.i+1)/this.slides.length*100)+'%';
    history.replaceState(null,'','#'+(this.i+1));
  }
  next(){this.show(this.i+1)} prev(){this.show(this.i-1)}
  keys(){
    document.addEventListener('keydown',e=>{
      if(document.body.classList.contains('editing'))return;
      if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){e.preventDefault();this.next()}
      else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();this.prev()}
      else if(e.key==='Home')this.show(0);
      else if(e.key==='End')this.show(this.slides.length-1);
    });
  }
  wheel(){
    addEventListener('wheel',e=>{
      if(this.lock||document.body.classList.contains('editing')||Math.abs(e.deltaY)<20)return;
      this.lock=true;e.deltaY>0?this.next():this.prev();setTimeout(()=>this.lock=false,700);
    },{passive:true});
  }
  touch(){
    let x=0;
    addEventListener('touchstart',e=>{x=e.touches[0].clientX},{passive:true});
    addEventListener('touchend',e=>{const d=e.changedTouches[0].clientX-x;if(Math.abs(d)>50)d<0?this.next():this.prev()});
  }
  /* page numbers, pixel-glitch columns and QR patches */
  decorate(){
    const total=String(this.slides.length).padStart(2,'0');
    this.slides.forEach((s,j)=>{const p=s.querySelector('[data-page]');if(p)p.textContent=String(j+1).padStart(2,'0')+' / '+total});
    document.querySelectorAll('.glitch').forEach(g=>{
      const w=+g.dataset.w||420,rows=+g.dataset.rows||64,h=g.clientHeight/rows;
      g.style.width=w+'px';
      for(let r=0;r<rows;r++){
        const step=Math.floor(r/(rows/8));
        const len=Math.max(18,w-step*(w/8)-((r*7)%3)*(w/26));
        const e=document.createElement('i');
        e.style.top=(r*h)+'px';e.style.width=len+'px';e.style.opacity=(r%5===0)?.3:1;
        e.style.transitionDelay=(.15+r*.01)+'s';
        g.appendChild(e);
      }
    });
    const pat='1111111010000010101110101011101010000010111111100110010010101101';
    document.querySelectorAll('.qr').forEach(q=>{for(const c of pat){const b=document.createElement('b');if(c==='0')b.className='o';q.appendChild(b)}});
  }
}

const deck=new SlidePresentation();
