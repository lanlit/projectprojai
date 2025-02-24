import os
import pandas as pd
from MyApp.models import Diary

def save_diary_data_to_csv():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../diary_data.csv")

    diaries = Diary.objects.all()

    data = [{"id": d.id, "owner_id": d.owner_id, "content": d.content, "label": d.label} for d in diaries]

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"📂 Diary data saved to {file_path}")

save_diary_data_to_csv()

