const $=id=>document.getElementById(id);
async function request(path,body){const opts=body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};const response=await fetch(path,opts),data=await response.json();if(!response.ok)throw Error(data.erro||'HTTP '+response.status);return data}
const el=(tag,text)=>{let n=document.createElement(tag);n.textContent=text||'';return n};
async function metrics(){try{const s=await request('/api/stats');$('totalPosts').textContent=s.posts;$('totalComments').textContent=s.comments;$('totalAlerts').textContent=s.alerts;$('totalSources').textContent=s.sources||0}catch(e){$('collectStatus').textContent=e.message}}
async function posts(){try{const data=await request('/api/posts?q='+encodeURIComponent($('search').value)+'&source='+encodeURIComponent($('sourceFilter').value)),div=$('postList'),alerts=$('alerts');div.replaceChildren();alerts.replaceChildren();for(const p of data.posts){const card=el('article');card.className='post';card.append(el('strong',p.title||'(sem título)'),el('p',(p.body||'').slice(0,650)),el('small','['+(p.source||'origem desconhecida')+'] · '+(p.author||'Autor desconhecido')+' · '+(p.submolt||'Sem comunidade')+' · Triagem '+p.risk));let a=el('a','Ver publicação original');a.href=p.source_url;a.target='_blank';a.rel='noopener noreferrer';card.append(document.createElement('br'),a);div.append(card);if(p.risk>=2){const alert=card.cloneNode(true);alerts.append(alert)}}if(!data.posts.length)div.append(el('p','Nenhuma publicação coletada.'));if(!alerts.children.length)alerts.append(el('p','Nenhum conteúdo sinalizado.'))}catch(e){$('postList').textContent=e.message}}
async function agents(){try{const a=await request('/api/agents');$('agentList').replaceChildren(...a.agentes.map(x=>el('p',x.id+': '+x.especialidade)))}catch(e){$('agentList').textContent=e.message}}
$('collect').onclick=async()=>{let b=$('collect');b.disabled=true;$('collectStatus').textContent=' Consultando...';try{const r=await request('/api/coletar',{limit:25,source:$('sourceSelect').value});$('collectStatus').textContent=r.obtidas+' itens, '+r.novas+' novos';await Promise.all([metrics(),posts()])}catch(e){$('collectStatus').textContent=e.message}finally{b.disabled=false}};
$('refresh').onclick=posts;$('search').oninput=()=>{clearTimeout(window.findTimer);window.findTimer=setTimeout(posts,300)};
let reportRaw='', reportPlain=false;
function inlineMd(node,value){
  for(const part of value.split(/(\*\*[^*]+\*\*|\x60[^\x60]+\x60|\*[^*]+\*)/g)){
    if(part.startsWith('**')&&part.endsWith('**')&&part.length>4)node.append(el('strong',part.slice(2,-2)));
    else if(part.startsWith('*')&&part.endsWith('*')&&part.length>2)node.append(el('em',part.slice(1,-1)));
    else if(part.charCodeAt(0)===96&&part.charCodeAt(part.length-1)===96)node.append(el('code',part.slice(1,-1)));
    else node.append(document.createTextNode(part));
  }
}
function renderReport(){
  const out=$('reportText');out.replaceChildren();
  if(!reportRaw){out.textContent='Nenhum relatório gerado.';return}
  if(reportPlain){out.append(el('pre',reportRaw));return}
  const lines=reportRaw.split(/\r?\n/);let list=null;
  const cells=line=>line.trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim());
  for(let i=0;i<lines.length;i++){
    const line=lines[i].trim();if(!line){list=null;continue}
    if(line.startsWith('|')&&i+1<lines.length&&/^\s*\|?[\s:|-]+$/.test(lines[i+1])&&lines[i+1].includes('---')){
      list=null;const table=el('table'),head=table.createTHead().insertRow();for(const c of cells(line)){const th=el('th');inlineMd(th,c);head.append(th)}
      i++;const body=table.createTBody();while(i+1<lines.length&&lines[i+1].trim().startsWith('|')){const row=body.insertRow();for(const c of cells(lines[++i]))inlineMd(row.insertCell(),c)}out.append(table);continue;
    }
    const h=line.match(/^(#{1,6})\s+(.*)$/),li=line.match(/^([-*]|\d+\.)\s+(.*)$/);
    if(li){const tag=/^\d/.test(li[1])?'ol':'ul';if(!list||list.tagName.toLowerCase()!==tag){list=el(tag);out.append(list)}const item=el('li');inlineMd(item,li[2]);list.append(item);continue}
    list=null;const n=el(h?'h'+h[1].length:'p');inlineMd(n,h?h[2]:line);out.append(n);
  }
}
$('report').onclick=async()=>{const b=$('report');b.disabled=true;$('clearReport').disabled=true;$('reportStatus').textContent='Gerando...';try{const r=await request('/api/relatorio',{provider:$('provider').value,source:$('sourceFilter').value});reportRaw=r.texto||'';renderReport();$('reportStatus').textContent='Relatório gerado.'}catch(e){$('reportStatus').textContent=e.message}finally{b.disabled=false;$('clearReport').disabled=false}};
$('toggleReport').onclick=()=>{reportPlain=!reportPlain;renderReport()};
$('clearReport').onclick=()=>{reportRaw='';renderReport();$('reportStatus').textContent='Relatório limpo.'};
$('copyReport').onclick=async()=>{if(!reportRaw)return;try{await navigator.clipboard.writeText(reportRaw);$('reportStatus').textContent='Copiado!'}catch(e){$('reportStatus').textContent='Não foi possível copiar; use a visualização de texto.'}};
function downloadReport(ext){if(!reportRaw)return;const stamp=new Date(),pad=(v,n=2)=>String(v).padStart(n,'0');const name=stamp.getFullYear()+'-'+pad(stamp.getMonth()+1)+'-'+pad(stamp.getDate())+'_'+pad(stamp.getHours())+'-'+pad(stamp.getMinutes())+'-'+pad(stamp.getSeconds())+'-'+pad(stamp.getMilliseconds(),3);let content=reportRaw;
if(ext==='html'){const old=reportPlain;reportPlain=false;renderReport();content='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>WMK Relatório</title><style>body{font:16px Arial;max-width:1000px;margin:30px auto;padding:15px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:8px;overflow-wrap:anywhere}</style><body><h1>WMK Intelligence</h1>'+$('reportText').innerHTML+'</body></html>';reportPlain=old;renderReport()}
const url=URL.createObjectURL(new Blob([content],{type:ext==='html'?'text/html;charset=utf-8':'text/plain;charset=utf-8'})),a=el('a');a.href=url;a.download='wmk-relatorio-'+name+'-'+crypto.randomUUID().slice(0,8)+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
$('downloadReport').onclick=()=>downloadReport('txt');$('downloadMd').onclick=()=>downloadReport('md');$('downloadHtml').onclick=()=>downloadReport('html');
$('registerAgent').onclick=async()=>{if(!confirm('Registrar um agente REAL no Moltbook? Será necessária ativação humana.'))return;let out=$('registerResult');out.textContent='Solicitando...';try{const r=await request('/api/register',{source:'moltbook',name:$('agentName').value,description:$('agentDescription').value});out.textContent=JSON.stringify(r,null,2)+'\nNÃO COMPARTILHE A CHAVE'}catch(e){out.textContent=e.message}};
const panels=[...document.querySelectorAll('.panel')];let z=5;
function save(){localStorage.setItem('wmk-layout-v1',JSON.stringify(panels.map(p=>({id:p.id,left:p.style.left,top:p.style.top,width:p.style.width,height:p.style.height,display:p.style.display}))))}
try{for(const x of JSON.parse(localStorage.getItem('wmk-layout-v1')||'[]')){let p=$(x.id);if(p)for(let k of ['left','top','width','height','display'])if(x[k]!==undefined)p.style[k]=x[k]}}catch(e){}
for(const p of panels){const h=p.querySelector('.handle');h.onpointerdown=event=>{if(event.target.closest('button')||matchMedia('(max-width:700px)').matches)return;let x=event.clientX,y=event.clientY,left=p.offsetLeft,top=p.offsetTop;p.style.zIndex=++z;h.setPointerCapture(event.pointerId);h.onpointermove=e=>{p.style.left=Math.max(0,left+e.clientX-x)+'px';p.style.top=Math.max(0,top+e.clientY-y)+'px'};h.onpointerup=()=>{h.onpointermove=null;h.onpointerup=null;save()}};p.querySelector('.close').onclick=()=>{p.style.display='none';save()}}
document.querySelectorAll('nav [data-panel]').forEach(b=>b.onclick=()=>{let p=$(b.dataset.panel);p.style.display='block';p.style.zIndex=++z;save()});
$('reset').onclick=()=>{localStorage.removeItem('wmk-layout-v1');location.reload()};metrics();posts();agents();

async function sources(){try{const r=await request('/api/sources');const active=$('sourceSelect'),filter=$('sourceFilter'),list=$('sourcesList');active.replaceChildren();filter.replaceChildren(new Option('Todas as redes',''));list.replaceChildren();for(const src of r.sources){const text=src.nome+' ('+src.id+')';if(src.ativo)active.add(new Option(text,src.id));filter.add(new Option(text,src.id));const card=el('article');card.className='post';card.append(el('strong',text),el('p',src.descricao||''),el('small',src.ativo?'ATIVA · '+src.status:'INATIVA · '+src.status));list.append(card)}if(!active.options.length)active.add(new Option('Sem fontes ativas',''));}catch(e){$('sourcesList').textContent=e.message}}
$('sourceFilter').onchange=posts;sources();
