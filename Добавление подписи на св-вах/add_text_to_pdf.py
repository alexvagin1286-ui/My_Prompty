import fitz  # PyMuPDF
import os
import glob

def add_annotation_to_pdf(pdf_path, output_path):
    """
    Находит слово 'лиц', ищет подчеркивание (линию) справа от него,
    и вставляет текст 'RA.RU.311579' жирным Verdana над этой линией.
    """
    # Открываем PDF
    doc = fitz.open(pdf_path)
    
    # Шрифт Verdana Bold
    font_name = "Verdana-Bold"
    
    found = False
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Ищем слово "лиц" (в любом регистре)
        text_instances = page.search_for("лиц")
        
        if not text_instances:
            text_instances = page.search_for("Лиц")
        
        for inst in text_instances:
            # Область поиска подчеркивания СПРАВА от слова
            search_rect = fitz.Rect(
                inst.x1,              # от правого края слова
                inst.y0 - 5,          # чуть выше слова
                inst.x1 + 200,        # на 200 пикселей вправо
                inst.y1 + 5           # чуть ниже слова
            )
            
            # Ищем линии в этой области
            drawings = page.get_drawings()
            
            for d in drawings:
                if d["type"] == "l":  # line
                    line_rect = d["rect"]
                    if search_rect.intersects(line_rect):
                        # Нашли линию-подчеркивание справа
                        print(f"  Найдено подчеркивание на стр. {page_num+1}")
                        
                        # Вычисляем позицию для вставки текста
                        text = "RA.RU.311579"
                        fontsize = 10
                        
                        # Получаем ширину текста
                        text_width = fitz.get_text_length(text, fontname=font_name, fontsize=fontsize)
                        
                        # Центрируем текст над линией
                        center_x = (line_rect.x0 + line_rect.x1) / 2
                        y_pos = line_rect.y0 - 2
                        
                        # Создаём прямоугольник для аннотации
                        rect = fitz.Rect(
                            center_x - text_width/2 - 2,
                            y_pos - 14,
                            center_x + text_width/2 + 2,
                            y_pos + 2
                        )
                        
                        # Добавляем аннотацию FreeText
                        annot = page.add_freetext_annot(
                            rect,
                            text,
                            fontsize=fontsize,
                            fontname=font_name,
                            text_color=(0, 0, 0),
                            fill_color=(1, 1, 1),
                            border_color=(0, 0, 0),
                            border_width=0.5,
                            rotate=0
                        )
                        
                        found = True
                        break
                
                if found:
                    break
            
            if found:
                break
        
        if found:
            break
    
    if not found:
        print(f"  ⚠️ Не найдено слово 'лиц' с подчеркиванием справа")
    
    # Сохраняем результат
    doc.save(output_path)
    doc.close()
    return found

def process_all_pdfs():
    """
    Находит все PDF файлы в текущей папке и обрабатывает их
    """
    # Получаем список всех PDF файлов в текущей директории
    pdf_files = glob.glob("*.pdf")
    
    if not pdf_files:
        print("❌ В текущей папке нет PDF файлов!")
        return
    
    print(f"📁 Найдено {len(pdf_files)} PDF файлов:")
    for f in pdf_files:
        print(f"  - {f}")
    print()
    
    processed = 0
    successful = 0
    
    for pdf_file in pdf_files:
        # Формируем имя выходного файла: добавляем "_" перед расширением
        name, ext = os.path.splitext(pdf_file)
        output_file = f"{name}_.pdf"
        
        print(f"🔄 Обработка: {pdf_file} → {output_file}")
        
        # Проверяем, не существует ли уже выходной файл
        if os.path.exists(output_file):
            print(f"  ⚠️ Файл {output_file} уже существует, пропускаем...")
            continue
        
        try:
            # Обрабатываем PDF
            success = add_annotation_to_pdf(pdf_file, output_file)
            
            if success:
                successful += 1
                print(f"  ✅ Аннотация добавлена")
            else:
                print(f"  ⚠️ Аннотация не добавлена (слово не найдено)")
            
            processed += 1
            
        except Exception as e:
            print(f"  ❌ Ошибка при обработке: {e}")
        
        print()
    
    print(f"📊 Итог: обработано {processed} файлов, успешно добавлено аннотаций в {successful}")

if __name__ == "__main__":
    process_all_pdfs()