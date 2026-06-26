# from flask import Flask, render_template, request
# import os
# import base64
# from final import run_ocr

# app = Flask(__name__)

# UPLOAD_FOLDER = "static/uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ---------------- Devanagari → Brahmi Mapping ----------------


# dev_to_brahmi = {
#     # ---------------- VOWELS ----------------

#     "अ": "𑀅", "आ": "𑀆", "इ": "𑀇", "ई": "𑀈",
#     "उ": "𑀉", "ऊ": "𑀊", "ऋ": "𑀋",
#     "ए": "𑀏", "ऐ": "𑀐",
#     "ओ": "𑀑", "औ": "𑀒",

#     # ---------------- CONSONANTS ----------------

#     "क": "𑀓", "ख": "𑀔", "ग": "𑀕", "घ": "𑀖", "ङ": "𑀗",
#     "च": "𑀘", "छ": "𑀙", "ज": "𑀚", "झ": "𑀛", "ञ": "𑀜",
#     "ट": "𑀝", "ठ": "𑀞", "ड": "𑀟", "ढ": "𑀠", "ण": "𑀡",
#     "त": "𑀢", "थ": "𑀣", "द": "𑀤", "ध": "𑀥", "न": "𑀦",
#     "प": "𑀧", "फ": "𑀨", "ब": "𑀩", "भ": "𑀪", "म": "𑀫",
#     "य": "𑀬", "र": "𑀭", "ल": "𑀮", "व": "𑀯",
#     "श": "𑀰", "ष": "𑀱", "स": "𑀲", "ह": "𑀳",

#     # ---------------- MATRAS ----------------

#     "ा": "𑀸",
#     "ि": "𑀺",
#     "ी": "𑀻",
#     "ु": "𑀼",
#     "ू": "𑀽",
#     "ृ": "𑀾",
#     "े": "𑀿",
#     "ै": "𑁀",
#     "ो": "𑁁",
#     "ौ": "𑁂",

#     # ---------------- SIGNS ----------------

#     "ं": "𑀁",   # Anusvara
#     "ः": "𑀂",   # Visarga
#     "ँ": "𑀀",   # Chandrabindu
#     "्": "𑁆",   # Halant / Virama

#     # ---------------- NUMBERS ----------------

#     "०": "𑁦", "१": "𑁧", "२": "𑁨", "३": "𑁩", "४": "𑁪",
#     "५": "𑁫", "६": "𑁬", "७": "𑁭", "८": "𑁮", "९": "𑁯",

#     # ---------------- PUNCTUATION ----------------

#     "।": "𑁇",
#     "॥": "𑁈"
# }


# brahmi_to_dev = {v:k for k,v in dev_to_brahmi.items()}

# # ---------------- ROUTE ----------------

# @app.route("/", methods=["GET","POST"])
# def index():

#     dev_input=""
#     brahmi_input=""
#     dev_output=""
#     brahmi_output=""
#     ocr_output=""

#     if request.method=="POST":

#         # Devnagari → Brahmi
#         if "dev_text" in request.form:
#             dev_input=request.form["dev_text"]
#             brahmi_output="".join(dev_to_brahmi.get(ch,ch) for ch in dev_input)

#         # Brahmi → Devnagari
#         if "brahmi_text" in request.form:
#             brahmi_input=request.form["brahmi_text"]
#             dev_output="".join(brahmi_to_dev.get(ch,ch) for ch in brahmi_input)

#         # Image Upload OCR
#         if "image_file" in request.files:

#             file=request.files["image_file"]

#             if file.filename!="":

#                 path=os.path.join(UPLOAD_FOLDER,file.filename)
#                 file.save(path)

#                 predictions=run_ocr(path)

#                 ocr_output=" ".join(predictions)

#         # Camera Image OCR
#         if "camera_image" in request.form:

#             img_data=request.form["camera_image"]

#             header,encoded=img_data.split(",",1)

#             image_bytes=base64.b64decode(encoded)

#             path=os.path.join(UPLOAD_FOLDER,"camera.png")

#             with open(path,"wb") as f:
#                 f.write(image_bytes)

#             predictions=run_ocr(path)

#             ocr_output=" ".join(predictions)

#     return render_template(
#         "index.html",
#         dev_input=dev_input,
#         brahmi_input=brahmi_input,
#         dev_output=dev_output,
#         brahmi_output=brahmi_output,
#         ocr_output=ocr_output
#     )

# if __name__=="__main__":
#     app.run(debug=True)






# from flask import Flask, render_template, request
# import os, base64
# from final import run_ocr

# app = Flask(__name__)
# UPLOAD_FOLDER = "static/uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ── Devanagari ↔ Brahmi Unicode ─────────────────────────────────────────────
# dev_to_brahmi = {
#     "अ":"𑀅","आ":"𑀆","इ":"𑀇","ई":"𑀈","उ":"𑀉","ऊ":"𑀊","ऋ":"𑀋",
#     "ए":"𑀏","ऐ":"𑀐","ओ":"𑀑","औ":"𑀒",
#     "क":"𑀓","ख":"𑀔","ग":"𑀕","घ":"𑀖","ङ":"𑀗",
#     "च":"𑀘","छ":"𑀙","ज":"𑀚","झ":"𑀛","ञ":"𑀜",
#     "ट":"𑀝","ठ":"𑀞","ड":"𑀟","ढ":"𑀠","ण":"𑀡",
#     "त":"𑀢","थ":"𑀣","द":"𑀤","ध":"𑀥","न":"𑀦",
#     "प":"𑀧","फ":"𑀨","ब":"𑀩","भ":"𑀪","म":"𑀫",
#     "य":"𑀬","र":"𑀭","ल":"𑀮","व":"𑀯",
#     "श":"𑀰","ष":"𑀱","स":"𑀲","ह":"𑀳",
#     "ा":"𑀸","ि":"𑀺","ी":"𑀻","ु":"𑀼","ू":"𑀽",
#     "ृ":"𑀾","े":"𑀿","ै":"𑁀","ो":"𑁁","ौ":"𑁂",
#     "ं":"𑀁","ः":"𑀂","ँ":"𑀀","्":"𑁆",
#     "०":"𑁦","१":"𑁧","२":"𑁨","३":"𑁩","४":"𑁪",
#     "५":"𑁫","६":"𑁬","७":"𑁭","८":"𑁮","९":"𑁯",
#     "।":"𑁇","॥":"𑁈",
# }
# brahmi_to_dev = {v: k for k, v in dev_to_brahmi.items()}

# # ── Brahmi label → Devanagari character ─────────────────────────────────────
# LABEL_TO_DEV = {
#     "a":"अ","aaa":"आ","i":"इ","ii":"ई","e":"ए","ee":"ऐ","o":"ओ",
#     "ka":"क","kaa":"का","ki":"कि","kii":"की","ku":"कु","kuu":"कू","ke":"के","ko":"को",
#     "kha":"ख","khaa":"खा","khi":"खि","khii":"खी","khu":"खु","khuu":"खू","khe":"खे","kho":"खो",
#     "ga":"ग","gaa":"गा","gi":"गि","gii":"गी","gu":"गु","guu":"गू","ge":"गे","go":"गो",
#     "gha":"घ","ghaa":"घा","ghi":"घि","ghii":"घी","ghu":"घु","ghuu":"घू","ghe":"घे","gho":"घो",
#     "ca":"च","caa":"चा","ci":"चि","cii":"ची","cu":"चु","cuu":"चू","ce":"चे","co":"चो",
#     "cha":"छ","chaa":"छा","chi":"छि","chii":"छी","chu":"छु","chuu":"छू","che":"छे","cho":"छो",
#     "ja":"ज","jaa":"जा","ji":"जि","jii":"जी","ju":"जु","juu":"जू","je":"जे","jo":"जो",
#     "jha":"झ","jhaa":"झा","jhi":"झि","jhii":"झी","jhu":"झु","jhuu":"झू","jhe":"झे","jho":"झो",
#     "nya":"ञ",
#     "nna":"ण","nnaa":"णा","nni":"णि","nnii":"णी","nnu":"णु","nnuu":"णू","nne":"णे","nno":"णो",
#     "ta":"त","taa":"ता","te":"ते","tii":"ती","to":"तो","tu":"तु","tuu":"तू",
#     "tha":"थ","thaa":"था","the":"थे","thi":"थि","thii":"थी","tho":"थो","thu":"थु","thuu":"थू",
#     "da":"द","daa":"दा","de":"दे","di":"दि","dii":"दी","do":"दो","du":"दु","duu":"दू",
#     "dha":"ध","dhaa":"धा","dhi":"धि","dhii":"धी","dho":"धो","dhu":"धु","dhuu":"धू",
#     "na":"न","naa":"ना","ne":"ने","ni":"नि","nii":"नी","no":"नो","nu":"नु","nuu":"नू",
#     "pa":"प","paa":"पा","pe":"पे","pi":"पि","pii":"पी","po":"पो","pu":"पु","puu":"पू",
#     "pha":"फ","phaa":"फा","phe":"फे","phi":"फि","phii":"फी","pho":"फो","phu":"फु","phuu":"फू",
#     "ba":"ब","baa":"बा","be":"बे","bi":"बि","bii":"बी","bo":"बो","bu":"बु","buu":"बू",
#     "bha":"भ","bhaa":"भा","bhe":"भे","bhi":"भि","bhii":"भी","bho":"भो","bhu":"भु","bhuu":"भू",
#     "ma":"म","maa":"मा","me":"मे","mi":"मि","mii":"मी","mo":"मो","mu":"मु","muu":"मू",
#     "ya":"य","yaa":"या","ye":"ये","yi":"यि","yii":"यी","yo":"यो","yu":"यु","yuu":"यू",
#     "ra":"र","raa":"रा","re":"रे","ri":"रि","rii":"री","ro":"रो","ru":"रु","ruu":"रू",
#     "la":"ल","laa":"ला","le":"ले","li":"लि","lii":"ली","lo":"लो","lu":"लु","luu":"लू",
#     "va":"व","vaa":"वा","vi":"वि","vii":"वी","vu":"वु","vuu":"वू",
#     "sha":"श","shaa":"शा","she":"शे","shi":"शि","shii":"शी","sho":"शो","shu":"शु","shuu":"शू",
#     "sa":"स","saa":"सा","se":"से","si":"सि","sii":"सी","so":"सो","su":"सु","suu":"सू",
#     "ha":"ह","haa":"हा","he":"हे","hi":"हि","hii":"ही","ho":"हो","hu":"हु","huu":"हू",
# }

# def label_to_dev(label):
#     label = label.strip()
#     if label in LABEL_TO_DEV:
#         return LABEL_TO_DEV[label]
#     # strip variant suffix: "nya(2)" → "nya"
#     base = label.split("(")[0].strip()
#     return LABEL_TO_DEV.get(base, f"[{label}]")

# def labels_to_devanagari(labels):
#     return "".join(label_to_dev(l) for l in labels)

# # ── Routes ───────────────────────────────────────────────────────────────────
# @app.route("/", methods=["GET", "POST"])
# def index():
#     dev_input = brahmi_input = dev_output = brahmi_output = ""
#     ocr_labels = []
#     ocr_output = devanagari_output = ""

#     if request.method == "POST":

#         # Devanagari → Brahmi Unicode
#         if "dev_text" in request.form:
#             dev_input     = request.form["dev_text"]
#             brahmi_output = "".join(dev_to_brahmi.get(ch, ch) for ch in dev_input)

#         # Brahmi Unicode → Devanagari
#         if "brahmi_text" in request.form:
#             brahmi_input = request.form["brahmi_text"]
#             dev_output   = "".join(brahmi_to_dev.get(ch, ch) for ch in brahmi_input)

#         # Image upload OCR
#         if "image_file" in request.files:
#             file = request.files["image_file"]
#             if file.filename:
#                 path = os.path.join(UPLOAD_FOLDER, file.filename)
#                 file.save(path)
#                 ocr_labels        = run_ocr(path)
#                 ocr_output        = " ".join(ocr_labels)
#                 devanagari_output = labels_to_devanagari(ocr_labels)

#         # Camera OCR
#         if "camera_image" in request.form:
#             data           = request.form["camera_image"]
#             _, encoded     = data.split(",", 1)
#             path           = os.path.join(UPLOAD_FOLDER, "camera.png")
#             with open(path, "wb") as f:
#                 f.write(base64.b64decode(encoded))
#             ocr_labels        = run_ocr(path)
#             ocr_output        = " ".join(ocr_labels)
#             devanagari_output = labels_to_devanagari(ocr_labels)

#     return render_template("index.html",
#         dev_input=dev_input, brahmi_input=brahmi_input,
#         dev_output=dev_output, brahmi_output=brahmi_output,
#         ocr_labels=ocr_labels, ocr_output=ocr_output,
#         devanagari_output=devanagari_output)

# if __name__ == "__main__":
#     app.run(debug=True)










from flask import Flask, render_template, request
import os, base64
from final import run_ocr

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Devanagari -> Brahmi Unicode ─────────────────────────────────────────────
dev_to_brahmi = {
    "अ":"𑀅","आ":"𑀆","इ":"𑀇","ई":"𑀈","उ":"𑀉","ऊ":"𑀊","ऋ":"𑀋",
    "ए":"𑀏","ऐ":"𑀐","ओ":"𑀑","औ":"𑀒",
    "क":"𑀓","ख":"𑀔","ग":"𑀕","घ":"𑀖","ङ":"𑀗",
    "च":"𑀘","छ":"𑀙","ज":"𑀚","झ":"𑀛","ञ":"𑀜",
    "ट":"𑀝","ठ":"𑀞","ड":"𑀟","ढ":"𑀠","ण":"𑀡",
    "त":"𑀢","थ":"𑀣","द":"𑀤","ध":"𑀥","न":"𑀦",
    "प":"𑀧","फ":"𑀨","ब":"𑀩","भ":"𑀪","म":"𑀫",
    "य":"𑀬","र":"𑀭","ल":"𑀮","व":"𑀯",
    "श":"𑀰","ष":"𑀱","स":"𑀲","ह":"𑀳",
    "ा":"𑀸","ि":"𑀺","ी":"𑀻","ु":"𑀼","ू":"𑀽",
    "ृ":"𑀾","े":"𑀿","ै":"𑁀","ो":"𑁁","ौ":"𑁂",
    "ं":"𑀁","ः":"𑀂","ँ":"𑀀","्":"𑁆",
    "०":"𑁦","१":"𑁧","२":"𑁨","३":"𑁩","४":"𑁪",
    "५":"𑁫","६":"𑁬","७":"𑁭","८":"𑁮","९":"𑁯",
    "।":"𑁇","॥":"𑁈",
}
brahmi_to_dev = {v: k for k, v in dev_to_brahmi.items()}

# ── Brahmi label -> Devanagari (covers all 308 classes from retrained model) ─
LABEL_TO_DEV = {
    # ── Vowels ──────────────────────────────────────────────────────────────
    "a":"अ","aa":"आ","aaa":"आ","i":"इ","ii":"ई","u":"उ","uu":"ऊ",
    "e":"ए","ee":"ऐ","o":"ओ","oo":"ओ","au":"औ","ai":"ऐ",
    "ah":"अः","an":"अं","am":"अं",

    # ── Ka group ─────────────────────────────────────────────────────────────
    "ka":"क","kaa":"का","ki":"कि","kii":"की","ku":"कु","kuu":"कू",
    "ke":"के","kee":"के","ko":"को","koo":"को","kai":"कै","kau":"कौ",
    "kan":"कं","kah":"कः",

    "kha":"ख","khaa":"खा","khi":"खि","khii":"खी","khu":"खु","khuu":"खू",
    "khe":"खे","kho":"खो","khai":"खै","khau":"खौ",

    "ga":"ग","gaa":"गा","gi":"गि","gii":"गी","gu":"गु","guu":"गू",
    "ge":"गे","go":"गो","gai":"गै","gau":"गौ",

    "gha":"घ","ghaa":"घा","ghi":"घि","ghii":"घी","ghu":"घु","ghuu":"घू",
    "ghe":"घे","gho":"घो",

    "nga":"ङ",

    # ── Ca group ─────────────────────────────────────────────────────────────
    "ca":"च","caa":"चा","ci":"चि","cii":"ची","cu":"चु","cuu":"चू",
    "ce":"चे","co":"चो",

    "cha":"छ","chaa":"छा","chi":"छि","chii":"छी","chu":"छु","chuu":"छू",
    "che":"छे","cho":"छो","chha":"छ","chhaa":"छा",

    "ja":"ज","jaa":"जा","ji":"जि","jii":"जी","ju":"जु","juu":"जू",
    "je":"जे","jo":"जो","jai":"जै","jau":"जौ",

    "jha":"झ","jhaa":"झा","jhi":"झि","jhii":"झी","jhu":"झु","jhuu":"झू",
    "jhe":"झे","jho":"झो",

    "nya":"ञ","nyaa":"ञा",

    # ── Ta group (retroflex) ──────────────────────────────────────────────────
    "tta":"ट","ttaa":"टा","tti":"टि","ttii":"टी","ttu":"टु","ttuu":"टू",
    "tte":"टे","tto":"टो",

    "ttha":"ठ","tthaa":"ठा",

    "dda":"ड","ddaa":"डा","ddi":"डि","ddii":"डी","ddu":"डु","dduu":"डू",
    "dde":"डे","ddo":"डो",

    "ddha":"ढ","ddhaa":"ढा",

    "nna":"ण","nnaa":"णा","nni":"णि","nnii":"णी","nnu":"णु","nnuu":"णू",
    "nne":"णे","nno":"णो",

    # ── Ta group (dental) ─────────────────────────────────────────────────────
    "ta":"त","taa":"ता","ti":"ति","tii":"ती","tu":"तु","tuu":"तू",
    "te":"ते","to":"तो","tai":"तै","tau":"तौ","tan":"तं","tah":"तः",
    "ta2":"त","taa2":"ता",

    "tha":"थ","thaa":"था","thi":"थि","thii":"थी","thu":"थु","thuu":"थू",
    "the":"थे","tho":"थो","thai":"थै","thau":"थौ",
    "thaa2":"था","thaaa":"था","thaaaa":"था",
    "thae":"थे","thaai":"थी","thaii":"थी",
    "thao":"थो","thau":"थौ","thauu":"थू",

    "da":"द","daa":"दा","di":"दि","dii":"दी","du":"दु","duu":"दू",
    "de":"दे","do":"दो","dai":"दै","dau":"दौ",
    "da2":"द","daa2":"दा","daaa":"दा","daaaa":"दा",
    "dae":"दे","daee":"दे","dai":"दै","daii":"दै",
    "dao":"दो","dau":"दौ","dauu":"दू",

    "dha":"ध","dhaa":"धा","dhi":"धि","dhii":"धी","dhu":"धु","dhuu":"धू",
    "dhe":"धे","dho":"धो",
    "dhaaa":"धा","dhaaaa":"धा","dhae":"धे","dhai":"धै","dhaii":"धै",
    "dhao":"धो","dhau":"धौ","dhauu":"धू","dhue":"धे",

    "na":"न","naa":"ना","ni":"नि","nii":"नी","nu":"नु","nuu":"नू",
    "ne":"ने","no":"नो","nai":"नै","nau":"नौ",
    "na2":"न","naa2":"ना",

    # ── Pa group ─────────────────────────────────────────────────────────────
    "pa":"प","paa":"पा","pi":"पि","pii":"पी","pu":"पु","puu":"पू",
    "pe":"पे","po":"पो","pai":"पै","pau":"पौ",

    "pha":"फ","phaa":"फा","phi":"फि","phii":"फी","phu":"फु","phuu":"फू",
    "phe":"फे","pho":"फो",
    "pha2":"फ","phaa2":"फा",

    "ba":"ब","baa":"बा","bi":"बि","bii":"बी","bu":"बु","buu":"बू",
    "be":"बे","bo":"बो","bai":"बै","bau":"बौ",
    "ba2":"ब","baa2":"बा",

    "bha":"भ","bhaa":"भा","bhi":"भि","bhii":"भी","bhu":"भु","bhuu":"भू",
    "bhe":"भे","bho":"भो",

    "ma":"म","maa":"मा","mi":"मि","mii":"मी","mu":"मु","muu":"मू",
    "me":"मे","mo":"मो","mai":"मै","mau":"मौ","man":"मं",
    "ma2":"म","maa2":"मा",

    # ── Ya group ─────────────────────────────────────────────────────────────
    "ya":"य","yaa":"या","yi":"यि","yii":"यी","yu":"यु","yuu":"यू",
    "ye":"ये","yo":"यो","yai":"यै","yau":"यौ",
    "ya2":"य","yaa2":"या",

    "ra":"र","raa":"रा","ri":"रि","rii":"री","ru":"रु","ruu":"रू",
    "re":"रे","ro":"रो","rai":"रै","rau":"रौ",
    "ra2":"र","ra3":"र","raa2":"रा",

    "la":"ल","laa":"ला","li":"लि","lii":"ली","lu":"लु","luu":"लू",
    "le":"ले","lo":"लो","lai":"लै","lau":"लौ",
    "la2":"ल","la3":"ल","laa2":"ला",

    "va":"व","vaa":"वा","vi":"वि","vii":"वी","vu":"वु","vuu":"वू",
    "ve":"वे","vo":"वो",
    "vhu":"व्ह","vhuu":"व्हू",
    "vu2":"वु","vuu2":"वू",

    # ── Sa group ─────────────────────────────────────────────────────────────
    "sha":"श","shaa":"शा","shi":"शि","shii":"शी","shu":"शु","shuu":"शू",
    "she":"शे","sho":"शो","shai":"शै","shau":"शौ",
    "shaaa":"शा","shaaaa":"शा","shae":"शे","shaii":"शी",
    "shao":"शो","shau":"शौ",
    "sha2":"श","shaa2":"शा",

    "ssa":"ष","ssaa":"षा","ssi":"षि","ssii":"षी","ssu":"षु","ssuu":"षू",
    "sse":"षे","sso":"षो",

    "sa":"स","saa":"सा","si":"सि","sii":"सी","su":"सु","suu":"सू",
    "se":"से","so":"सो","sai":"सै","sau":"सौ",
    "sa2":"स","saa2":"सा",

    # ── Ha ───────────────────────────────────────────────────────────────────
    "ha":"ह","haa":"हा","hi":"हि","hii":"ही","hu":"हु","huu":"हू",
    "he":"हे","ho":"हो","hai":"है","hau":"हौ",

    # ── Conjuncts / special ───────────────────────────────────────────────────
    "ksha":"क्ष","kshaa":"क्षा",
    "tra":"त्र","traa":"त्रा",
    "jna":"ज्ञ","jnaa":"ज्ञा",
    "shva":"श्व","shva2":"श्व",

    # ── Stone dataset extra labels ────────────────────────────────────────────
    "lion":"[lion]",
    "dharma_wheel":"[dharma]",
}


def label_to_dev(label):
    """Convert a Brahmi label string to Devanagari character(s)."""
    label = label.strip().lower()

    # Direct match
    if label in LABEL_TO_DEV:
        return LABEL_TO_DEV[label]

    # Strip variant suffix: "nya(2)" -> "nya", "sha(3)" -> "sha"
    base = label.split("(")[0].strip()
    if base in LABEL_TO_DEV:
        return LABEL_TO_DEV[base]

    # Strip trailing digits: "sha2" -> "sha", "da2" -> "da"
    import re
    base2 = re.sub(r'\d+$', '', base)
    if base2 in LABEL_TO_DEV:
        return LABEL_TO_DEV[base2]

    # Unknown label — show as-is in brackets
    return f"[{label}]"


def labels_to_devanagari(labels):
    """Convert list of Brahmi labels to Devanagari string."""
    return "".join(label_to_dev(l) for l in labels)


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    dev_input = brahmi_input = dev_output = brahmi_output = ""
    ocr_labels = []
    ocr_output = devanagari_output = ""

    if request.method == "POST":

        # Devanagari -> Brahmi Unicode
        if "dev_text" in request.form:
            dev_input     = request.form["dev_text"]
            brahmi_output = "".join(dev_to_brahmi.get(ch, ch) for ch in dev_input)

        # Brahmi Unicode -> Devanagari
        if "brahmi_text" in request.form:
            brahmi_input = request.form["brahmi_text"]
            dev_output   = "".join(brahmi_to_dev.get(ch, ch) for ch in brahmi_input)

        # Image upload OCR
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file.filename:
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)
                ocr_labels        = run_ocr(path)
                ocr_output        = " ".join(ocr_labels)
                devanagari_output = labels_to_devanagari(ocr_labels)

        # Camera OCR
        if "camera_image" in request.form:
            data       = request.form["camera_image"]
            _, encoded = data.split(",", 1)
            path       = os.path.join(UPLOAD_FOLDER, "camera.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(encoded))
            ocr_labels        = run_ocr(path)
            ocr_output        = " ".join(ocr_labels)
            devanagari_output = labels_to_devanagari(ocr_labels)

    return render_template("index.html",
        dev_input=dev_input, brahmi_input=brahmi_input,
        dev_output=dev_output, brahmi_output=brahmi_output,
        ocr_labels=ocr_labels, ocr_output=ocr_output,
        devanagari_output=devanagari_output)


if __name__ == "__main__":
    app.run(debug=True)

