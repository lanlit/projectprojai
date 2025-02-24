import re

# 📌 รายการคำหยาบที่ต้องการกรอง (สามารถเพิ่มได้)
BAD_WORDS = ["เหี้ย", "ควย", "เย็ดแม่", "เย็ด", "fuck", "shit", "asshole","กะหรี่","หี","แตด","ส้นตีน","อีเวร","ตอแหล","ดอกทอง","หมอย","สัตว์","สัส","ไอ้","อี"]

def contains_bad_words(text):
    """ ตรวจสอบว่ามีคำหยาบในข้อความหรือไม่ """
    pattern = r"\b(" + "|".join(re.escape(word) for word in BAD_WORDS) + r")\b"
    return re.search(pattern, text, re.IGNORECASE) is not None

def filter_bad_words(text, replacement="***"):
    """ แทนคำหยาบด้วย *** """
    for word in BAD_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
