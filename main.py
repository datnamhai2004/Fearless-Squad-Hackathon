from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import os
import datetime
from gtts import gTTS
import openai
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv

from pydantic import BaseModel
from typing import List
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Define directories and load API key
AUDIO_FOLDER = "frontend/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)
openai.api_key = os.getenv('OPENAI_API_KEY')
CHAT_HISTORY_FILE = "chat_history.txt"

# Mount static and template directories
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")


def generate_response(user_input):
    # Generate text response using OpenAI
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Bạn hãy đọc kỹ yêu cầu là bạn là ai và công việc của bạn là gì. Bi giờ bạn là một trợ lý ảo về phiên dịch viên người dùng bạn hãy nhận biết đầu vào nếu là tiếng việt bạn hãy giúp tôi dịch sang tiếng anh, nếu là tiếng anh thì bạn hãy giúp tôi dịch sang tiếng việt. Bạn hãy nhớ kĩ bạn chỉ dịch từ câu hỏi của nguời dùng thôi mà không trả lời thêm những điều khác. Khi người dùng hỏi j bạn chỉ dịch những điều đấy không trả lời thêm bất cứ điều gì và khi người dùng hỏi tôi là thi bạn    "},
            {"role": "user", "content": user_input}
        ]
    )
    response_text = completion.choices[0].message['content']

    # Create audio from text response
    tts = gTTS(response_text, lang='vi')
    audio_filename = f"response_audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    audio_filepath = os.path.join(AUDIO_FOLDER, audio_filename)
    tts.save(audio_filepath)

    return response_text, audio_filename


def save_chat_history(user_input: str, response: str):
    with open(CHAT_HISTORY_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        f.write(f"{timestamp} - User: {user_input}\n")
        f.write(f"{timestamp} - Bot: {response}\n\n")


def convert_audio_to_wav(input_file_path: str, output_file_path: str):
    audio = AudioSegment.from_file(input_file_path)
    audio.export(output_file_path, format="wav")


def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            lines = f.readlines()
            formatted_lines = []
            for line in lines:
                # Differentiate between User and Bot
                if "User:" in line:
                    formatted_lines.append(f"<div class='chat-message user'>{line.strip()}</div>")
                else:
                    formatted_lines.append(f"<div class='chat-message bot'>{line.strip()}</div>")
            return formatted_lines
    return []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test-pen", response_class=HTMLResponse)
async def test_pen(request: Request):
    return templates.TemplateResponse("test-pen.html", {"request": request})


@app.post("/chat", response_class=JSONResponse)  # Changed from "/chats" to "/chat"
async def chat(user_input: str = Form(...)):
    response_text, audio_filename = generate_response(user_input)
    save_chat_history(user_input, response_text)

    return {
        "user_input": user_input,
        "response": response_text,
        "audio_url": f"/frontend/audio/{audio_filename}"
    }


@app.post("/chat-voice", response_class=JSONResponse)
async def chat_voice(voice: UploadFile = File(...)):
    # Save the uploaded file
    audio_path = os.path.join(AUDIO_FOLDER, voice.filename)
    with open(audio_path, "wb") as f:
        f.write(voice.file.read())

    # Convert the uploaded audio file to WAV format
    wav_audio_path = audio_path.rsplit(".", 1)[0] + ".wav"
    convert_audio_to_wav(audio_path, wav_audio_path)

    # Convert audio to text using speech_recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_audio_path) as source:
        audio_data = recognizer.record(source)
        user_input = recognizer.recognize_google(audio_data, language="vi-VN")

    # Generate response and save it as an audio file
    response_text, audio_filename = generate_response(user_input)

    return {
        "response": response_text,
        "audio_url": f"/frontend/audio/{audio_filename}"
    }


@app.get("/chats", response_class=HTMLResponse)
async def read_chats(request: Request):
    chat_history = load_chat_history()
    return templates.TemplateResponse("chats.html", {"request": request, "chat_history": chat_history})

DATA_FOLDER = "icm20948_data"  # Thư mục lưu file CSV

os.makedirs(DATA_FOLDER, exist_ok=True)


# Mô hình dữ liệu cho từng mẫu
class ICM20948Data(BaseModel):
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float

record_count = 1210  # Khởi đầu từ 207 để tạo file từ readings_207_digit_2
digit_count = 0   # Bắt đầu từ digit 2
current_file_path = None  # Đường dẫn tới file CSV hiện tại
icm20948_data_storage = []  # Biến để lưu trữ dữ liệu ICM-20948

# Endpoint nhận dữ liệu từ cảm biến, bây giờ nhận danh sách các mẫu
@app.post("/icm20948-data")
async def receive_icm20948_data(data: List[ICM20948Data]):  # Nhận danh sách các mẫu
    global current_file_path, icm20948_data_storage

    print(f"Received {len(data)} data samples")  # Hiển thị số lượng mẫu nhận được
    icm20948_data_storage.extend([d.dict() for d in data])  # Lưu trữ tất cả các mẫu dữ liệu vào danh sách

    # Append data to the current file if it exists
    if current_file_path is not None:
        append_batch_to_csv(data, current_file_path)  # Gọi hàm append mới cho dữ liệu theo lô
    else:
        print("No active file. Please create a new file session first.")

    return {"status": "success", "data_count": len(data)}

@app.post("/new-file")
async def create_new_csv_file():
    global record_count, digit_count, current_file_path

    # Create a new CSV file and reset the current file path
    current_file_path = create_new_file(record_count, digit_count)
    record_count += 1  # Tăng record_count thêm 1 để tạo các file liên tiếp
    return {"status": "new file created", "file": current_file_path.name}

def create_new_file(record_id, digit_id):
    # Create a new file based on the record count and digit count
    filename = f"readings_{record_id}_digit_{digit_id}.csv"
    file_path = Path(DATA_FOLDER) / filename  # Path to the new file
    print(f"Tạo file mới: {filename}")
    return file_path

# Hàm mới để append danh sách dữ liệu vào CSV
def append_batch_to_csv(data: List[ICM20948Data], file_path):
    # Convert list of data to DataFrame
    df = pd.DataFrame([d.dict() for d in data])

    # Append batch of data to the current file
    df.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)
    print(f"Lưu {len(data)} mẫu dữ liệu vào file: {file_path.name}")

@app.get("/icm20948-data")
async def get_icm20948_data():
    global icm20948_data_storage
    return {"icm20948_data": icm20948_data_storage}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
