import pyautogui, cv2
import numpy as np
import easyocr
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import time
json_path=r"C:\Users\HP\Documents\project\memoaura\memoaura\gif.json"
load_gif="C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\df.gif"
def call(triggered_words):
    
    with open(json_path, "r") as f:
        data = json.load(f)
        imgs=[i[0] for i in data]
        if load_gif  not in imgs:
            print("GIF already playing. Skipping new trigger.")
            return
        data.append([load_gif,[100,500]])
        time.sleep(4)
        json.dump(data, open(json_path, "w"), indent=4)

reader = easyocr.Reader(['en'], gpu=True)
stop_words = set(stopwords.words('english'))
trigger_words = {"resign","work","resssign","quite","stop","job","pressure","stress","depression","sex","fear","threat","depressed","stressed","anxiety","deadline","deadline_is_over","tough","pressure"}

def full_screen_ocr():
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    results = reader.readtext(gray)
    texts = " ".join([text for (_, text, _) in results])
    words = set(word.lower() for word in word_tokenize(texts)
                if word not in string.punctuation and word.lower() not in stop_words)
    if trigger_words & words:
        print(f"Trigger word detected: {trigger_words & words}")
        call(trigger_words & words)
    #reset the logo
    with open(json_path, "r") as f:
        data = json.load(f)
        for i in data:
            if i[0]==load_gif:
                data.remove(i)
                break
        json.dump(data, open(json_path, "w"), indent=4)

if __name__ == "__main__":
    while True:
        full_screen_ocr()
