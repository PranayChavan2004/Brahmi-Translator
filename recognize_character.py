import random

# Full Character Mapping: Brahmi to Devanagari
brahmi_to_devanagari = {
    '𑀅': 'अ', '𑀧': 'क', '𑀨': 'ख', '𑀩': 'ग', '𑀪': 'घ', '𑀫': 'ङ',
    '𑀄': 'च', '𑀅': 'छ', '𑀆': 'ज', '𑀇': 'झ', '𑀈': 'ञ', '𑀕': 'ट',
    '𑀖': 'ठ', '𑀗': 'ड', '𑀘': 'ढ', '𑀙': 'ण', '𑀚': 'त', '𑀛': 'थ',
    '𑀜': 'द', '𑀝': 'ध', '𑀞': 'न', '𑀟': 'प', '𑀠': 'फ', '𑀡': 'ब',
    '𑀢': 'भ', '𑀣': 'म', '𑀤': 'य', '𑀥': 'र', '𑀦': 'ल', '𑀧': 'व',
    '𑀨': 'श', '𑀩': 'ष', '𑀪': 'स', '𑀫': 'ह', '𑀬': 'ळ', '𑀭': 'क्ष',
    '𑀮': 'ज्ञ', '𑀁': 'ि', '𑀂': 'ी', '𑀃': 'ु', '𑀄': 'ू', '𑀅': 'ृ',
    '𑀆': 'े', '𑀇': 'ै', '𑀈': 'ो', '𑀉': 'ौ', '𑀋': 'ं', '𑀌': 'ः',
    '𑀍': '।', '𑀑': 'अ', '𑀒': 'ब', '𑀓': 'क', '𑀔': 'न', '𑀕': 'म',
    '𑀖': 'ल', '𑀗': 'व', '𑀘': 'श', '𑀙': 'ष', '𑀚': 'स', '𑀛': 'ह',
    '𑀜': 'ह', '𑀝': 'ङ', '𑀟': 'च', '𑀠': 'ट', '𑀡': 'ड', '𑀢': 'प',
    '𑀣': 'फ', '𑀤': 'ब', '𑀥': 'भ', '𑀦': 'म', '𑀧': 'य', '𑀨': 'र',
    '𑀩': 'ल', '𑀪': 'व', '𑀫': 'श', '𑀬': 'ष', '𑀭': 'स', '𑀮': 'ह',
    '𑀯': 'ळ', '𑀰': 'क', '𑀱': 'ट', '𑀲': 'त', '𑀳': 'प', '𑀴': 'श',
    '𑀵': 'अ', '𑀶': 'म', '𑀷': 'व', '𑀸': 'प', '𑀹': 'म', '𑀺': 'न',
    '𑀻': 'त', '𑀼': 'व', '𑀽': 'ल', '𑀾': 'श', '𑀿': 'ह', '𑁀': 'ं',
    '𑁁': 'अ', '𑁂': 'आ', '𑁃': 'इ', '𑁄': 'ई', '𑁅': 'उ', '𑁆': 'ऊ',
    '𑁇': 'ऋ', '𑁈': 'ए', '𑁉': 'ऐ', '𑁊': 'ओ', '𑁋': 'औ', '𑁌': 'अं',
    '𑁍': 'अः', '𑁎': 'क', '𑁏': 'ख', '𑁐': 'ग', '𑁑': 'घ', '𑁒': 'ङ',
    '𑁓': 'च', '𑁔': 'छ', '𑁕': 'ज', '𑁖': 'झ', '𑁗': 'ञ', '𑁘': 'ट',
    '𑁙': 'ठ', '𑁚': 'ड', '𑁛': 'ढ', '𑁜': 'ण', '𑁝': 'त', '𑁞': 'थ',
    '𑁟': 'द', '𑁠': 'ध', '𑁡': 'न', '𑁢': 'प', '𑁣': 'फ', '𑁤': 'ब',
    '𑁥': 'भ', '𑁦': 'म', '𑁧': 'य', '𑁨': 'र', '𑁩': 'ल', '𑁪': 'व',
    '𑁫': 'श', '𑁬': 'ष', '𑁭': 'स', '𑁮': 'ह', '𑁯': 'ळ', '𑁰': 'क्ष',
    '𑁱': 'ज्ञ', '𑁲': 'ञ', '𑁳': 'आ', '𑁴': 'इ', '𑁵': 'ई', '𑁶': 'उ',
    '𑁷': 'ऊ', '𑁸': 'ऋ', '𑁹': 'ए', '𑁺': 'ऐ', '𑁻': 'ओ', '𑁼': 'औ',
    '𑁽': 'अं', '𑁾': 'अः', '𑁿': 'क', '𑂀': 'ख', '𑂁': 'ग', '𑂂': 'घ',
    '𑂃': 'ङ', '𑂄': 'च', '𑂅': 'छ', '𑂆': 'ज', '𑂇': 'झ', '𑂈': 'ञ'

}


# Full Character Mapping: Index to Brahmi Character
index_to_brahmi = {
    0: '𑀅', 1: '𑀧', 2: '𑀨', 3: '𑀩', 4: '𑀪', 5: '𑀫', 6: '𑀄', 
    7: '𑀅', 8: '𑀆', 9: '𑀇', 10: '𑀈', 11: '𑀕', 12: '𑀖', 13: '𑀗',
    14: '𑀘', 15: '𑀙', 16: '𑀚', 17: '𑀛', 18: '𑀜', 19: '𑀝', 20: '𑀞',
    21: '𑀟', 22: '𑀠', 23: '𑀡', 24: '𑀢', 25: '𑀣', 26: '𑀤', 27: '𑀥',
    28: '𑀦', 29: '𑀧', 30: '𑀨', 31: '𑀩', 32: '𑀪', 33: '𑀫', 
    34: '𑀩', 35: '𑀪', 36: '𑀫', 37: '𑀬', 38: '𑀭', 39: '𑀮', 40: '𑀯',
    41: '𑀰', 42: '𑀱', 43: '𑀲', 44: '𑀳', 45: '𑀴', 46: '𑀵', 47: '𑀶',
    48: '𑀷', 49: '𑀸', 50: '𑀹', 51: '𑀺', 52: '𑀻', 53: '𑀼', 54: '𑀽',
    55: '𑀾', 56: '𑀿', 57: '𑁀', 58: '𑁁', 59: '𑁂', 60: '𑁃', 61: '𑁄',
    62: '𑁅', 63: '𑁆', 64: '𑁇', 65: '𑁈', 66: '𑁉', 67: '𑁊', 68: '𑁋',
    69: '𑁌', 70: '𑁍', 71: '𑁎', 72: '𑁏', 73: '𑁐', 74: '𑁑', 75: '𑁒',
    76: '𑁓', 77: '𑁔', 78: '𑁕', 79: '𑁖', 80: '𑁗', 81: '𑁘', 82: '𑁙',
    83: '𑁚', 84: '𑁛', 85: '𑁜', 86: '𑁝', 87: '𑁞', 88: '𑁟', 89: '𑁠',
    90: '𑁡', 91: '𑁢', 92: '𑁣', 93: '𑁤', 94: '𑁥', 95: '𑁦', 96: '𑁧',
    97: '𑁨', 98: '𑁩', 99: '𑁪', 100: '𑁫', 101: '𑁬', 102: '𑁭', 103: '𑁮',
    104: '𑁯', 105: '𑁰', 106: '𑁱', 107: '𑁲', 108: '𑁳', 109: '𑁴', 110: '𑁵',
    111: '𑁶', 112: '𑁷', 113: '𑁸', 114: '𑁹', 115: '𑁺', 116: '𑁻', 117: '𑁼',
    118: '𑁽', 119: '𑁾', 120: '𑁿', 121: '𑂀', 122: '𑂁', 123: '𑂂', 124: '𑂃',
    125: '𑂄', 126: '𑂅', 127: '𑂆', 128: '𑂇', 129: '𑂈', 130: '𑂉', 131: '𑂊',
    132: '𑂋', 133: '𑂌', 134: '𑂍', 135: '𑂎', 136: '𑂏', 137: '𑂐', 138: '𑂑',
    139: '𑂒', 140: '𑂓', 141: '𑂔', 142: '𑂕', 143: '𑂖', 144: '𑂗', 145: '𑂘',
    146: '𑂙', 147: '𑂚', 148: '𑂛', 149: '𑂜', 150: '𑂝', 151: '𑂞', 152: '𑂟',
    153: '𑂠', 154: '𑂡', 155: '𑂢', 156: '𑂣', 157: '𑂤', 158: '𑂥', 159: '𑂦',
    160: '𑂧', 161: '𑂨', 162: '𑂩', 163: '𑂪', 164: '𑂫', 165: '𑂬', 166: '𑂭',
    167: '𑂮', 168: '𑂯', 169: '𑂰', 170: '𑂱', 171: '𑂲', 172: '𑂳', 173: '𑂴',
    174: '𑂵', 175: '𑂶', 176: '𑂷', 177: '𑂸', 178: '𑂹', 179: '𑂺', 180: '𑂻',
    181: '𑂼', 182: '𑂽', 183: '𑂾', 184: '𑂿', 185: '𑃀', 186: '𑃁', 187: '𑃂'
}

# Function to Convert Brahmi Characters to Devanagari
def brahmi_to_devanagari_conversion(brahmi_sequence):
    word = ""
    for char in brahmi_sequence:
        if char in brahmi_to_devanagari:
            word += brahmi_to_devanagari[char]
    return word

# Function to Map Predicted Index Values to Brahmi Characters
def map_indexes_to_brahmi(indexes):
    brahmi_word = []
    for index in indexes:
        if index in index_to_brahmi:
            brahmi_word.append(index_to_brahmi[index])
        else:
            brahmi_word.append('--')  # If index is not in the mapping, add a placeholder
    return brahmi_word

# Confidence Threshold for Prediction
CONFIDENCE_THRESHOLD = 0.6

# Function to Simulate Model Output with Confidence Check
def predict_word_with_confidence(model_output, confidence_scores):
    brahmi_word = []
    for i in range(len(model_output)):
        if confidence_scores[i] < CONFIDENCE_THRESHOLD:
            brahmi_word.append('--')  # Mark word as uncertain if confidence is low
        else:
            brahmi_word.append(model_output[i])
    return brahmi_word

# Example Model Output (Predicted Indexes)
predicted_indexes = [0, 1, 2, 3, 4, 5, 6]
confidence_scores = [0.95, 0.98, 0.45, 0.92, 0.87, 0.55, 0.72]

# Step 1: Map Predicted Indexes to Brahmi Characters
brahmi_sequence = map_indexes_to_brahmi(predicted_indexes)
print("Mapped Brahmi Sequence:", brahmi_sequence)

# Step 2: Check Confidence and Process Prediction
final_brahmi_sequence = predict_word_with_confidence(brahmi_sequence, confidence_scores)
print("Brahmi Sequence with Confidence Threshold:", final_brahmi_sequence)

# Step 3: Convert Brahmi to Devanagari
devanagari_word = brahmi_to_devanagari_conversion(final_brahmi_sequence)
print("Devanagari Word:", devanagari_word)

# If there's a gap (missing character), handle by generating predictions
def generate_word_with_gap_handling(predicted_indexes, confidence_scores):
    brahmi_word = []
    for i in range(len(predicted_indexes)):
        if confidence_scores[i] < CONFIDENCE_THRESHOLD:
            brahmi_word.append('𑀍')  # Placeholder for gaps (or based on prediction rules)
        else:
            brahmi_word.append(index_to_brahmi.get(predicted_indexes[i], '--'))
    return brahmi_word

# Handle gaps in word prediction
final_brahmi_word_with_gap = generate_word_with_gap_handling(predicted_indexes, confidence_scores)
print("Final Brahmi Word with Gap Handling:", final_brahmi_word_with_gap)
