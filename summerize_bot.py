import discord
import cohere
import asyncio
import deepl  # DeepL API 라이브러리 사용

# Discord 봇 토큰 및 Cohere API 키 설정
DISCORD_TOKEN = ''
COHERE_API_KEY = ''
DEEPL_API_KEY = ''  # DeepL API 키 설정

# Cohere 클라이언트 초기화
co = cohere.Client(COHERE_API_KEY)

# DeepL 클라이언트 초기화
deepl_translator = deepl.Translator(DEEPL_API_KEY)

# Discord 클라이언트 초기화
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 메시지 요약 함수
async def summarize_messages(messages):
    combined_text = "\n".join(messages)  # 메시지를 하나의 텍스트로 결합
    print(f"[DEBUG] Combined Text: {combined_text}")  # 디버깅: 결합된 텍스트 출력

    if len(combined_text) >= 150:  # 텍스트가 충분히 길 경우 요약
        # Cohere API 호출
        response = co.generate(
            prompt=combined_text,
            model="command-xlarge-nightly",  # Cohere의 적합한 모델 사용
            max_tokens=150,  # 생성될 요약 길이 제한
            temperature=0.7,  # 텍스트 다양성 조절
        )
        english_summary = response.generations[0].text.strip()  # 생성된 요약 텍스트
        print(f"[DEBUG] English Summary: {english_summary}")  # 디버깅: 영어 요약 출력

        # DeepL을 사용해 영어 요약을 한국어로 번역
        korean_summary = deepl_translator.translate_text(english_summary, target_lang='KO').text
        print(f"[DEBUG] Korean Summary: {korean_summary}")  # 디버깅: 한국어 요약 출력
        return korean_summary
    else:
        return "요약할 메시지가 너무 짧습니다."

# Discord 봇 이벤트 핸들러: 메시지 수신
@client.event
async def on_message(message):
    # 봇 자신의 메시지는 무시
    if message.author == client.user:
        return

    # !요약 명령어 처리
    if message.content.startswith('!요약'):
        messages = []

        # "요약 중" 메시지 전송
        loading_message = await message.channel.send("요약 중입니다. 잠시만 기다려주세요...")

        # 최근 메시지 최대 100개 가져오기
        async for msg in message.channel.history(limit=100):
            if msg.author != client.user:  # 봇의 메시지는 제외
                messages.append(msg.content)

        print(f"[DEBUG] Collected Messages: {messages}")  # 디버깅: 수집된 메시지 출력

        # 메시지가 있는 경우 요약 수행
        if messages:
            summarized = await summarize_messages(messages)
            await loading_message.edit(content=f"{message.author.mention} 요약된 내용:\n{summarized}")
        else:
            await loading_message.edit(content="요약할 메시지가 없습니다.")

# Discord 봇 실행
client.run(DISCORD_TOKEN)