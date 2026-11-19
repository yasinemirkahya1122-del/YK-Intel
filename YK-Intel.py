"""

YK-Intel 
Kurulum:  pip install flask google-genai ddgs

"""
import os
import threading
import webbrowser

from flask import Flask, render_template_string, request, jsonify

try:
    from google import genai
    from google.genai import types
    GENAI_OK = True
except ImportError:
    GENAI_OK = False

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

app = Flask(__name__)

MODELS = [m.strip() for m in os.environ.get(
    "GEMINI_MODELS", "gemini-2.5-flash,gemini-2.5-flash-lite").split(",") if m.strip()]

SYSTEM = (
    "Sen bir arama ve araştırma asistanısın  ismin eğer sorulursa ismin yok sadece osint amacıyla kullanılan bir yapay zeka asistanısın. Kullanıcının yazdığı konuyu/ismi internette ara, bir kişi sorulduğunda yanlızca o kişi hakkında kapsamlı ve uzun bilgiler ver isim benzerliği olan kişileri söyleme eğer o kişiyi bulamadıysan bu kişi hakkında internette hiç bir dijital ayak izi bulamadım de"
    "bulduklarını düzenli ve anlaşılır şekilde Türkçe söyle eğer abartı şekilde uzunsa özetle (kullanıcı başka dilde yazdıysa o dilde yanıtla). "
    "Başlıklar ve kısa maddeler kullan. Sadece bulduğun bilgilere dayan, uydurma. "
    "Bir kişi araması ise ve isimleri birebir aynı ise belirt ve hepsi hakkında bilgi ver. "
    "KURAL: T.C. kimlik numarası, ev adresi, sızdırılmış/özel veri verme; "
    "böyle bir şey görürsen rapora ekleme."
)


def sources_from_grounding(resp):
    out, seen = [], set()
    try:
        gm = resp.candidates[0].grounding_metadata
        for ch in (gm.grounding_chunks or []):
            w = ch.web
            if w and w.uri and w.uri not in seen:
                seen.add(w.uri)
                out.append({"title": w.title or w.uri, "url": w.uri})
    except Exception:
        pass
    return out


def search_with_gemini(client, query):
    """Gemini'nin yerleşik Google Search aracıyla ara + özetle."""
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )
    last = ""
    for m in MODELS:
        try:
            resp = client.models.generate_content(model=m, contents=query, config=cfg)
            if resp and resp.text:
                return resp.text, sources_from_grounding(resp), m
        except Exception as e:
            last = str(e)
    raise RuntimeError(last or "Gemini yanıt vermedi")


def search_with_ddg(client, query):
    """Yedek: DuckDuckGo sonuçlarını çek, Gemini'ye özetlet (o da olmazsa ham sonuçları göster)."""
    if DDGS is None:
        raise RuntimeError("Yedek arama için: pip install ddgs")
    results = []
    for region in ("tr-tr", "wt-wt", "us-en"):
        try:
            results = list(DDGS().text(query, region=region, max_results=10))
        except Exception:
            results = []
        if results:
            break
    sources = [{"title": r.get("title", ""), "url": r.get("href", "")} for r in results]
    if not results:
        return "Sonuç bulunamadı.", [], "ddgs"

    blob = "\n\n".join(
        f"[{i+1}] {r.get('title','')}\n{r.get('href','')}\n{r.get('body','')}"
        for i, r in enumerate(results)
    )
    prompt = (f"{SYSTEM}\n\nKullanıcının aramasi: {query}\n\n"
              f"Aşağıdaki arama sonuçlarına dayanarak özetle, kaynak numaralarını [1], [2] şeklinde belirt:\n\n{blob}")
    for m in MODELS:
        try:
            resp = client.models.generate_content(model=m, contents=prompt)
            if resp and resp.text:
                return resp.text, sources, f"ddgs+{m}"
        except Exception:
            continue

    raw = "\n\n".join(f"**{r.get('title','')}**\n{r.get('body','')}" for r in results)
    return "_AI özeti alınamadı, ham sonuçlar:_\n\n" + raw, sources, "ddgs"


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/search", methods=["POST"])
def api_search():
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    api_key = (body.get("api_key") or os.environ.get("GEMINI_API_KEY", "")).strip()

    if not query:
        return jsonify({"status": "error", "message": "Bir şey yaz!"})
    if len(query) > 500:
        return jsonify({"status": "error", "message": "Arama çok uzun (en fazla 500 karakter)."})
    if not GENAI_OK:
        return jsonify({"status": "error", "message": "Terminale yaz: pip install google-genai"})
    if not api_key:
        return jsonify({"status": "error", "message": "Gemini API anahtarı gerekli."})

    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1beta"))
    errors = []
    try:
        text, sources, used = search_with_gemini(client, query)
        return jsonify({"status": "success", "result": text, "sources": sources, "via": used})
    except Exception as e:
        errors.append(f"Gemini arama: {e}")
    try:
        text, sources, used = search_with_ddg(client, query)
        return jsonify({"status": "success", "result": text, "sources": sources, "via": used})
    except Exception as e:
        errors.append(f"Yedek arama: {e}")
    return jsonify({"status": "error", "message": " | ".join(errors)})


HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YK-Intel</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js"></script>
<style>
  .md h1,.md h2,.md h3{font-weight:700;margin:1rem 0 .4rem;color:#a5b4fc}
  .md h1{font-size:1.3rem}.md h2{font-size:1.15rem}.md h3{font-size:1.05rem}
  .md p{margin:.5rem 0;line-height:1.6}
  .md ul{list-style:disc;margin:.5rem 0 .5rem 1.4rem}
  .md ol{list-style:decimal;margin:.5rem 0 .5rem 1.4rem}
  .md a{color:#818cf8;text-decoration:underline}
  .md strong{color:#fff}
  .md code{background:#1f2937;padding:1px 5px;border-radius:4px}
</style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen p-4 flex justify-center">
<div class="w-full max-w-3xl mt-8">
  <h1 class="text-3xl font-bold text-indigo-400 text-center">YK-Intel</h1>
  <p class="text-xs text-gray-500 text-center mb-6">YK-Intel • İnternette ara • sonuçları topla • Gemini ile özetle</p>

  <div id="keyBox" class="mb-4">
    <input id="key" type="password" placeholder="Gemini API anahtarı"
      class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:border-indigo-500">
    <a href="https://www.youtube.com/results?search_query=gemini+api+key+nasıl+alınır" target="_blank" rel="noopener"
       class="text-xs text-indigo-400 underline">Ücretsiz API anahtarı al</a>
    <span class="text-xs text-gray-600"> • Gemini API anahtarı olmadan sonuç alamazsınız</span>
  </div>

  <div class="flex gap-2">
    <input id="q" autofocus placeholder="Bir isim, ya da soru yaz... "
      class="flex-1 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:border-indigo-500"
      onkeydown="if(event.key==='Enter')search()">
    <button id="btn" onclick="search()" class="bg-indigo-600 hover:bg-indigo-500 px-6 rounded-lg font-medium disabled:opacity-50">Ara</button>
  </div>

  <div id="loading" class="hidden text-center text-indigo-400 text-sm py-6 animate-pulse">İnternette aranıyor ve özetleniyor...</div>
  <div id="error" class="hidden mt-4 text-red-400 text-sm bg-gray-900 border border-red-900 rounded-lg p-3"></div>

  <div id="result" class="hidden mt-5 bg-gray-900 border border-gray-800 rounded-xl p-5">
    <div id="answer" class="md text-sm"></div>
    <div id="srcWrap" class="hidden mt-5 pt-4 border-t border-gray-800">
      <div class="text-xs uppercase text-gray-500 mb-2">Kaynaklar</div>
      <div id="sources" class="space-y-1 text-sm"></div>
    </div>
    <div id="via" class="text-[10px] text-gray-600 mt-4"></div>
  </div>
</div>

<script>
async function search(){
  const q = document.getElementById("q").value.trim();
  if(!q) return;
  const $ = id => document.getElementById(id);
  $("error").classList.add("hidden");
  $("result").classList.add("hidden");
  $("loading").classList.remove("hidden");
  $("btn").disabled = true;
  try{
    const r = await fetch("/api/search", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({query:q, api_key:$("key").value.trim()})});
    const d = await r.json();
    if(d.status !== "success"){ $("error").textContent = "Hata: " + d.message; $("error").classList.remove("hidden"); return; }

    $("answer").innerHTML = DOMPurify.sanitize(marked.parse(d.result));
    $("answer").querySelectorAll("a").forEach(a => { a.target="_blank"; a.rel="noopener noreferrer"; });

    const box = $("sources"); box.replaceChildren();
    (d.sources||[]).forEach((s,i)=>{
      if(!/^https?:\\/\\//.test(s.url)) return;
      const a = document.createElement("a");
      a.href = s.url; a.target="_blank"; a.rel="noopener noreferrer";
      a.className = "block text-indigo-400 hover:underline truncate";
      a.textContent = (i+1) + ". " + (s.title || s.url);
      box.appendChild(a);
    });
    $("srcWrap").classList.toggle("hidden", !box.children.length);
    $("via").textContent = "Yöntem: " + d.via;
    $("result").classList.remove("hidden");
  }catch(e){
    $("error").textContent = "Bağlantı hatası: " + e.message; $("error").classList.remove("hidden");
  }finally{
    $("loading").classList.add("hidden"); $("btn").disabled = false;
  }
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    print("\n[+] YK-Intel -> http://127.0.0.1:5000\n")
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
