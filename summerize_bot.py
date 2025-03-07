import discord
import cohere
import asyncio
import deepl
import os
from dotenv import load_dotenv
from discord.ext import commands

# ✅ 환경 변수 로드
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# ✅ Cohere & DeepL 클라이언트 초기화
co = cohere.Client(COHERE_API_KEY)
deepl_translator = deepl.Translator(DEEPL_API_KEY)

# ✅ Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ 메시지 요약 함수
async def summarize_messages(messages):
    combined_text = "\n".join(messages)
    print(f"[DEBUG] Combined Text: {combined_text}")  # 디버깅

    if len(combined_text) >= 150:
        try:
            response = co.chat(
                model="command-r",
                message=f"Summarize the following messages:\n{combined_text}",
                max_tokens=200
            )
            english_summary = response.text.strip()
            print(f"[DEBUG] English Summary: {english_summary}")

            # ✅ DeepL 번역
            korean_summary = deepl_translator.translate_text(english_summary, target_lang="KO").text
            print(f"[DEBUG] Korean Summary: {korean_summary}")

            # ✅ 요약을 5줄로 마크다운 형식 적용
            summary_lines = korean_summary.split(". ")
            formatted_summary = "\n".join([f"• {line.strip()}" for line in summary_lines[:5]])

            return formatted_summary

        except Exception as e:
            print(f"Error: {e}")
            return "❌ 요약 실패: API 요청 중 오류가 발생했습니다."
    else:
        return "⚠️ 요약할 메시지가 너무 짧습니다."

# ✅ !요약 명령어 처리
@bot.command(name="요약")
async def summarize(ctx):
    messages = []
    loading_message = await ctx.send("🔄 **요약을 시작합니다...**")

    # ✅ 최근 메시지 100개 가져오기
    async for msg in ctx.channel.history(limit=100):
        if msg.author != bot.user:
            messages.append(msg.content)

    print(f"[DEBUG] Collected Messages: {messages}")

    if messages:
        # ✅ 진행 중 애니메이션 효과
        loading_steps = [
            "⏳ **요약을 분석 중...**",
            "📖 **핵심 내용을 추출하는 중...**",
            "📋 **요약을 정리하고 있습니다...**",
            "✅ **곧 결과를 출력합니다!**"
        ]
        for step in loading_steps:
            await loading_message.edit(content=step)
            await asyncio.sleep(1.5)  # 단계별로 시간 간격 추가

        summarized = await summarize_messages(messages)
        
        # ✅ 최종 요약 결과 출력
        await loading_message.edit(content=f"📢 {ctx.author.mention} **요약된 내용:**\n```\n{summarized}\n```")
    else:
        await loading_message.edit(content="❌ **요약할 메시지가 없습니다.**")

# ✅ Discord 봇 실행
bot.run(DISCORD_TOKEN)
