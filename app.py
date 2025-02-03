import os

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ETF_KEYWORDS = ["etf", "ETF", "이티에프"]
ETF_CHECK_POSTFIX = "더 많은 ETF 정보는 ETF CHECK(https://www.etfcheck.co.kr/)를 확인하세요."


class ChatMessage(BaseModel):
    message: str


@app.post("/chat")
async def chat(chat_message: ChatMessage):
    system_prompt = """당신은 사용자의 금융 질문에 전문적이고 친근하게 답변하는 AI 금융 어드바이저입니다.
복잡한 금융 개념을 일반인도 쉽게 이해할 수 있도록 설명합니다.
전문 용어를 사용할 때는 반드시 쉽게 풀어서 설명합니다.
---
<대화 원칙>
- 모든 답변의 분량은 길지 않고 간결해야합니다.
- 해당 개념의 기본 정의을 설명하세요.
- 유사하거나 관련된 다른 금융 개념을 함께 알려주세요.
- 전문 용어는 쉬운 말로 풀어서 설명합니다.
---
<추가 기능>
- 객관적이고 중립적인 정보 제공
- 개인화된 금융 조언은 피하고 일반적인 정보만 제공
---
<금지사항>
- 개인 투자 추천 금지
- 불확실한 정보나 근거 없는 주장 금지
- 특정 금융상품이나 기업에 대한 편향된 의견 금지"""

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_message.message},
            ]
        )
        
        ai_response = response.choices[0].message.content
        
        if any(keyword in chat_message.message.lower() or keyword in ai_response.lower() for keyword in ETF_KEYWORDS):
            ai_response += f"\n\n{ETF_CHECK_POSTFIX}"

        return {"response": ai_response}
    
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)