/* MYCELIUM — replays the WITNESSED 43-event trace as a growing typed hypergraph.
   G_t --e_t--> G_{t+1}. The renderer OBSERVES the fold; it never invents state.
   Semantic color = f(node.sigma) (pure). Above Φ: dream shimmer (presentation
   entropy, NON-semantic). At a verdict the color COLLAPSES to its typed value —
   dH_visual/dt < 0 approaching Φ. Compost stays visible (J_memory=alive∪dead).
   ΔX=ΔP=ΔE=ΔA=0 · NO_CLAIM.  SIGMA map is IDENTICAL to reducer.py (one truth). */
const SIGMA = { SURVIVES:"survive", EVIDENCE_NEEDED:"hold", RENAMING_ONLY:"compost" };
const LIVE = new URLSearchParams(location.search).get("src") === "live";
// live producer op → internal renderer event (same object_id → same node identity)
function fromLive(le){
  const agent = le.actor==="HER_GEMMA"?"HER" : le.actor==="PREHAL_QWEN"?"HAL" : "CROSS";
  const o = le.object_id, p = (le.parent_ids||[])[0];
  if(le.op==="PROPOSE")  return { _id:le.event_id, _op:le.op, _actor:agent, type:"SPAWN", agent, name:o, seed:le.distinction, detail:le.mechanism };
  if(le.op==="MUTATE")   return { _id:le.event_id, _op:le.op, _actor:agent, type:"CROSS_POLLINATE", agent, name:o, parent:p, seed:le.distinction };
  if(le.op==="COMPOST")  return { _id:le.event_id, _op:le.op, _actor:agent, type:"VERDICT", agent, name:o, verdict:"RENAMING_ONLY", fitness:0 };
  if(le.op==="HOLD")     return { _id:le.event_id, _op:le.op, _actor:agent, type:"VERDICT", agent, name:o, verdict:"EVIDENCE_NEEDED", fitness:0.2 };
  if(le.op==="CHIDDUSH_CANDIDATE") return { _id:le.event_id, _op:le.op, _actor:agent, type:"VERDICT", agent, name:o, verdict:"SURVIVES", fitness:0.6 };
  return { _id:le.event_id, _op:le.op, _actor:agent, type:"PULSE", agent, name:p||o }; // COUNTERFEIT/ATTACK/DISCRIMINATE
}
const cv = document.getElementById("field"), ctx = cv.getContext("2d");
let W = 0, H = 0, DPR = 1;
const S = { events:[], jspace:null, nodes:new Map(), order:[], edges:[], pulses:[],
            sparks:[], seq:0, herN:0, halN:0, xN:0, clock:0, lastStep:0 };
const norm = s => (s||"").toLowerCase().replace(/[^a-z0-9]/g,"");

function resize(){
  DPR = window.devicePixelRatio||1; W = innerWidth; H = innerHeight;
  cv.width = W*DPR; cv.height = H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0);
}
addEventListener("resize", resize);

const PHI = () => 0.70*H;
const org = { HER:()=>({x:0.055*W,y:0.42*H,h:150}), GATE:()=>({x:0.945*W,y:0.42*H,h:22}) };

function target(n){                          // typed state → target position (the collapse)
  const phi = PHI();
  if(n.sigma==="survive") return { x:n.ax, y:phi+0.09*H };          // below Φ, typed
  if(n.sigma==="hold")    return { x:n.ax, y:phi-0.06*H };          // just above the seam (🟡)
  if(n.sigma==="compost") return { x:n.ax+ (n.seed%2?20:-20), y:0.90*H }; // sinks to substrate
  return { x:n.ax, y:n.ay };                                        // possibility → dream band
}
function spawnPos(agent){
  const phi = PHI();
  if(agent==="HER"){ const i=S.herN++; return { ax:(0.15+0.30*(i/9))*W, ay:(0.16+0.30*Math.sin(i*1.7))*H+0.14*H }; }
  if(agent==="HAL"||agent==="HAL_GATE"){ const i=S.halN++; return { ax:(0.55+0.30*(i/9))*W, ay:(0.16+0.30*Math.cos(i*1.9))*H+0.14*H }; }
  const i=S.xN++; return { ax:(0.42+0.16*Math.sin(i))*W, ay:(0.22+0.10*i)*H };   // CROSS child, center
}

function pulse(from,to,h){ S.pulses.push({fx:from.x,fy:from.y,tx:to.x,ty:to.y,h,t0:S.clock}); }

function applyEvent(e){
  const k = norm(e.name);
  if(e.type==="SPAWN"){
    const p = spawnPos(e.agent);
    const n = { name:e.name, agent:e.agent, sigma:"possibility", x:org[e.agent==="HER"?"HER":"GATE"]().x,
                y:org[e.agent==="HER"?"HER":"GATE"]().y, ax:p.ax, ay:p.ay, r:6, seed:S.order.length, glow:1, parents:[] };
    S.nodes.set(k,n); S.order.push(k);
    pulse(org[e.agent==="HER"?"HER":"GATE"](), {x:p.ax,y:p.ay}, e.agent==="HER"?150:22);
  } else if(e.type==="CROSS_POLLINATE"){
    let n = S.nodes.get(k);
    if(!n){ const p=spawnPos("CROSS"); n={ name:e.name, agent:"CROSS", sigma:"possibility",
             x:0.5*W, y:0.2*H, ax:p.ax, ay:p.ay, r:7, seed:S.order.length, glow:1.4, parents:[] };
             S.nodes.set(k,n); S.order.push(k); }
    const pk = norm(e.parent); n.parents.push(pk);
    if(S.nodes.has(pk)) S.edges.push({ a:pk, b:k, kind:"CROSS" });   // anastomosis/fusion hypha
    const pn = S.nodes.get(pk); if(pn) pulse({x:pn.x,y:pn.y},{x:n.ax,y:n.ay},190);
  } else if(e.type==="VERDICT"){
    const n = S.nodes.get(k); if(!n) return;                          // orphan guarded by R
    n.sigma = SIGMA[(e.verdict||"").toUpperCase()] || "hold";
    n.verdict = e.verdict; n.fitness = e.fitness; n.glow = 1.6;
    pulse(org.GATE(), {x:n.x,y:n.y}, 320);                            // adversarial pulse (magenta)
  } else if(e.type==="PULSE"){                                        // attack/counterfeit/discriminate
    const n = S.nodes.get(k); if(n){ n.glow = 1.8; pulse(org.GATE(), {x:n.x,y:n.y}, 330); }
  }
}

// ---- color projection: sigma → hsl. possibility shimmers (dream, non-semantic) ----
function nodeHSL(n){
  if(n.sigma==="survive") return [272,72,66];
  if(n.sigma==="hold")    return [46,92,60];
  if(n.sigma==="compost") return [2,18,30];
  const base = n.agent==="HER"?150 : n.agent==="CROSS"?190 : 24;
  return [ base + 42*Math.sin(S.clock/700 + n.seed), 88, 62 ];       // dream shimmer
}
function alpha(n){ return n.sigma==="compost" ? 0.42 : 1; }

function step(){                              // advance the fold by one witnessed event
  if(S.seq>=S.events.length) return;
  const e = S.events[S.seq++]; applyEvent(e); addRain(e); updateHUD();
}

function addRain(e){
  const host = document.getElementById("rain");
  const t = "t+"+(S.seq*0.55).toFixed(1)+"s";
  let body, cls = e._actor==="HER"?"her":(e._actor==="HAL"?"hal":"gate");
  if(LIVE){                                    // show the REAL producer op + object id
    body = `${e._actor||"?"} ${e._op}  ${e.name}` + (e.parent?` ← ${e.parent}`:"");
  } else if(e.type==="SPAWN"){ cls=e.agent==="HER"?"her":"hal"; body=`${e.agent} SPAWN  ${e.name}`; }
  else if(e.type==="CROSS_POLLINATE"){ cls="gate"; body=`CROSS  ${e.parent} × ${e.name}`; }
  else { cls="gate"; body=`Φ GATE  ${e.name}  <span class="v-${e.verdict}">${e.verdict}</span>`; }
  const d = document.createElement("div"); d.className="r "+cls;
  d.innerHTML = `<span class="dim">${t}</span> ${body}`;
  host.appendChild(d); while(host.children.length>8) host.removeChild(host.firstChild);
}

function updateHUD(){
  let poss=0,hold=0,comp=0,typed=0,cross=0;
  for(const k of S.order){ const s=S.nodes.get(k).sigma;
    if(s==="possibility")poss++; else if(s==="hold")hold++; else if(s==="compost")comp++; else if(s==="survive")typed++; }
  cross = S.edges.filter(e=>e.kind==="CROSS").length;
  set("c-poss",poss); set("c-hold",hold); set("c-compost",comp); set("c-typed",typed);
  set("c-cross",cross); set("c-seq",S.seq); set("c-tot",S.events.length);
}
const set=(id,v)=>{ document.getElementById(id).textContent=v; };

function draw(){
  S.clock = performance.now();
  if(S.clock - S.lastStep > 560){ step(); S.lastStep = S.clock; }
  ctx.clearRect(0,0,W,H);
  const phi = PHI();

  // dream sparkles above Φ (presentation entropy — decorative, non-semantic)
  for(const sp of S.sparks){ const a=0.25+0.25*Math.sin(S.clock/500+sp.p);
    ctx.globalAlpha=a; ctx.fillStyle="#bfffe0"; ctx.fillRect(sp.x, sp.y, 1.5,1.5); }
  ctx.globalAlpha=1;

  // Φ membrane
  const g = ctx.createLinearGradient(0,phi-40,0,phi+40);
  g.addColorStop(0,"rgba(120,255,190,0)"); g.addColorStop(.5,"rgba(120,255,190,.10)"); g.addColorStop(1,"rgba(2,4,10,.6)");
  ctx.fillStyle=g; ctx.fillRect(0,phi-40,W,80);
  ctx.strokeStyle="rgba(140,255,206,.55)"; ctx.lineWidth=1; ctx.setLineDash([6,6]);
  ctx.beginPath(); ctx.moveTo(0,phi); ctx.lineTo(W,phi); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle="rgba(140,255,206,.7)"; ctx.font="11px monospace";
  ctx.fillText("Φ  MEMBRANE  —  only SURVIVES crosses", 16, phi-6);

  // typed-zone watermark when empty
  const anySurv = S.order.some(k=>S.nodes.get(k).sigma==="survive");
  if(!anySurv){ ctx.fillStyle="rgba(80,140,110,.35)"; ctx.font="13px monospace";
    ctx.fillText("(( typed zone empty — HELEN dreamed "+S.order.length+" objects, 0 crossed Φ ))", W*0.28, phi+0.11*H); }

  // hyphae: faint agent→node branches, bright CROSS fusions
  for(const k of S.order){ const n=S.nodes.get(k); const o=org[n.agent==="HER"?"HER":"GATE"]();
    if(n.agent==="CROSS") continue;
    ctx.strokeStyle="rgba(90,180,140,.10)"; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(o.x,o.y); ctx.bezierCurveTo((o.x+n.x)/2,o.y,(o.x+n.x)/2,n.y,n.x,n.y); ctx.stroke(); }
  for(const e of S.edges){ const a=S.nodes.get(e.a), b=S.nodes.get(e.b); if(!a||!b) continue;
    ctx.strokeStyle="rgba(120,255,180,.5)"; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.bezierCurveTo((a.x+b.x)/2,a.y,(a.x+b.x)/2,b.y,b.x,b.y); ctx.stroke(); }

  // integrate + draw nodes
  for(const k of S.order){ const n=S.nodes.get(k); const tg=target(n);
    const bx = n.sigma==="possibility" ? tg.x+8*Math.sin(S.clock/900+n.seed) : tg.x;
    const by = n.sigma==="possibility" ? tg.y+8*Math.cos(S.clock/1100+n.seed) : tg.y;
    n.x += (bx-n.x)*0.06; n.y += (by-n.y)*0.06;
    n.r += ((n.sigma==="survive"?9:n.sigma==="compost"?4:n.sigma==="hold"?7:6)-n.r)*0.08;
    n.glow += (( n.sigma==="possibility"?0.9:0.5 )-n.glow)*0.04;
    const [h,s,l]=nodeHSL(n);
    ctx.globalAlpha=alpha(n);
    ctx.shadowBlur=20*n.glow; ctx.shadowColor=`hsl(${h},${s}%,${l}%)`;
    ctx.fillStyle=`hsl(${h},${s}%,${l}%)`;
    ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,7); ctx.fill();
    ctx.shadowBlur=0; ctx.globalAlpha=1;
  }

  // agent organisms (peripheral, breathing) — agents are NOT the foreground
  for(const [name,f] of Object.entries(org)){ const o=f(); const br=6+2*Math.sin(S.clock/600);
    ctx.shadowBlur=16; ctx.shadowColor=`hsl(${o.h},85%,60%)`; ctx.fillStyle=`hsl(${o.h},85%,60%)`;
    ctx.beginPath(); ctx.arc(o.x,o.y,br,0,7); ctx.fill(); ctx.shadowBlur=0;
    ctx.fillStyle="rgba(180,255,220,.6)"; ctx.font="10px monospace";
    ctx.fillText(name==="HER"?"🌿 HER/GEMMA":"🃏 PRE-HAL/QWEN", o.x-30, o.y+22); }

  // pulses (agent action traveling to the object)
  S.pulses = S.pulses.filter(p=>{ const dt=(S.clock-p.t0)/700; if(dt>=1) return false;
    const x=p.fx+(p.tx-p.fx)*dt, y=p.fy+(p.ty-p.fy)*dt;
    ctx.globalAlpha=1-dt; ctx.shadowBlur=12; ctx.shadowColor=`hsl(${p.h},90%,65%)`;
    ctx.fillStyle=`hsl(${p.h},90%,70%)`; ctx.beginPath(); ctx.arc(x,y,3,0,7); ctx.fill();
    ctx.shadowBlur=0; ctx.globalAlpha=1; return true; });

  requestAnimationFrame(draw);
}

async function loadLive(){                      // fetch live trace, map to internal events (same ids)
  const raw = await fetch("/api/live/events").then(r=>r.json()).catch(()=>[]);
  const known = new Set(S.events.map(e=>e._id));
  for(const le of raw){ if(!known.has(le.event_id) && le.op!=="RUN_END"){ S.events.push(fromLive(le)); } }
}
async function boot(){
  resize();
  for(let i=0;i<60;i++) S.sparks.push({ x:Math.random()*W, y:Math.random()*PHI(), p:Math.random()*6 });
  if(LIVE){
    document.getElementById("titlebar").innerHTML =
      "🌈 HELEN · J-SPACE / MYCELIUM <span class='dim'>— LIVE · two real goblins · same event ids as terminal · ΔA=0</span>";
    await loadLive();
    setInterval(loadLive, 1500);               // follow the live frontier (browser=Π(Trace))
  } else {
    S.events = await fetch("/api/events").then(r=>r.json()).catch(()=>[]);
    S.jspace = await fetch("/api/jspace").then(r=>r.json()).catch(()=>null);
    if(S.jspace) console.log("[mycelium] R counters (browser converges to):", S.jspace.counters);
  }
  requestAnimationFrame(draw);
}
boot();
