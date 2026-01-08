
function checkDomain(){
  const input = document.getElementById('domainInput');
  const out = document.getElementById('domainResult');
  const q = (input?.value||'').trim();
  if(!q){ out.textContent='Enter a domain to search.'; out.className='small text-muted'; return; }
  fetch('/domains/check/?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{
    out.textContent = d.available ? (d.domain+' is available ✓') : (d.domain+' is taken ✗');
    out.className = 'small ' + (d.available ? 'text-success' : 'text-danger');
  }).catch(()=>{ out.textContent='Error checking domain'; out.className='small text-danger'; });
}
