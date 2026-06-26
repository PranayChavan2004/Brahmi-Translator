import cv2
import numpy as np
from keras.models import load_model

# Load the trained model
model = load_model(r"F:\final_bramhi\OCR\model.h5")

# Mapping from index to Brahmi class
brahmi_mapping = {
    0: "a(3)", 1: "a(4)", 2: "a(5)", 3: "aaa", 4: "ba", 5: "ba(2)", 6: "baa", 7: "be",
    8: "bha", 9: "bhaa", 10: "bhe", 11: "bhi", 12: "bhii", 13: "bho", 14: "bhu", 15: "bhuu",
    16: "bi", 17: "bii", 18: "bo", 19: "bo(2)", 20: "bu", 21: "buu", 22: "ca", 23: "caa",
    24: "ce", 25: "cha", 26: "chaa", 27: "che", 28: "chi", 29: "chii", 30: "cho", 31: "chu",
    32: "chuu", 33: "ci", 34: "cii", 35: "co", 36: "cu", 37: "cuu", 38: "da(2)", 39: "daa",
    40: "daa(2)", 41: "daaa", 42: "daaaa", 43: "dae", 44: "dai", 45: "daii", 46: "dao", 47: "dau",
    48: "dauu", 49: "de", 50: "dha", 51: "dhaa", 52: "dhaaa", 53: "dhaaaa", 54: "dhae", 55: "dhai",
    56: "dhaii", 57: "dhao", 58: "dhau", 59: "dhauu", 60: "dhi", 61: "dhii", 62: "dho", 63: "dhu",
    64: "dhue", 65: "dhuu", 66: "di", 67: "dii", 68: "do", 69: "du", 70: "duu", 71: "e", 72: "ee",
    73: "ga", 74: "gaa", 75: "ge", 76: "gha", 77: "ghaa", 78: "ghe", 79: "ghi", 80: "ghii", 81: "gho",
    82: "ghu", 83: "ghuu", 84: "gi", 85: "gii", 86: "go", 87: "gu", 88: "guu", 89: "ha", 90: "haa",
    91: "he", 92: "hi", 93: "hii", 94: "ho", 95: "hu", 96: "huu", 97: "i", 98: "ja", 99: "ja(2)",
    100: "ja(3)", 101: "ja(4)", 102: "jaa", 103: "je", 104: "jha", 105: "jhaa", 106: "jhe", 107: "jhi",
    108: "jhii", 109: "jho", 110: "jhu", 111: "jhuu", 112: "ji", 113: "jii", 114: "jo", 115: "ju",
    116: "juu", 117: "ka", 118: "kaa", 119: "ke", 120: "kha", 121: "kha(2)", 122: "khaa", 123: "khaa(2)",
    124: "khe", 125: "khe(2)", 126: "khi", 127: "khii", 128: "khii(2)", 129: "kho", 130: "kho(2)",
    131: "khu", 132: "khu(2)", 133: "khuu", 134: "khuu(2)", 135: "ki", 136: "kii", 137: "ko",
    138: "ku", 139: "kuu", 140: "la", 141: "la(2)", 142: "la(3)", 143: "laa", 144: "le",
    145: "li", 146: "lii", 147: "lo", 148: "lu", 149: "luu", 150: "ma", 151: "ma(2)", 152: "maa",
    153: "me", 154: "mi", 155: "mii", 156: "mo", 157: "mu", 158: "muu", 159: "na", 160: "na(2)",
    161: "naa", 162: "ne", 163: "ni", 164: "nii", 165: "nna", 166: "nnaa", 167: "nne", 168: "nni",
    169: "nnii", 170: "nno", 171: "nno(2)", 172: "nnu", 173: "nnuu", 174: "no", 175: "nu",
    176: "nuu", 177: "nya", 178: "nya(2)", 179: "o", 180: "o(2)", 181: "pa", 182: "paa",
    183: "pe", 184: "pha", 185: "pha(2)", 186: "phaa", 187: "phe", 188: "phi", 189: "phii",
    190: "pho", 191: "phu", 192: "phuu", 193: "pi", 194: "pii", 195: "po", 196: "pu", 197: "puu",
    198: "ra", 199: "ra(2)", 200: "ra(3)", 201: "raa", 202: "re", 203: "ri", 204: "rii", 205: "ro",
    206: "ru", 207: "ruu", 208: "sa", 209: "sa(2)", 210: "saa", 211: "se", 212: "sha", 213: "shaa",
    214: "shaaa", 215: "shaaaa", 216: "shae", 217: "shai", 218: "shaii", 219: "shao", 220: "shau",
    221: "she", 222: "shi", 223: "shii", 224: "sho", 225: "shu", 226: "shuu", 227: "si", 228: "sii",
    229: "so", 230: "su", 231: "suu", 232: "ta", 233: "taa", 234: "taaa", 235: "taaaa", 236: "tae",
    237: "tai", 238: "taii", 239: "tao", 240: "tau", 241: "tauu", 242: "te", 243: "tha", 244: "tha(2)",
    245: "thaa", 246: "thaaa", 247: "thaaaa", 248: "thaai", 249: "thae", 250: "thai", 251: "thaii",
    252: "thao", 253: "thau", 254: "thauu", 255: "the", 256: "the(2)", 257: "thi", 258: "thii",
    259: "tho", 260: "thu", 261: "thuu", 262: "tii", 263: "to", 264: "tu", 265: "tuu"
}

# Function to recognize Brahmi script from image
def recognize_brahmi(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (32, 32)) / 255.0
    img = img.reshape(1, 32, 32, 1)
    pred = model.predict(img)
    predicted_index = np.argmax(pred)
    return brahmi_mapping.get(predicted_index, "Unknown")

print(recognize_brahmi("5.png"))
