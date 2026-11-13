import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/resolve")
async def resolve_url(url: str = Query(...)):
    try:
        # إعدادات yt-dlp لاستخراج الرابط فقط دون تحميل الفيديو
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best[ext=mp4]/best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # محاولة إيجاد الرابط المباشر للفيديو
            if 'url' in info:
                return {"direct_url": info['url']}
            elif 'formats' in info:
                formats = [f for f in info['formats'] if f.get('vcodec') != 'none']
                if formats:
                    return {"direct_url": formats[-1]['url']}
            
            raise HTTPException(status_code=400, detail="No direct URL found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "ASQ Fetch Backend is running!"}
