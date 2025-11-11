# -*- coding: utf-8 -*-
import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

class LLM:
    """GPT API를 호출하는 클래스"""
    def __init__(self, api_key: Optional[str] = None):
        # 우선순위: 위젯 입력 키 > .env > 환경변수
        load_dotenv()
        effective_key = api_key or os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=effective_key)

    def get_response(self, prompt, data_list):
        """GPT의 응답을 받아서 그대로 반환"""
        results = []

        for data in data_list:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": str(data)},
                    ],
                    temperature=0,
                )
                results.append(response.choices[0].message.content.strip())

            except Exception as e:
                results.append(f"Error: {str(e)}")  # 오류 발생 시 메시지 추가

        return results

    def get_multimodal_response(self, prompt, multimodal_data):
        """멀티모달 데이터(이미지+텍스트)를 처리하는 메서드"""
        try:
            # 멀티모달 메시지 구성
            messages = [{"role": "system", "content": prompt}]
            
            # 사용자 메시지 구성
            user_content = []
            
            for item in multimodal_data:
                if item["type"] == "image":
                    # 이미지 데이터를 base64로 전송
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{item['data']}",
                            "detail": "low"
                        }
                    })
                elif item["type"] == "text":
                    # 텍스트 데이터 추가
                    if user_content and user_content[-1].get("type") == "text":
                        # 이미 텍스트가 있으면 기존 텍스트에 추가
                        user_content[-1]["text"] += f"\n{item['data']}"
                    else:
                        # 새로운 텍스트 블록 생성
                        user_content.append({
                            "type": "text",
                            "text": item["data"]
                        })
            
            # 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            # GPT-4o 모델로 멀티모달 요청
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0,
                max_tokens=1000
            )
            
            return [response.choices[0].message.content.strip()]
            
        except Exception as e:
            return [f"멀티모달 처리 오류: {str(e)}"]

    