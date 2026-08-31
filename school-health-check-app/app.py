import subprocess
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def launch_streamlit_when_opened_directly():
    """コマンド入力なしで、このファイルからStreamlitを起動する。"""
    try:
        running_in_streamlit = st.runtime.exists()
    except AttributeError:
        # 古いStreamlitにも対応する。
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        running_in_streamlit = get_script_run_ctx() is not None

    if __name__ == "__main__" and not running_in_streamlit:
        app_path = str(Path(__file__).resolve())
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run", app_path],
                check=True,
            )
        except KeyboardInterrupt:
            pass
        except subprocess.CalledProcessError as error:
            raise SystemExit(
                "アプリを起動できませんでした。Streamlitがインストールされているか確認してください。"
            ) from error
        raise SystemExit


launch_streamlit_when_opened_directly()


st.set_page_config(
    page_title="ないかけんしん・おとの たいけん",
    page_icon="🩺",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background:#f4f9ff; }
      .block-container { max-width:1180px; padding-top:0.8rem; }
      .hero { padding:22px 28px; border-radius:24px; color:white;
        background:linear-gradient(135deg,#1769c2,#2ba7c9); margin-bottom:14px; }
      .hero h1 { margin:0; font-size:2.35rem; }
      .hero p { margin:10px 0 0; font-size:1.35rem; font-weight:700; }
      .note { background:#fff7d6; border-left:7px solid #f2b73e;
        padding:15px 19px; border-radius:14px; font-size:1.15rem; line-height:1.8; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🩺 しんぞうの おとを きいてみよう！</h1>
      <p>ふくの うえと、はだに あてたときの おとを くらべるよ</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note">
      👕 ふくの うえでは、「がさがさ」という おとが はいることが あります。<br>
      🩺 はだに あてると、しんぞうの おとが ききやすくなります。
    </div>
    """,
    unsafe_allow_html=True,
)


SIMULATION_HTML = r"""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Yu Gothic","Hiragino Kaku Gothic ProN",sans-serif;
    color:#263f55; background:transparent; }
  .steps { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:4px 2px 14px; }
  .step { padding:12px 8px; border-radius:15px; text-align:center; font-size:1.2rem;
    font-weight:900; color:#174d77; background:#dff2ff; border:3px solid #9bcfed; }
  .step:nth-child(2) { background:#fff0bf; border-color:#f3ca58; color:#73540b; }
  .step:nth-child(3) { background:#dff5e8; border-color:#8bd0a5; color:#206a43; }
  .app { display:grid; grid-template-columns:minmax(430px,1.08fr) minmax(350px,.92fr);
    gap:20px; padding:4px 2px 12px; }
  .panel { background:white; border:1px solid #d8e8f5; border-radius:20px;
    padding:20px; box-shadow:0 7px 20px rgba(47,84,115,.08); }
  h2 { margin:0 0 13px; color:#145eaa; font-size:1.55rem; line-height:1.45; }
  .stage { position:relative; height:535px; overflow:hidden; border-radius:18px;
    background:linear-gradient(#eaf7ff 0 78%,#dcefd5 78%); border:2px solid #cbe3f3; }
  .privacy { position:absolute; right:10px; top:14px; width:92px; height:185px;
    border:5px solid #83aabc; border-radius:8px 8px 0 0; background:#cfeef2;
    background-image:repeating-linear-gradient(90deg,transparent 0 17px,#b7dce4 18px 20px); }
  .nurse { position:absolute; right:27px; bottom:78px; font-size:56px; }
  .child { position:absolute; left:122px; top:32px; width:220px; height:465px; }
  .head { position:absolute; left:70px; top:4px; width:82px; height:82px; border-radius:50%;
    background:#ffd5b3; border:4px solid #35536c; }
  .hair { position:absolute; left:68px; top:0; width:86px; height:39px;
    border-radius:48px 48px 20px 20px; background:#3d4650; }
  .face { position:absolute; left:93px; top:39px; font-size:26px; z-index:2; }
  .torso { position:absolute; left:38px; top:88px; width:145px; height:205px;
    border-radius:45px 45px 22px 22px; background:#f2b997; border:4px solid #35536c; }
  .shirt { position:absolute; left:30px; top:84px; width:161px; height:218px;
    border-radius:46px 46px 20px 20px; background:white; border:4px solid #315976;
    transition:transform .55s ease; z-index:3; }
  .shirt:before { content:""; position:absolute; left:50px; top:-4px; width:54px; height:26px;
    border-radius:0 0 28px 28px; background:#d8edf9; border:4px solid #315976; border-top:0; }
  .shirt.lifted { transform:translateY(-122px) scaleY(.42); transform-origin:top; }
  .exam-label { position:absolute; left:51px; top:142px; width:120px; text-align:center;
    font-size:18px; font-weight:900; color:#8a4732; opacity:0; transition:opacity .3s; }
  .exam-label.show { opacity:1; }
  .arm { position:absolute; top:113px; width:30px; height:190px; background:#ffd5b3;
    border:4px solid #35536c; border-radius:18px; }
  .arm.left { left:13px; transform:rotate(6deg); } .arm.right { right:13px; transform:rotate(-6deg); }
  .shorts { position:absolute; left:42px; top:290px; width:137px; height:100px;
    background:#28577e; border:4px solid #27465f; border-radius:12px 12px 25px 25px; z-index:4; }
  .leg { position:absolute; top:380px; width:43px; height:83px; background:#ffd5b3;
    border:4px solid #35536c; border-radius:0 0 18px 18px; }
  .leg.left { left:53px; } .leg.right { right:53px; }
  .zone { position:absolute; border:3px dashed #ff8e70; border-radius:50%; z-index:6;
    background:rgba(255,255,255,.17); }
  #heartZone { left:88px; top:143px; width:62px; height:58px; }
  #lungZone { left:61px; top:114px; width:112px; height:112px; }
  .zone-label { position:absolute; left:13px; bottom:10px; padding:9px 13px; border-radius:12px;
    background:rgba(255,255,255,.94); font-size:18px; font-weight:900; }
  #scope { position:absolute; left:20px; top:35px; width:72px; height:72px; border-radius:50%;
    border:10px solid #455667; background:radial-gradient(circle,#d9e0e6 0 43%,#8796a2 44% 58%,#3a4a58 59%);
    z-index:20; cursor:grab; touch-action:none; filter:drop-shadow(0 5px 4px rgba(0,0,0,.2)); }
  #scope:after { content:""; position:absolute; width:90px; height:12px; background:#313d48;
    left:-74px; top:20px; border-radius:8px; transform:rotate(-28deg); transform-origin:right; }
  .controls { display:grid; gap:14px; align-content:start; }
  button { width:100%; min-height:64px; border:0; border-radius:17px; padding:15px 16px; font-size:1.25rem;
    font-weight:800; cursor:pointer; transition:.15s; }
  button:hover { transform:translateY(-1px); }
  .primary { background:#1876c9; color:white; }
  .secondary { background:#e9f5ff; color:#145eaa; border:2px solid #9bc9e9; }
  .privacy-btn { background:#eaf8ef; color:#25784f; border:2px solid #8ed0aa; }
  .status { min-height:136px; padding:18px; border-radius:17px; background:#eef7ff;
    border-left:8px solid #2589cf; font-size:1.2rem; line-height:1.75; }
  .meter { height:48px; display:flex; align-items:end; gap:4px; padding:7px;
    border-radius:12px; background:#172c3d; overflow:hidden; }
  .bar { width:7px; height:10px; background:#65d5ff; border-radius:5px; }
  .meter.active .bar { animation:bounce .45s infinite alternate; }
  .meter.noisy .bar { background:#ffbf54; animation-duration:.16s; }
  @keyframes bounce { to { height:38px; } }
  .check { margin-top:10px; padding:16px; background:#fff8d9; border-radius:14px;
    font-size:1.1rem; line-height:1.8; }
  .legend { display:flex; gap:8px; flex-wrap:wrap; margin:10px 0; }
  .pill { padding:9px 13px; border-radius:999px; background:#edf5fa; font-size:1.05rem; font-weight:800; }
  @media(max-width:820px){
    .steps{grid-template-columns:1fr}.app{grid-template-columns:1fr}.stage{height:510px}
    .child{left:50%;transform:translateX(-50%)}
  }
</style>
</head>
<body>
<div class="steps">
  <div class="step">① うごかす 🩺</div>
  <div class="step">② きく 🔊</div>
  <div class="step">③ くらべる 💡</div>
</div>
<div class="app">
  <section class="panel">
    <h2>① ちょうしんきを うごかして<br>むねの まるに おこう</h2>
    <div class="stage" id="stage">
      <div class="privacy" id="screen"></div><div class="nurse">🧑‍⚕️</div>
      <div id="scope" title="ゆびで うごかしてね"></div>
      <div class="child">
        <div class="head"></div><div class="hair"></div><div class="face">•ᴗ•</div>
        <div class="torso"></div><div class="exam-label" id="skinLabel">おとを<br>きく ところ</div>
        <div class="arm left"></div><div class="arm right"></div>
        <div class="shirt" id="shirt"></div>
        <div class="zone" id="lungZone"></div><div class="zone" id="heartZone"></div>
        <div class="shorts"></div><div class="leg left"></div><div class="leg right"></div>
      </div>
      <div class="zone-label">🟠 この まるに おこう</div>
    </div>
  </section>

  <section class="panel controls">
    <h2>② ふくを うごかして<br>おとを くらべよう</h2>
    <button class="secondary" id="clothesBtn">👕 いまは「ふくの うえ」</button>
    <button class="primary" id="listenBtn">🔊 おとを きく</button>
    <div class="meter" id="meter">
      <span class="bar"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span>
      <span class="bar"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span>
      <span class="bar"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span>
    </div>
    <div class="status" id="status">
      ちょうしんきを むねの まるまで うごかしてね。<br>
      <b>はじめは ふくの うえから きいてみよう！</b>
    </div>
    <div class="legend">
      <span class="pill">❤️ しんぞう：どくん どくん</span>
      <span class="pill">👕 ふく：がさがさ</span>
    </div>
    <button class="privacy-btn" id="privacyBtn">🟦 からだが みえない くふう</button>
    <div class="check" id="privacyText" hidden>
      ✓ カーテンや ついたてを つかうよ<br>
      ✓ ひつような ところだけ みるよ<br>
      ✓ タオルで からだを かくせるよ<br>
      ✓ いやなときは「いや」と いっていいよ
    </div>
  </section>
</div>

<script>
  const scope = document.getElementById('scope');
  const stage = document.getElementById('stage');
  const shirt = document.getElementById('shirt');
  const clothesBtn = document.getElementById('clothesBtn');
  const listenBtn = document.getElementById('listenBtn');
  const statusBox = document.getElementById('status');
  const meter = document.getElementById('meter');
  const privacyBtn = document.getElementById('privacyBtn');
  const privacyText = document.getElementById('privacyText');
  const skinLabel = document.getElementById('skinLabel');
  let lifted = false, placed = false, dragging = false, dx = 0, dy = 0;
  let audioCtx = null, timers = [];

  function pointerStart(e){
    dragging = true; scope.setPointerCapture(e.pointerId);
    const r = scope.getBoundingClientRect(); dx=e.clientX-r.left; dy=e.clientY-r.top;
  }
  function pointerMove(e){
    if(!dragging) return;
    const r=stage.getBoundingClientRect();
    let x=Math.max(0,Math.min(r.width-72,e.clientX-r.left-dx));
    let y=Math.max(0,Math.min(r.height-72,e.clientY-r.top-dy));
    scope.style.left=x+'px'; scope.style.top=y+'px';
  }
  function pointerEnd(){
    dragging=false;
    const s=scope.getBoundingClientRect(), z=document.getElementById('lungZone').getBoundingClientRect();
    const cx=s.left+s.width/2, cy=s.top+s.height/2;
    placed = cx>z.left-30 && cx<z.right+30 && cy>z.top-30 && cy<z.bottom+45;
    statusBox.innerHTML = placed
      ? 'じょうずに おけたよ！<br><b>「おとを きく」を おしてね。</b>'
      : 'もうすこし むねの まるへ うごかしてみよう。';
  }
  scope.addEventListener('pointerdown',pointerStart);
  scope.addEventListener('pointermove',pointerMove);
  scope.addEventListener('pointerup',pointerEnd);

  clothesBtn.onclick=()=>{
    lifted=!lifted; shirt.classList.toggle('lifted',lifted); skinLabel.classList.toggle('show',lifted);
    clothesBtn.textContent=lifted?'🩺 いまは「はだに ちょくせつ」':'👕 いまは「ふくの うえ」';
    clothesBtn.className=lifted?'privacy-btn':'secondary';
    statusBox.innerHTML=lifted
      ? 'ふくを すこし うごかしたよ。<br><b>もういちど おとを きいてみよう！</b>'
      : 'ふくを もとに もどしたよ。ふくの うえから きいてみよう。';
  };

  function tone(ctx,time,freq,duration,gainValue){
    const osc=ctx.createOscillator(), gain=ctx.createGain();
    osc.type='sine'; osc.frequency.value=freq;
    gain.gain.setValueAtTime(0,time); gain.gain.linearRampToValueAtTime(gainValue,time+.015);
    gain.gain.exponentialRampToValueAtTime(.001,time+duration);
    osc.connect(gain).connect(ctx.destination); osc.start(time); osc.stop(time+duration);
  }
  function noise(ctx,time,duration,level){
    const length=Math.floor(ctx.sampleRate*duration), buffer=ctx.createBuffer(1,length,ctx.sampleRate);
    const data=buffer.getChannelData(0); for(let i=0;i<length;i++) data[i]=(Math.random()*2-1);
    const src=ctx.createBufferSource(), filter=ctx.createBiquadFilter(), gain=ctx.createGain();
    src.buffer=buffer; filter.type='bandpass'; filter.frequency.value=lifted?700:1500;
    gain.gain.value=level; src.connect(filter).connect(gain).connect(ctx.destination);
    src.start(time); src.stop(time+duration);
  }
  function playSample(){
    if(!placed){ statusBox.innerHTML='さきに ちょうしんきを むねの まるへ うごかしてね。'; return; }
    if(audioCtx) audioCtx.close(); audioCtx=new (window.AudioContext||window.webkitAudioContext)();
    const now=audioCtx.currentTime+.05; meter.className='meter active'+(lifted?'':' noisy');
    for(let i=0;i<7;i++){
      const t=now+i*.72; tone(audioCtx,t,62,.13,lifted?.19:.09); tone(audioCtx,t+.18,48,.16,lifted?.16:.07);
    }
    if(!lifted){ for(let i=0;i<12;i++) noise(audioCtx,now+i*.35,.16,.09); }
    statusBox.innerHTML=lifted
      ? 'はだに あてると、「がさがさ」が へって、<br><b>しんぞうの おとが ききやすいね！</b>'
      : 'ふくの「がさがさ」が まざって、<br><b>しんぞうの おとが ききにくいことが あるね。</b>';
    setTimeout(()=>meter.className='meter',5200);
  }
  listenBtn.onclick=playSample;
  privacyBtn.onclick=()=>{ privacyText.hidden=!privacyText.hidden; };
</script>
</body>
</html>
"""

components.html(SIMULATION_HTML, height=970, scrolling=True)

st.info(
    "この おとは、べんきょうの ために つくった おとです。ほんものの こどもの おとでは ありません。"
)

with st.expander("💡 わかったかな？"):
    answer = st.radio(
        "どうして ちょうしんきを はだに あてるの？",
        ["えらんでね", "がさがさの おとを へらすため", "ちょうしんきを あたためるため", "せの たかさを はかるため"],
    )
    if st.button("こたえを みる", type="primary"):
        if answer == "がさがさの おとを へらすため":
            st.success("せいかい！ しんぞうの おとが ききやすくなるよ。")
        else:
            st.warning("もういちど おとを くらべてみよう。")

st.caption(
    "※これは けんしんの まえに べんきょうする ための アプリです。びょうきを きめる アプリでは ありません。"
)
