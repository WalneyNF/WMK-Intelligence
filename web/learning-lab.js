const $=id=>document.getElementById(id);let scripts=[],books=[];async function api(path,b){let r=await fetch('/api/learning/'+path,b?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}:{}),d=await r.json();if(!r.ok)throw Error(d.erro||d.error||'Falha');return d}function safe(fn,status){return async()=>{try{await fn()}catch(e){$(status).textContent=e.message}}}function fillBooks(d){books=d;$('books').replaceChildren(new Option('Novo caderno',''),...d.map(x=>new Option(x.name,x.id)))}$('books').onchange=()=>{let b=books.find(x=>x.id===$('books').value);$('name').value=b?.name||'';$('term').value=b?.term||''};$('new').onclick=()=>{$('books').value='';$('books').onchange()};$('save').onclick=safe(async()=>{fillBooks(await api('notebook',{op:'save',id:$('books').value,name:$('name').value,term:$('term').value}));$('note').textContent='Salvo. Selecione o caderno.'},'note');$('scripts').onchange=()=>{$('description').textContent=scripts.find(x=>x.id===$('scripts').value)?.description||''};$('view').onclick=safe(async()=>{setCode((await api('code',{id:$('scripts').value})).code,'python')},'status');$('run').onclick=safe(async()=>{$('status').textContent='Processando...';let d=await api('run',{id:$('scripts').value}),t=document.createElement('table');for(let [i,row] of [d.columns,...d.rows].entries()){let tr=document.createElement('tr');for(let v of row){let c=document.createElement(i?'td':'th');c.textContent=v;tr.append(c)}t.append(tr)}$('results').replaceChildren(t);$('status').textContent=d.sample+' publicações examinadas · '+d.total_results+' resultados (até 500 exibidos)'},'status');async function read(op){let provider=$('provider').value,consent=op==='ask'&&provider==='groq'&&confirm('Enviar até 8 trechos ao Groq?');if(op==='ask'&&provider==='groq'&&!consent)return;$('note').textContent='Consultando...';let d=await api('notebook',{op,id:$('books').value,provider,consent,question:$('question').value});$('note').textContent=d.method;$('answer').textContent=d.answer;$('sourcesList').replaceChildren();for(let p of d.sources){let a=document.createElement('article'),h=document.createElement('strong'),t=document.createElement('p');h.textContent=p.title;t.textContent=p.excerpt;a.append(h,t);if(/^https?:\/\//i.test(p.source_url||'')){let l=document.createElement('a');l.href=p.source_url;l.textContent=p.id;l.target='_blank';l.rel='noopener noreferrer';a.append(l)}$('sourcesList').append(a)}}$('sources').onclick=safe(()=>read('sources'),'note');$('ask').onclick=safe(()=>read('ask'),'note');safe(async()=>{scripts=await api('catalog');$('scripts').replaceChildren(...scripts.map(x=>new Option(x.name,x.id)));$('scripts').onchange();fillBooks(await api('books'))},'status')();
let editor=null,lang='python',examples=[];
function setCode(code,language){lang=language;$('code').value=code;if(editor){editor.setValue(code);monaco.editor.setModelLanguage(editor.getModel(),language)}}
function getCode(){return editor?editor.getValue():$('code').value}
async function schemaCompletion(){
 const d=await (await fetch('/api/database/catalog')).json();
 const words=[...new Set(d.tables.flatMap(t=>[t.name,...t.columns.map(c=>c.name)]))];
 monaco.languages.registerCompletionItemProvider('sql',{provideCompletionItems(model,pos){
 const w=model.getWordUntilPosition(pos);
 return {suggestions:words.map(label=>({label,kind:monaco.languages.CompletionItemKind.Field,insertText:label,range:{startLineNumber:pos.lineNumber,endLineNumber:pos.lineNumber,startColumn:w.startColumn,endColumn:w.endColumn}}))};
 }});
}
const loader=document.createElement('script');
loader.src='/vendor/monaco/vs/loader.js';
loader.onload=()=>{
 require.config({paths:{vs:'/vendor/monaco/vs'}});
 require(['vs/editor/editor.main'],()=>{
 $('monaco').style.display='block';
 editor=monaco.editor.create($('monaco'),{value:$('code').value,language:lang,theme:'vs-dark',automaticLayout:true,minimap:{enabled:false},fontSize:14});
 $('code').style.display='none';$('editorStatus').textContent='Monaco ativo';
 schemaCompletion().catch(()=>{$('editorStatus').textContent='Monaco ativo; esquema indisponível'});
 });
};
document.head.append(loader);
safe(async()=>{examples=await api('snippets');$('snippet').replaceChildren(...examples.map((s,i)=>new Option(s.language+' · '+s.name,i)))},'status')();
$('loadSnippet').onclick=()=>{const s=examples[Number($('snippet').value)];if(s)setCode(s.code,s.language)};
$('copyCode').onclick=safe(async()=>{await navigator.clipboard.writeText(getCode());$('status').textContent='Copiado'},'status');
$('sqlRun').onclick=safe(async()=>{if(lang!=='sql')throw Error('Selecione um exemplo SQL');const r=await fetch('/api/database/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sql:getCode()})});const d=await r.json();if(!r.ok)throw Error(d.erro||d.error||'Consulta recusada');const t=document.createElement('table');for(const row of [d.columns,...d.rows]){const tr=t.insertRow();for(const v of row)tr.insertCell().textContent=v}$('results').replaceChildren(t);$('status').textContent=d.rows.length+' linhas'+(d.truncated?' (limitado)':'')},'status');
