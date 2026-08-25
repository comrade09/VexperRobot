"""
pdf2cbt.html_gen
Turns the structured question data (from parser.parse_pdf) into a single,
self-contained HTML file that behaves like a real CBT (computer-based test):
  - overall countdown timer (auto-submits on expiry)
  - subject tabs + numbered question palette
    (not visited / not answered / answered / marked for review / answered & marked)
  - previous / save & next / mark for review / clear response
  - final submit with confirmation, then a full scorecard:
    total score, subject-wise score, correct/wrong/unattempted, per-question review
  - NEET/JEE-style default marking (+4 correct, -1 wrong, 0 unattempted) - editable
    in the SCORING dict below before generating, or overridable per call.
"""
import json
import html as _html

PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ — CBT</title>
<style>
  :root{
    --nav:#0b2e59; --nav2:#123b73; --accent:#0d6efd; --green:#3fae4a;
    --purple:#9c27b0; --red:#e53935; --grey:#8a8a8a; --bg:#eef1f5;
  }
  *{box-sizing:border-box;}
  body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:var(--bg);color:#222;}
  header{background:var(--nav);color:#fff;padding:10px 16px;display:flex;justify-content:space-between;
         align-items:center;flex-wrap:wrap;gap:8px;position:sticky;top:0;z-index:50;}
  header .title{font-weight:600;font-size:15px;}
  #timer{background:#fff;color:var(--nav);font-weight:700;padding:6px 14px;border-radius:6px;font-size:16px;letter-spacing:1px;}
  #timer.low{color:#fff;background:var(--red);}
  .subject-tabs{display:flex;gap:4px;background:var(--nav2);padding:6px 10px;overflow-x:auto;}
  .subject-tabs button{background:transparent;border:none;color:#cfe0ff;padding:8px 14px;border-radius:6px 6px 0 0;
         cursor:pointer;font-size:13px;white-space:nowrap;}
  .subject-tabs button.active{background:var(--bg);color:var(--nav);font-weight:700;}
  .layout{display:flex;gap:0;align-items:flex-start;}
  main{flex:1;min-width:0;padding:16px;padding-bottom:90px;}
  aside{width:270px;flex-shrink:0;background:#fff;border-left:1px solid #d8d8d8;padding:14px;
        max-height:calc(100vh - 96px);overflow-y:auto;position:sticky;top:96px;}
  @media (max-width:820px){
    .layout{flex-direction:column;}
    aside{width:100%;position:static;max-height:none;order:2;}
    main{order:1;padding-bottom:16px;}
  }
  .qcard{background:#fff;border-radius:8px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,.12);}
  .qhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
  .qhead b{font-size:15px;color:var(--nav);}
  .qstem{font-size:15px;line-height:1.55;margin-bottom:14px;}
  .qstem img{max-width:100%;height:auto;display:block;margin:6px 0;}
  .qstem p{margin:0 0 6px 0;}
  .opt{display:flex;align-items:flex-start;gap:10px;border:1px solid #e0e0e0;border-radius:8px;
       padding:10px 12px;margin-bottom:10px;cursor:pointer;transition:.15s;}
  .opt:hover{border-color:var(--accent);}
  .opt.selected{border-color:var(--accent);background:#e8f1ff;}
  .opt input{margin-top:3px;flex-shrink:0;}
  .optbody{font-size:14.5px;line-height:1.5;}
  .optbody img{max-width:100%;height:auto;}
  .optbody p{margin:0;}
  .btnrow{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
  button.act{border:none;border-radius:6px;padding:10px 16px;font-size:13.5px;cursor:pointer;font-weight:600;}
  .b-mark{background:#7b3fae;color:#fff;}
  .b-clear{background:#6c757d;color:#fff;}
  .b-prev{background:#adb5bd;color:#222;}
  .b-save{background:var(--green);color:#fff;}
  .b-submit{background:var(--red);color:#fff;}
  .footerbar{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #ddd;
             padding:10px 16px;display:flex;justify-content:space-between;align-items:center;z-index:40;}
  .footerbar .right{display:flex;gap:8px;}
  .legend{display:flex;flex-wrap:wrap;gap:8px;font-size:11.5px;margin-bottom:12px;}
  .legend span{display:flex;align-items:center;gap:4px;}
  .dot{width:12px;height:12px;border-radius:3px;display:inline-block;}
  .pal-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;}
  .pal-grid button{border:none;border-radius:4px;height:34px;font-size:12.5px;font-weight:700;cursor:pointer;color:#fff;background:#8a8a8a;}
  .st-notvisited{background:#8a8a8a !important;color:#fff;}
  .st-notanswered{background:var(--red) !important;color:#fff;}
  .st-answered{background:var(--green) !important;color:#fff;}
  .st-marked{background:var(--purple) !important;color:#fff;}
  .st-markedans{background:var(--purple) !important;color:#fff;box-shadow:inset 0 0 0 3px var(--green);}
  .pal-grid button.current{outline:3px solid #ffb300;}
  #startScreen,#resultScreen{max-width:720px;margin:40px auto;background:#fff;border-radius:10px;
        padding:30px 26px;box-shadow:0 2px 10px rgba(0,0,0,.15);}
  #startScreen h2,#resultScreen h2{color:var(--nav);margin-top:0;}
  #startScreen label{display:block;margin:14px 0 6px;font-size:13.5px;font-weight:600;}
  #startScreen input[type=number]{padding:8px;border:1px solid #ccc;border-radius:6px;width:120px;font-size:14px;}
  #startScreen button, #resultScreen button{margin-top:20px;background:var(--nav);color:#fff;border:none;
        padding:12px 22px;border-radius:6px;font-size:15px;cursor:pointer;font-weight:700;}
  .score-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:18px 0;}
  .score-box{background:#f4f6fa;border-radius:8px;padding:14px;text-align:center;}
  .score-box b{display:block;font-size:22px;color:var(--nav);}
  .score-box span{font-size:12px;color:#555;}
  table.subjtbl{width:100%;border-collapse:collapse;margin-top:10px;font-size:13.5px;}
  table.subjtbl th,table.subjtbl td{border:1px solid #ddd;padding:8px;text-align:center;}
  table.subjtbl th{background:#f1f3f6;}
  .review-list{margin-top:22px;}
  .review-item{border:1px solid #e2e2e2;border-radius:8px;padding:12px 14px;margin-bottom:10px;}
  .review-item.correct{border-left:5px solid var(--green);}
  .review-item.wrong{border-left:5px solid var(--red);}
  .review-item.skipped{border-left:5px solid var(--grey);}
  .tag{display:inline-block;font-size:11px;padding:2px 8px;border-radius:10px;color:#fff;margin-left:6px;}
  .tag.correct{background:var(--green);}
  .tag.wrong{background:var(--red);}
  .tag.skipped{background:var(--grey);}
  .hide{display:none !important;}

  /* ===== Join-channel popup ===== */
  .jc-popup-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;
      align-items:center;justify-content:center;z-index:99999;animation:jcFadeIn .2s ease;}
  @keyframes jcFadeIn{from{opacity:0;}to{opacity:1;}}
  .jc-popup-box{background:#fff;border-radius:14px;padding:28px 24px 22px;width:90%;max-width:320px;
      text-align:center;position:relative;box-shadow:0 12px 40px rgba(0,0,0,.25);font-family:inherit;}
  .jc-popup-close{position:absolute;top:8px;right:10px;background:none;border:none;font-size:22px;
      line-height:1;cursor:pointer;color:#888;padding:4px;}
  .jc-popup-close:hover{color:#333;}
  .jc-popup-icon{font-size:32px;margin-bottom:6px;}
  .jc-popup-title{margin:0 0 6px;font-size:17px;font-weight:700;color:var(--nav);}
  .jc-popup-text{margin:0 0 16px;font-size:13.5px;color:#555;line-height:1.4;}
  .jc-popup-btn{display:inline-block;background:#229ED9;color:#fff !important;text-decoration:none;
      font-weight:600;font-size:14px;padding:10px 22px;border-radius:8px;transition:background .15s ease;}
  .jc-popup-btn:hover{background:#1b87bd;}
</style>
</head>
<body>

<div id="startScreen">
  <h2>__TITLE__</h2>
  <p>__TOTAL_Q__ questions &middot; __SUBJ_SUMMARY__</p>
  <label>Test duration (minutes)</label>
  <input type="number" id="durationInput" value="__DEFAULT_MINUTES__" min="1">
  <p style="font-size:13px;color:#555;margin-top:16px;">Marking scheme: +__MARK_CORRECT__ for a correct answer,
     __MARK_WRONG__ for a wrong answer, 0 for unattempted. Once you start, the timer runs continuously —
     the test auto-submits when time is up.</p>
  <button onclick="startTest()">Start Test</button>
</div>

<div id="testScreen" class="hide">
  <header>
    <div class="title">__TITLE__</div>
    <div id="timer">--:--:--</div>
    <div>
      <button class="act b-submit" onclick="confirmSubmit()">Submit Test</button>
    </div>
  </header>
  <div class="subject-tabs" id="subjectTabs"></div>
  <div class="layout">
    <main>
      <div class="qcard">
        <div class="qhead"><b id="qLabel"></b><span id="qMeta" style="font-size:12px;color:#777;"></span></div>
        <div class="qstem" id="qStem"></div>
        <div id="qOptions"></div>
        <div class="btnrow">
          <button class="act b-mark" onclick="markReview()">Mark for Review &amp; Next</button>
          <button class="act b-clear" onclick="clearResponse()">Clear Response</button>
        </div>
      </div>
    </main>
    <aside>
      <div class="legend">
        <span><i class="dot st-notvisited"></i>Not visited</span>
        <span><i class="dot st-notanswered"></i>Not answered</span>
        <span><i class="dot st-answered"></i>Answered</span>
        <span><i class="dot st-marked"></i>Marked</span>
        <span><i class="dot st-markedans"></i>Marked &amp; answered</span>
      </div>
      <div class="pal-grid" id="palette"></div>
    </aside>
  </div>
  <div class="footerbar">
    <button class="act b-prev" onclick="goPrev()">&larr; Previous</button>
    <div class="right">
      <button class="act b-save" onclick="goNext()">Save &amp; Next &rarr;</button>
    </div>
  </div>
</div>

<div id="resultScreen" class="hide"></div>

<!-- ===== Join-channel popup ===== -->
<div id="joinChannelPopup" class="jc-popup-overlay" style="display:none;">
  <div class="jc-popup-box">
    <button type="button" class="jc-popup-close" onclick="jcClosePopup()" aria-label="Close">&times;</button>
    <div class="jc-popup-icon">📢</div>
    <h3 class="jc-popup-title">Join our Telegram Channel</h3>
    <p class="jc-popup-text">Get more free tests, updates and study resources.</p>
    <a href="https://t.me/a3xarva" target="_blank" rel="noopener noreferrer" class="jc-popup-btn">Join Channel</a>
  </div>
</div>

<script id="testData" type="application/json">__DATA_JSON__</script>
<script>
const DATA = JSON.parse(document.getElementById('testData').textContent);
const MARK_CORRECT = __MARK_CORRECT__;
const MARK_WRONG = __MARK_WRONG__;

// Flatten questions in order, keep subject index
let QUESTIONS = [];
DATA.subjects.forEach((s, si) => {
  s.questions.forEach(q => {
    QUESTIONS.push({...q, subjIdx: si, subjName: s.name});
  });
});
const N = QUESTIONS.length;
let selected = new Array(N).fill(null);     // chosen option 1-4 or null
let status = new Array(N).fill('notvisited'); // notvisited|notanswered|answered|marked|markedans
let current = 0;
let remainingSec = 0;
let timerHandle = null;
let submitted = false;

function startTest(){
  const mins = parseFloat(document.getElementById('durationInput').value) || __DEFAULT_MINUTES__;
  remainingSec = Math.round(mins*60);
  document.getElementById('startScreen').classList.add('hide');
  document.getElementById('testScreen').classList.remove('hide');
  buildSubjectTabs();
  buildPalette();
  goTo(0);
  timerHandle = setInterval(tick, 1000);
  tick();
}

function tick(){
  if(submitted) return;
  remainingSec--;
  const h = Math.floor(remainingSec/3600), m = Math.floor((remainingSec%3600)/60), s = remainingSec%60;
  const el = document.getElementById('timer');
  el.textContent = [h,m,s].map(x=>String(x).padStart(2,'0')).join(':');
  if(remainingSec <= 300) el.classList.add('low');
  if(remainingSec <= 0){
    clearInterval(timerHandle);
    doSubmit(true);
  }
}

function buildSubjectTabs(){
  const box = document.getElementById('subjectTabs');
  box.innerHTML = '';
  DATA.subjects.forEach((s, si) => {
    const b = document.createElement('button');
    b.textContent = s.name + ' (' + s.questions.length + ')';
    b.onclick = () => {
      const firstIdx = QUESTIONS.findIndex(q => q.subjIdx === si);
      goTo(firstIdx);
    };
    b.dataset.idx = si;
    box.appendChild(b);
  });
}

function refreshSubjectTabs(){
  const activeSubj = QUESTIONS[current].subjIdx;
  document.querySelectorAll('#subjectTabs button').forEach(b=>{
    b.classList.toggle('active', parseInt(b.dataset.idx)===activeSubj);
  });
}

function buildPalette(){
  const grid = document.getElementById('palette');
  grid.innerHTML = '';
  QUESTIONS.forEach((q,i)=>{
    const btn = document.createElement('button');
    btn.textContent = (i+1);
    btn.id = 'pal-'+i;
    btn.className = 'st-notvisited';
    btn.onclick = () => goTo(i);
    grid.appendChild(btn);
  });
}

function refreshPalette(){
  QUESTIONS.forEach((q,i)=>{
    const btn = document.getElementById('pal-'+i);
    btn.className = 'st-'+status[i] + (i===current ? ' current' : '');
  });
}

function renderQuestion(){
  const q = QUESTIONS[current];
  document.getElementById('qLabel').textContent = q.subjName + ' — Question ' + (current+1) + ' of ' + N;
  document.getElementById('qMeta').textContent = 'Q.No ' + (current+1);
  document.getElementById('qStem').innerHTML = q.stem_html;
  const optBox = document.getElementById('qOptions');
  optBox.innerHTML = '';
  q.options_html.forEach((html, idx) => {
    const n = idx+1;
    const row = document.createElement('label');
    row.className = 'opt' + (selected[current]===n ? ' selected' : '');
    row.innerHTML = '<input type="radio" name="opt" '+(selected[current]===n?'checked':'')+'>' +
                     '<div class="optbody">'+html+'</div>';
    row.onclick = () => { selectOption(n); };
    optBox.appendChild(row);
  });
}

function selectOption(n){
  selected[current] = n;
  if(status[current] === 'marked' || status[current]==='markedans') status[current] = 'markedans';
  else status[current] = 'answered';
  renderQuestion();
  refreshPalette();
}

function clearResponse(){
  selected[current] = null;
  status[current] = (status[current]==='markedans') ? 'marked' : 'notanswered';
  renderQuestion();
  refreshPalette();
}

function markReview(){
  status[current] = (selected[current]!=null) ? 'markedans' : 'marked';
  goNext();
}

function goTo(i){
  if(i<0 || i>=N) return;
  if(status[current]==='notvisited') status[current]='notanswered';
  current = i;
  if(status[current]==='notvisited') status[current]='notanswered';
  renderQuestion();
  refreshPalette();
  refreshSubjectTabs();
  window.scrollTo({top:0,behavior:'smooth'});
}

function goNext(){
  if(status[current]==='notvisited') status[current]='notanswered';
  if(current < N-1) goTo(current+1); else { refreshPalette(); }
}
function goPrev(){ goTo(current-1); }

function confirmSubmit(){
  const unanswered = status.filter(s=>s==='notanswered'||s==='notvisited'||s==='marked').length;
  const msg = unanswered>0
     ? ('You have '+unanswered+' unanswered question(s). Submit anyway?')
     : 'Submit the test now?';
  if(confirm(msg)) doSubmit(false);
}

function doSubmit(auto){
  if(submitted) return;
  submitted = true;
  clearInterval(timerHandle);
  document.getElementById('testScreen').classList.add('hide');
  showResults(auto);
}

function showResults(auto){
  let totalCorrect=0, totalWrong=0, totalSkip=0, totalScore=0;
  const bySubj = {};
  DATA.subjects.forEach(s=> bySubj[s.name] = {correct:0,wrong:0,skip:0,score:0,max:s.questions.length});

  const reviewHtml = [];
  QUESTIONS.forEach((q,i)=>{
    const chosen = selected[i];
    const correctAns = q.answer;
    let cls, tag, delta;
    if(chosen==null){
      cls='skipped'; tag='Skipped'; delta=0; totalSkip++; bySubj[q.subjName].skip++;
    } else if(correctAns!=null && chosen===correctAns){
      cls='correct'; tag='Correct'; delta=MARK_CORRECT; totalCorrect++; bySubj[q.subjName].correct++;
    } else {
      cls='wrong'; tag='Wrong'; delta=MARK_WRONG; totalWrong++; bySubj[q.subjName].wrong++;
    }
    totalScore += delta;
    bySubj[q.subjName].score += delta;
    const yourAnsTxt = chosen ? ('Option '+chosen) : '—';
    const correctTxt = correctAns ? ('Option '+correctAns) : 'N/A';
    reviewHtml.push(
      '<div class="review-item '+cls+'">'+
      '<b>Q'+(i+1)+'. '+q.subjName+'</b><span class="tag '+cls+'">'+tag+' ('+(delta>0?'+':'')+delta+')</span>'+
      '<div class="qstem" style="margin-top:8px;">'+q.stem_html+'</div>'+
      '<div style="font-size:13.5px;">Your answer: <b>'+yourAnsTxt+'</b> &nbsp;|&nbsp; Correct answer: <b>'+correctTxt+'</b></div>'+
      '</div>'
    );
  });

  let subjRows = '';
  Object.keys(bySubj).forEach(name=>{
    const b = bySubj[name];
    subjRows += '<tr><td>'+name+'</td><td>'+b.max+'</td><td>'+b.correct+'</td><td>'+b.wrong+'</td>'+
                '<td>'+b.skip+'</td><td>'+b.score+'</td></tr>';
  });

  const maxPossible = N*MARK_CORRECT;
  const resultBox = document.getElementById('resultScreen');
  resultBox.innerHTML =
    '<h2>'+(auto?'Time Up — ':'')+'Test Submitted</h2>'+
    '<div class="score-grid">'+
      '<div class="score-box"><b>'+totalScore+' / '+maxPossible+'</b><span>Total Score</span></div>'+
      '<div class="score-box"><b>'+totalCorrect+'</b><span>Correct</span></div>'+
      '<div class="score-box"><b>'+totalWrong+'</b><span>Wrong</span></div>'+
      '<div class="score-box"><b>'+totalSkip+'</b><span>Unattempted</span></div>'+
    '</div>'+
    '<table class="subjtbl"><tr><th>Subject</th><th>Total</th><th>Correct</th><th>Wrong</th><th>Skipped</th><th>Score</th></tr>'+
    subjRows+'</table>'+
    '<div class="review-list"><h3>Answer Review</h3>'+reviewHtml.join('')+'</div>'+
    '<button onclick="location.reload()">Retake Test</button>';
  resultBox.classList.remove('hide');
  window.scrollTo({top:0,behavior:'smooth'});
}

// ===== Join-channel popup: shows shortly after open, then every 5 min =====
function jcShowPopup(){
  const el = document.getElementById('joinChannelPopup');
  if(el) el.style.display = 'flex';
}
function jcClosePopup(){
  const el = document.getElementById('joinChannelPopup');
  if(el) el.style.display = 'none';
}
setTimeout(jcShowPopup, 1200);
setInterval(jcShowPopup, 5 * 60 * 1000);
</script>
</body>
</html>
"""


def render_cbt_html(data, title="Mock Test", default_minutes=180,
                     mark_correct=4, mark_wrong=-1):
    subj_summary = ", ".join(f'{s["name"]} {len(s["questions"])}' for s in data["subjects"])
    html_out = (PAGE_TEMPLATE
                .replace("__TITLE__", _html.escape(title))
                .replace("__TOTAL_Q__", str(data["total"]))
                .replace("__SUBJ_SUMMARY__", _html.escape(subj_summary))
                .replace("__DEFAULT_MINUTES__", str(default_minutes))
                .replace("__MARK_CORRECT__", str(mark_correct))
                .replace("__MARK_WRONG__", str(mark_wrong))
                .replace("__DATA_JSON__", json.dumps(data)))
    return html_out


if __name__ == "__main__":
    import sys
    from plugins.parser import parse_pdf
    data = parse_pdf(sys.argv[1])
    out = render_cbt_html(data, title="ALLEN Mock Test")
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", sys.argv[2], len(out), "bytes")
