// Exemplo de consumo de API REST com JavaScript puro.
const $=id=>document.getElementById(id);
async function refresh(){
 try{
 const response=await fetch('/api/database/catalog');
 if(!response.ok)throw Error('HTTP '+response.status);
 const data=await response.json();
 $('raw').textContent=JSON.stringify(data,null,2);
 $('cards').replaceChildren();
 for(const table of data.tables){
 const card=document.createElement('article'),value=document.createElement('strong');
 value.textContent=table.count;card.append(value,document.createTextNode(table.name));$('cards').append(card);
 }
 $('bars').replaceChildren();
 const max=Math.max(1,...data.communities.map(c=>c.total));
 for(const c of data.communities){
 const row=document.createElement('p'),bar=document.createElement('div');
 row.textContent=(c.community||'(sem comunidade)')+' — '+c.total;
 bar.className='bar';bar.style.width=(100*c.total/max)+'%';row.append(bar);$('bars').append(row);
 }
 }catch(e){$('raw').textContent=e.message}
}
$('refresh').onclick=refresh;refresh();