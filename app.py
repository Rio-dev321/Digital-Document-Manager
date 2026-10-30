import streamlit as st
import json, uuid
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="DocuSpace | Digital Document Manager", page_icon="📁", layout="wide")
ROOT=Path(__file__).parent
STORE=ROOT/"document_storage"
FILES=STORE/"files"
META=STORE/"documents.json"
FILES.mkdir(parents=True, exist_ok=True)

def load():
    try: return json.loads(META.read_text(encoding="utf-8")) if META.exists() else []
    except Exception: return []
def save():
    STORE.mkdir(exist_ok=True)
    tmp=META.with_suffix(".tmp")
    tmp.write_text(json.dumps(st.session_state.docs,ensure_ascii=False,indent=2),encoding="utf-8")
    tmp.replace(META)
def sizefmt(n):
    return f"{n/1024:.1f} KB" if n<1024**2 else f"{n/1024**2:.2f} MB"
def icon(name):
    return {".pdf":"📕",".doc":"📘",".docx":"📘",".xls":"📗",".xlsx":"📗",".ppt":"📙",".pptx":"📙",".txt":"📄",".csv":"📊",".png":"🖼️",".jpg":"🖼️",".jpeg":"🖼️"}.get(Path(name).suffix.lower(),"📎")
def delete_doc(doc_id):
    kept=[]
    for d in st.session_state.docs:
        if d["id"]==doc_id:
            p=FILES/d["stored"]
            if p.exists(): p.unlink()
        else: kept.append(d)
    st.session_state.docs=kept
    save()

if "docs" not in st.session_state: st.session_state.docs=load()
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:linear-gradient(135deg,#f3f7fd,#edf4fc,#f9fbff);color:#183153}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102b52,#174c7d)}
[data-testid="stSidebar"] *{color:white!important}
.hero{background:linear-gradient(115deg,#102b52,#1763a6 72%,#59a7e6);color:white;padding:28px 30px;border-radius:21px;margin-bottom:20px;box-shadow:0 12px 30px #174c8229;animation:up .5s ease-out}
.hero h1{color:white;font-size:30px;margin:0;font-weight:800}.hero p{color:#e4f1ff;margin:7px 0 0}
@keyframes up{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}
.panel{background:white;border:1px solid #e1eaf5;border-radius:16px;padding:16px 18px;box-shadow:0 5px 18px #143a640e;animation:up .35s ease-out}
.section{color:#12365f;font-size:21px;font-weight:800;margin:16px 0 10px}
.metric-label{color:#6b7f99;font-size:13px}.metric-value{color:#12365f;font-size:26px;font-weight:800;margin-top:4px}
.pill{display:inline-block;background:#eaf3ff;color:#175b9a;border:1px solid #d3e6fb;padding:5px 10px;border-radius:18px;font-size:12px;font-weight:700;margin:2px}
div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button{border-radius:10px;border:0;background:#1763a6;color:white;font-weight:700;transition:all .18s ease}
div[data-testid="stButton"] button:hover,div[data-testid="stFormSubmitButton"] button:hover{background:#104879;transform:translateY(-1px);box-shadow:0 5px 12px #1763a633}
div[data-testid="stDownloadButton"] button{background:#e5f1ff;color:#15568f;border:1px solid #c9e0f8;border-radius:10px;font-weight:700}
</style>""",unsafe_allow_html=True)

st.sidebar.markdown("# 📁 DocuSpace")
st.sidebar.caption("Digital Document Manager")
page=st.sidebar.radio("Navigation",["🏠 Dashboard","⬆️ Upload Documents","📚 All Documents","🔎 Search Documents","🗂️ Categories"])
st.sidebar.markdown("---")
st.sidebar.caption("Files project ke document_storage folder mein save hoti hain.")
st.markdown('<div class="hero"><h1>📁 Digital Document Manager</h1><p>Upload · Organize · Search · Add Notes · Download your documents</p></div>',unsafe_allow_html=True)

docs=st.session_state.docs
pdfs=sum(Path(d["original"]).suffix.lower()==".pdf" for d in docs)
used=sum(d["size"] for d in docs)
cats=sorted(set(d["category"] for d in docs))
def show_doc(d,prefix=""):
    with st.expander(f"{icon(d['original'])} {d['name']} · {d['category']}"):
        a,b=st.columns([2,1])
        with a:
            st.write("**Original file:**",d["original"])
            st.write("**Category:**",d["category"])
            st.write("**Uploaded:**",d["uploaded"])
            st.write("**Size:**",sizefmt(d["size"]))
            st.write("**Notes:**",d.get("notes") or "No notes")
        with b:
            path=FILES/d["stored"]
            if path.exists():
                st.download_button("⬇️ Download",path.read_bytes(),d["original"],key=f"{prefix}dl_{d['id']}",use_container_width=True)
            else: st.error("File missing")
            if st.button("🗑️ Delete",key=f"{prefix}del_{d['id']}",use_container_width=True):
                delete_doc(d["id"]); st.rerun()
        with st.form(f"{prefix}edit_{d['id']}"):
            choices=["Personal","Education","Work","Bills & Receipts","Health","Certificates","Other"]
            cat=st.selectbox("Category update",choices,index=choices.index(d["category"]) if d["category"] in choices else 6)
            note=st.text_area("Notes",value=d.get("notes",""))
            if st.form_submit_button("Save changes"):
                for item in st.session_state.docs:
                    if item["id"]==d["id"]: item["category"]=cat; item["notes"]=note.strip()
                save(); st.success("Details update ho gayi!"); st.rerun()

if page=="🏠 Dashboard":
    st.markdown('<div class="section">✨ Document Overview</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for col,(label,value,emoji) in zip(cols,[("Total Documents",len(docs),"📁"),("PDF Files",pdfs,"📕"),("Categories",len(cats),"🗂️"),("Storage Used",sizefmt(used),"💾")]):
        with col: st.markdown(f'<div class="panel"><div class="metric-label">{emoji} {label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
    l,r=st.columns([1.2,1])
    with l:
        st.markdown('<div class="section">🕘 Recently Added</div>',unsafe_allow_html=True)
        for d in sorted(docs,key=lambda x:x["uploaded"],reverse=True)[:6]:
            st.markdown(f'<div class="panel" style="margin-bottom:9px"><b>{icon(d["original"])} {d["name"]}</b><br><span style="color:#71839b;font-size:12px">{d["category"]} · {sizefmt(d["size"])} · {d["uploaded"]}</span></div>',unsafe_allow_html=True)
        if not docs: st.info("Abhi koi document nahi. Upload Documents se shuru karein.")
    with r:
        st.markdown('<div class="section">🗂️ Category Summary</div>',unsafe_allow_html=True)
        if docs:
            count={c:sum(x["category"]==c for x in docs) for c in cats}
            st.bar_chart(count,color="#2878c8")
        else: st.info("Category chart upload ke baad show hoga.")
        st.markdown('<div class="panel"><b>💡 Smart Tip</b><br>Files ko meaningful naam dein aur notes add karein, taake baad mein dhoondhna asaan ho.</div>',unsafe_allow_html=True)

elif page=="⬆️ Upload Documents":
    st.markdown('<div class="section">⬆️ Upload New Documents</div>',unsafe_allow_html=True)
    st.write("PDF, Word, Excel, PowerPoint, TXT, CSV aur image files upload karein.")
    uploads=st.file_uploader("Files select karein",type=["pdf","doc","docx","xls","xlsx","ppt","pptx","txt","csv","png","jpg","jpeg"],accept_multiple_files=True)
    with st.form("upload_form"):
        cat=st.selectbox("Category",["Personal","Education","Work","Bills & Receipts","Health","Certificates","Other"])
        notes=st.text_area("Notes (optional)",placeholder="Document ki important details...")
        submit=st.form_submit_button("💾 Save Documents")
        if submit:
            if not uploads: st.warning("Pehle file select karein.")
            else:
                for up in uploads:
                    original=Path(up.name).name
                    uid=str(uuid.uuid4())
                    stored=uid+Path(original).suffix.lower()
                    content=up.getvalue()
                    (FILES/stored).write_bytes(content)
                    st.session_state.docs.append({"id":uid,"name":Path(original).stem,"original":original,"stored":stored,"category":cat,"notes":notes.strip(),"size":len(content),"uploaded":datetime.now().strftime("%Y-%m-%d %H:%M")})
                save(); st.success(f"{len(uploads)} file(s) save ho gayi!"); st.rerun()
    st.markdown('<div class="panel"><b>Supported formats</b><br><span class="pill">PDF</span><span class="pill">DOC/DOCX</span><span class="pill">XLS/XLSX</span><span class="pill">PPT/PPTX</span><span class="pill">TXT</span><span class="pill">CSV</span><span class="pill">PNG/JPG</span></div>',unsafe_allow_html=True)

else:
    title={"📚 All Documents":"📚 All Documents","🔎 Search Documents":"🔎 Find a Document","🗂️ Categories":"🗂️ Browse Categories"}[page]
    st.markdown(f'<div class="section">{title}</div>',unsafe_allow_html=True)
    q=st.text_input("Search name, original filename, category ya notes",placeholder="Document search karein...")
    c1,c2=st.columns(2)
    with c1: cat=st.selectbox("Category",["All categories"]+cats)
    with c2: typ=st.selectbox("File type",["All types","PDF only","Other files"])
    result=[]
    for d in sorted(docs,key=lambda x:x["uploaded"],reverse=True):
        hay=" ".join([d["name"],d["original"],d["category"],d.get("notes","")]).lower()
        if q.strip().lower() not in hay: continue
        if cat!="All categories" and d["category"]!=cat: continue
        ispdf=Path(d["original"]).suffix.lower()==".pdf"
        if typ=="PDF only" and not ispdf: continue
        if typ=="Other files" and ispdf: continue
        result.append(d)
    st.caption(f"{len(result)} document(s) found")
    if page=="🗂️ Categories" and cat=="All categories":
        if cats:
            tabs=st.tabs(cats)
            for tab,category in zip(tabs,cats):
                with tab:
                    for d in [x for x in result if x["category"]==category]: show_doc(d,"cat")
        else: st.info("Upload documents to create categories.")
    elif result:
        for d in result: show_doc(d)
    else: st.info("Koi matching document nahi mila. Search ya filters change karein.")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#71839b;font-size:12px'>DocuSpace · Digital Document Manager · Python + Streamlit</p>",unsafe_allow_html=True)
