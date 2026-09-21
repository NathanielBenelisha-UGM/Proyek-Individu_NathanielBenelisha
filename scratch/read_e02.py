import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
reader = pypdf.PdfReader('d:/UGM/Teknik Elektro/SEMESTER 7/Proyek Individual/Referensi/Full Referensi/[E02] Unit_Commitment_with_Primary_Frequency_Regulation_Consideration_in_the_Southern_Sulawesi_Power_System.pdf')
page = reader.pages[1]

# Let's inspect the characters and their exact unicode codepoints in equations (7) to (10)
text = page.extract_text()
lines = text.split('\n')
for i, line in enumerate(lines):
    if any(f'({num})' in line for num in range(1, 11)):
        print(f"L{i}: {line}")
        # print codepoints
        cps = " ".join(f"U+{ord(c):04X}({c})" for c in line)
        print(f"     {cps}")
