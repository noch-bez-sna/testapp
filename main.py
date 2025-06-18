from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
import shutil
import zipfile
# Создаем экземпляр FastAPI приложения
# Это основной объект, с которым мы будем работать для определения маршрутов (ручек)
app = FastAPI(
    title="Сервер для тестирования и результатов",
    description="Это приложение принимает ZIP-архивы 'тестирование' и 'результаты' и возвращает их.",
    version="1.0.0"
)

# --- Ручка для "тестирования" ---
@app.post("/testing/",
          summary="Принимает ZIP-архив 'тестирование' и возвращает его",
          tags=["Тестирование"])
async def upload_testing_archive(
    file: UploadFile = File(..., description="ZIP-архив с данными для тестирования (картинки, JSON).")
):
    # Проверяем, что загруженный файл - это ZIP-архив (по расширению или Content-Type)
    if not file.filename.endswith(".zip") and file.content_type != "application/zip":
        # Если файл не похож на ZIP, возвращаем ошибку
        raise HTTPException(
            status_code=400,
            detail=f"Ожидается ZIP-архив. Получен файл '{file.filename}' с типом '{file.content_type}'."
        )
    await file.seek(0)

    # Возвращаем файл как потоковый ответ.
    return StreamingResponse(
        file.file,  # Сам файловый объект для чтения
        media_type=file.content_type or "application/zip", # Тип контента, берем из файла или ставим по умолчанию
        headers={
            # Этот заголовок подсказывает браузеру, что файл нужно скачать
            # и какое имя ему дать по умолчанию.
            "Content-Disposition": f"attachment; filename={file.filename}"
        }
    )

# --- Ручка для "результатов" ---
@app.post("/results/",
          summary="Принимает ZIP-архив 'результаты' и ключ пользователя, возвращает архив",
          tags=["Результаты"])
async def upload_results_archive(
    user_key: str = Form(..., description="Уникальный ключ пользователя.", example="user123_abc"),
    file: UploadFile = File(..., description="ZIP-архив с JSON-файлом результатов.")
):

    # Логируем полученный ключ пользователя (в реальном приложении он бы использовался)
    print(f"Получен ключ пользователя для результатов: {user_key}")

    # Аналогично ручке /testing/, проверяем тип файла
    if not file.filename.endswith(".zip") and file.content_type != "application/zip":
        raise HTTPException(
            status_code=400,
            detail=f"Ожидается ZIP-архив для результатов. Получен файл '{file.filename}' с типом '{file.content_type}'."
        )

    # Перемещаем указатель в начало файла для повторного чтения при отправке
    await file.seek(0)

    # Возвращаем файл как потоковый ответ
    return StreamingResponse(
        file.file,
        media_type=file.content_type or "application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={file.filename}"
        }
    )

# --- Точка входа для запуска приложения через Uvicorn ---
# Этот блок выполняется, только если скрипт запускается напрямую (а не импортируется как модуль)
if __name__ == "__main__":
    import uvicorn # ASGI сервер для запуска FastAPI приложений

    # Запускаем Uvicorn сервер
    # host="0.0.0.0" делает сервер доступным со всех сетевых интерфейсов
    # port=8000 стандартный порт для FastAPI примеров
    # reload=True автоматически перезагружает сервер при изменениях в коде (удобно для разработки)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)