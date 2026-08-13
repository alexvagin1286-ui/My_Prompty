import fitz
import os
import glob

output_dir = "processed_results"
if not os.path.exists(output_dir): os.makedirs(output_dir)

# Пути к шрифтам
font_bold = "C:/Windows/Fonts/arialbd.ttf"
font_regular = "C:/Windows/Fonts/arial.ttf"
if not os.path.exists(font_bold): font_bold = font_regular

SIZE_1, SIZE_2, SIZE_3 = 10, 8, 8

pdf_files = glob.glob("*.pdf")

for input_file in pdf_files:
    if "READY_" in input_file: continue
    try:
        doc = fitz.open(input_file)
        print(f"Обработка: {input_file}")
        
        for page in doc:
            page.insert_font(fontname="f_bold", fontfile=font_bold)
            page.insert_font(fontname="f_reg", fontfile=font_regular)

            # 1. RA.RU.311579 (Жирный)
            words = page.get_text("words")
            for w in words:
                if w[4].strip().lower() == "лиц":
                    page.insert_text(fitz.Point(w[2] + 5, w[3] - 2), 
                                     "RA.RU.311579", fontsize=SIZE_1, fontname="f_bold")

            # 2. Начальник отдела (Нежирный)
            # Ищем "должность" как ключевое слово
            inst2 = page.search_for("должность")
            if not inst2: inst2 = page.search_for("доджность")
            for inst in inst2:
                page.insert_text(fitz.Point(inst.x0, inst.y0 - 10), 
                                 "Начальник отдела", fontsize=SIZE_2, fontname="f_reg")

            # 3. В. С. Крылов (Над ВТОРОЙ "фамилия")
            inst3 = page.search_for("фамилия")
            if len(inst3) >= 2:
                target = inst3[1] # Второе вхождение
                page.insert_text(fitz.Point(target.x0, target.y0 - 10), 
                                 "В. С. Крылов", fontsize=SIZE_3, fontname="f_reg")
                print(f"   Найдено 'фамилия': {len(inst3)}. Вставлено над второй.")
            else:
                print(f"   Предупреждение: Найдено только {len(inst3)} слов 'фамилия'")

        output_path = os.path.join(output_dir, f"READY_{input_file}")
        doc.save(output_path)
        doc.close()
    except Exception as e:
        print(f"Ошибка: {e}")

print("-" * 30)
print("Готово! Проверьте результат.")