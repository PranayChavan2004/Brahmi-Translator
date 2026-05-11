"""
test_ocr.py
-----------
Place this file in:  C:\\Users\\yashd\\final_bramhi\\
Then run:            python test_ocr.py

It will:
1. Let you pick any image file
2. Show exactly what the pipeline finds at every step
3. Print the final Brahmi labels + Devanagari output
4. Save debug images to debug_output\\ folder
"""

import cv2
import numpy as np
import os
import sys

# ── CONFIG ──────────────────────────────────────────────────────────────────
# Put the filename of your test image here (must be in same folder as this script)
IMAGE_FILE = "Screenshot_2026-03-16_105325.png"

# Gap threshold: how many pixels of horizontal space between two ink blobs
# before they are treated as SEPARATE characters.
# Start with 20. If too many chars → lower it. If chars split → raise it.
GAP_THRESHOLD = 20

# Minimum blob area to keep (filters out dust/noise pixels)
MIN_AREA = 50
# ────────────────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_output")
os.makedirs(OUT_DIR, exist_ok=True)

# Brahmi label → Devanagari
LABEL_TO_DEV = {
    "a":"अ","aaa":"आ","i":"इ","ii":"ई","e":"ए","ee":"ऐ","o":"ओ",
    "ka":"क","kaa":"का","ki":"कि","kii":"की","ku":"कु","kuu":"कू","ke":"के","ko":"को",
    "kha":"ख","khaa":"खा","khi":"खि","khii":"खी","khu":"खु","khuu":"खू","khe":"खे","kho":"खो",
    "ga":"ग","gaa":"गा","gi":"गि","gii":"गी","gu":"गु","guu":"गू","ge":"गे","go":"गो",
    "gha":"घ","ghaa":"घा","ghi":"घि","ghii":"घी","ghu":"घु","ghuu":"घू","ghe":"घे","gho":"घो",
    "ca":"च","caa":"चा","ci":"चि","cii":"ची","cu":"चु","cuu":"चू","ce":"चे","co":"चो",
    "cha":"छ","chaa":"छा","chi":"छि","chii":"छी","chu":"छु","chuu":"छू","che":"छे","cho":"छो",
    "ja":"ज","jaa":"जा","ji":"जि","jii":"जी","ju":"जु","juu":"जू","je":"जे","jo":"जो",
    "jha":"झ","jhaa":"झा","jhi":"झि","jhii":"झी","jhu":"झु","jhuu":"झू","jhe":"झे","jho":"झो",
    "nya":"ञ",
    "nna":"ण","nnaa":"णा","nni":"णि","nnii":"णी","nnu":"णु","nnuu":"णू","nne":"णे","nno":"णो",
    "ta":"त","taa":"ता","te":"ते","tii":"ती","to":"तो","tu":"तु","tuu":"तू",
    "tha":"थ","thaa":"था","the":"थे","thi":"थि","thii":"थी","tho":"थो","thu":"थु","thuu":"थू",
    "da":"द","daa":"दा","de":"दे","di":"दि","dii":"दी","do":"दो","du":"दु","duu":"दू",
    "dha":"ध","dhaa":"धा","dhi":"धि","dhii":"धी","dho":"धो","dhu":"धु","dhuu":"धू",
    "na":"न","naa":"ना","ne":"ने","ni":"नि","nii":"नी","no":"नो","nu":"नु","nuu":"नू",
    "pa":"प","paa":"पा","pe":"पे","pi":"पि","pii":"पी","po":"पो","pu":"पु","puu":"पू",
    "pha":"फ","phaa":"फा","phe":"फे","phi":"फि","phii":"फी","pho":"फो","phu":"फु","phuu":"फू",
    "ba":"ब","baa":"बा","be":"बे","bi":"बि","bii":"बी","bo":"बो","bu":"बु","buu":"बू",
    "bha":"भ","bhaa":"भा","bhe":"भे","bhi":"भि","bhii":"भी","bho":"भो","bhu":"भु","bhuu":"भू",
    "ma":"म","maa":"मा","me":"मे","mi":"मि","mii":"मी","mo":"मो","mu":"मु","muu":"मू",
    "ya":"य","yaa":"या","ye":"ये","yi":"यि","yii":"यी","yo":"यो","yu":"यु","yuu":"यू",
    "ra":"र","raa":"रा","re":"रे","ri":"रि","rii":"री","ro":"रो","ru":"रु","ruu":"रू",
    "la":"ल","laa":"ला","le":"ले","li":"लि","lii":"ली","lo":"लो","lu":"लु","luu":"लू",
    "va":"व","vaa":"वा","vi":"वि","vii":"वी","vu":"वु","vuu":"वू",
    "sha":"श","shaa":"शा","she":"शे","shi":"शि","shii":"शी","sho":"शो","shu":"शु","shuu":"शू",
    "sa":"स","saa":"सा","se":"से","si":"सि","sii":"सी","so":"सो","su":"सु","suu":"सू",
    "ha":"ह","haa":"हा","he":"हे","hi":"हि","hii":"ही","ho":"हो","hu":"हु","huu":"हू",
}

def label_to_dev(label):
    label = label.strip()
    if label in LABEL_TO_DEV:
        return LABEL_TO_DEV[label]
    base = label.split("(")[0].strip()
    return LABEL_TO_DEV.get(base, f"[{label}]")


def save_img(name, img):
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, img)


def segment_and_predict(image_path, gap_threshold=GAP_THRESHOLD, min_area=MIN_AREA):

    print("\n" + "="*55)
    print("  BRAHMI OCR - STEP BY STEP DEBUG")
    print("="*55)

    # ── STEP 1: Load ────────────────────────────────────────
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"\n  ERROR: Cannot open image: {image_path}")
        print("  Make sure the file is in the same folder as test_ocr.py")
        print(f"  Folder: {os.path.dirname(os.path.abspath(__file__))}")
        return [], ""

    save_img("1_original.png", img_bgr)
    print(f"\n[1] Image loaded OK — size: {img_bgr.shape[1]}w × {img_bgr.shape[0]}h")

    # ── STEP 2: Grayscale ────────────────────────────────────
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    save_img("2_gray.png", gray)
    print(f"[2] Grayscale — pixel range: {int(gray.min())} to {int(gray.max())}")

    # ── STEP 3: Scale up 3× ─────────────────────────────────
    scale = 3
    gray = cv2.resize(gray,
                      (gray.shape[1] * scale, gray.shape[0] * scale),
                      interpolation=cv2.INTER_CUBIC)
    save_img("3_scaled.png", gray)
    print(f"[3] Scaled ×{scale} — new size: {gray.shape[1]}w × {gray.shape[0]}h")

    # ── STEP 4: Threshold ────────────────────────────────────
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    otsu_val, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    ink = cv2.countNonZero(thresh)
    save_img("4_thresh.png", thresh)
    print(f"[4] Threshold (OTSU={otsu_val:.0f}) — ink pixels: {ink}")

    # If threshold finds nothing, try without invert
    if ink < 100:
        print("    !! Very few ink pixels found with INV threshold.")
        print("    !! Trying without invert...")
        _, thresh2 = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        ink2 = cv2.countNonZero(thresh2)
        save_img("4b_thresh_noinvert.png", thresh2)
        print(f"    Without invert: {ink2} ink pixels")
        if ink2 > ink:
            thresh = thresh2
            ink = ink2
            print("    → Using non-inverted threshold")

    # ── STEP 5: Find contours ────────────────────────────────
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"[5] Total contours found: {len(contours)}")

    # Draw ALL contours in red
    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 0, 255), 1)
    save_img("5_all_contours.png", vis)

    # ── STEP 6: Filter by area ───────────────────────────────
    raw = []
    for c in contours:
        area = cv2.contourArea(c)
        if area >= min_area:
            raw.append(cv2.boundingRect(c))
    print(f"[6] After noise filter (area≥{min_area}): {len(raw)} blobs")

    if not raw:
        print("\n  !! No blobs found after area filter.")
        print(f"  !! Try lowering MIN_AREA (currently {min_area})")
        print(f"  !! Check debug_output/4_thresh.png — is ink white?")
        return [], ""

    # Draw filtered blobs in blue
    vis2 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for (x, y, w, h) in raw:
        cv2.rectangle(vis2, (x, y), (x+w, y+h), (255, 0, 0), 2)
    save_img("6_filtered_blobs.png", vis2)

    # ── STEP 7: Merge nearby bboxes ──────────────────────────
    eff_gap = gap_threshold * scale
    raw_s   = sorted(raw, key=lambda b: b[0])
    merged  = []
    cx, cy, cw, ch = raw_s[0]

    for (x, y, w, h) in raw_s[1:]:
        gap = x - (cx + cw)
        if gap <= eff_gap:
            nx = min(cx, x);  ny = min(cy, y)
            nr = max(cx+cw, x+w);  nb = max(cy+ch, y+h)
            cx, cy, cw, ch = nx, ny, nr-nx, nb-ny
        else:
            merged.append((cx, cy, cw, ch))
            cx, cy, cw, ch = x, y, w, h
    merged.append((cx, cy, cw, ch))

    print(f"[7] After merge (gap≤{eff_gap}px): {len(merged)} character(s)")

    # Draw merged chars in green
    vis3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for i, (x, y, w, h) in enumerate(merged):
        cv2.rectangle(vis3, (x, y), (x+w, y+h), (0, 200, 0), 3)
        cv2.putText(vis3, str(i+1), (x+2, y-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 180, 0), 2)
    save_img("7_merged_chars.png", vis3)

    # ── STEP 8: Crop characters ──────────────────────────────
    pad   = 6
    H, W  = gray.shape
    crops = []
    print(f"\n[8] Character crops:")
    for i, (x, y, w, h) in enumerate(merged):
        x1 = max(0, x-pad);  y1 = max(0, y-pad)
        x2 = min(W, x+w+pad);  y2 = min(H, y+h+pad)
        crop = gray[y1:y2, x1:x2]
        crops.append(crop)
        save_img(f"8_char_{i+1}.png", crop)
        print(f"   Char {i+1}: size={crop.shape[1]}×{crop.shape[0]}")

    # ── STEP 9: Load model and predict ──────────────────────
    print(f"\n[9] Loading model...")
    try:
        import tensorflow as tf
        from tensorflow import keras
        model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "models", "MODEL", "model.h5")
        print(f"   Model path: {model_path}")
        model = keras.models.load_model(model_path)
        print(f"   Model loaded OK")
    except Exception as ex:
        print(f"   !! Could not load model: {ex}")
        print("   Skipping prediction — check debug_output images manually")
        return [], ""

    num_to_name = {
        0:'a',1:'a(3)',2:'a(4)',3:'a(5)',4:'aaa',5:'ba',6:'ba(2)',7:'baa',8:'be',
        9:'bha',10:'bhaa',11:'bhe',12:'bhi',13:'bhii',14:'bho',15:'bhu',16:'bhuu',
        17:'bi',18:'bii',19:'bo',20:'bo(2)',21:'bu',22:'buu',23:'ca',24:'caa',
        25:'ce',26:'cha',27:'chaa',28:'che',29:'chi',30:'chii',31:'cho',32:'chu',
        33:'chuu',34:'ci',35:'cii',36:'co',37:'cu',38:'cuu',39:'da(2)',40:'daa',
        41:'daa(2)',42:'daaa',43:'daaaa',44:'dae',45:'dai',46:'daii',47:'dao',
        48:'dau',49:'dauu',50:'de',51:'dha',52:'dhaa',53:'dhaaa',54:'dhaaaa',
        55:'dhae',56:'dhai',57:'dhaii',58:'dhao',59:'dhau',60:'dhauu',61:'dhi',
        62:'dhii',63:'dho',64:'dhu',65:'dhue',66:'dhuu',67:'di',68:'dii',69:'do',
        70:'du',71:'duu',72:'e',73:'ee',74:'ga',75:'gaa',76:'ge',77:'gha',
        78:'ghaa',79:'ghe',80:'ghi',81:'ghii',82:'gho',83:'ghu',84:'ghuu',85:'gi',
        86:'gii',87:'go',88:'gu',89:'guu',90:'ha',91:'haa',92:'he',93:'hi',
        94:'hii',95:'ho',96:'hu',97:'huu',98:'i',99:'ja',100:'ja(2)',101:'ja(3)',
        102:'ja(4)',103:'jaa',104:'je',105:'jha',106:'jhaa',107:'jhe',108:'jhi',
        109:'jhii',110:'jho',111:'jhu',112:'jhuu',113:'ji',114:'jii',115:'jo',
        116:'ju',117:'juu',118:'ka',119:'kaa',120:'ke',121:'kha',122:'kha(2)',
        123:'khaa',124:'khaa(2)',125:'khe',126:'khe(2)',127:'khi',128:'khii',
        129:'khii(2)',130:'kho',131:'kho(2)',132:'khu',133:'khu(2)',134:'khuu',
        135:'khuu(2)',136:'ki',137:'kii',138:'ko',139:'ku',140:'kuu',141:'la',
        142:'la(2)',143:'la(3)',144:'laa',145:'le',146:'li',147:'lii',148:'lo',
        149:'lu',150:'luu',151:'ma',152:'ma(2)',153:'maa',154:'me',155:'mi',
        156:'mii',157:'mo',158:'mu',159:'muu',160:'na',161:'na(2)',162:'naa',
        163:'ne',164:'ni',165:'nii',166:'nna',167:'nnaa',168:'nne',169:'nni',
        170:'nnii',171:'nno',172:'nno(2)',173:'nnu',174:'nnuu',175:'no',176:'nu',
        177:'nuu',178:'nya',179:'nya(2)',180:'o',181:'o(2)',182:'pa',183:'paa',
        184:'pe',185:'pha',186:'pha(2)',187:'phaa',188:'phe',189:'phi',190:'phii',
        191:'pho',192:'phu',193:'phuu',194:'pi',195:'pii',196:'po',197:'pu',
        198:'puu',199:'ra',200:'ra(2)',201:'ra(3)',202:'raa',203:'re',204:'ri',
        205:'rii',206:'ro',207:'ru',208:'ruu',209:'sa',210:'sa(2)',211:'saa',
        212:'se',213:'sha',214:'shaa',215:'shaaa',216:'shaaaa',217:'shae',
        218:'shai',219:'shaii',220:'shao',221:'shau',222:'she',223:'shi',
        224:'shii',225:'sho',226:'shu',227:'shuu',228:'si',229:'sii',230:'so',
        231:'su',232:'suu',233:'ta',234:'taa',235:'taaa',236:'taaaa',237:'tae',
        238:'tai',239:'taii',240:'tao',241:'tau',242:'tauu',243:'te',244:'tha',
        245:'tha(2)',246:'thaa',247:'thaaa',248:'thaaaa',249:'thaai',250:'thae',
        251:'thai',252:'thaii',253:'thao',254:'thau',255:'thauu',256:'the',
        257:'the(2)',258:'thi',259:'thii',260:'tho',261:'thu',262:'thuu',263:'tii',
        264:'to',265:'tu',266:'tuu',267:'va',268:'vaa',269:'vhu',270:'vhuu',
        271:'vi',272:'vii',273:'vu',274:'vu(2)',275:'vuu',276:'vuu(2)',277:'ya',
        278:'ya(2)',279:'yaa',280:'ye',281:'yi',282:'yii',283:'yo',284:'yo(2)',
        285:'yu',286:'yuu'
    }

    test_imgs = []
    for crop in crops:
        resized = cv2.resize(crop, (32, 32)) / 255.0
        test_imgs.append(np.expand_dims(resized, axis=-1))
    test_imgs = np.array(test_imgs)

    preds      = model.predict(test_imgs, verbose=0)
    labels     = []
    devanagari = []

    print(f"\n[10] Predictions:")
    for i, pred in enumerate(preds):
        conf  = float(np.max(pred))
        idx   = int(np.argmax(pred))
        label = num_to_name.get(idx, "?")
        deva  = label_to_dev(label)
        labels.append(label)
        devanagari.append(deva)
        print(f"   Char {i+1}: {label:12s} → {deva}   (confidence: {conf:.2f})")

    deva_str = "".join(devanagari)

    print(f"\n{'='*55}")
    print(f"  Brahmi labels : {' '.join(labels)}")
    print(f"  Devanagari    : {deva_str}")
    print(f"{'='*55}")
    print(f"\n  Debug images saved to: {OUT_DIR}")
    print("  Open 7_merged_chars.png to see character segmentation")
    print("  Open 8_char_1.png etc  to see individual character crops\n")

    return labels, deva_str


if __name__ == "__main__":
    # Build full path to image (same folder as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, IMAGE_FILE)

    if not os.path.exists(image_path):
        print(f"\n  ERROR: Image not found: {image_path}")
        print(f"\n  Files in {script_dir}:")
        for f in os.listdir(script_dir):
            if f.lower().endswith(('.png','.jpg','.jpeg','.bmp')):
                print(f"    {f}")
        sys.exit(1)

    segment_and_predict(image_path, gap_threshold=GAP_THRESHOLD, min_area=MIN_AREA)
