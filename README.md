# Orange3 Example Widgets

Orange3를 위한 LLM 기반 사용자 정의 위젯 모음입니다.

## 설치

```bash
pip install orange3-example
```

## 포함된 위젯

### 1. LLM Transformer

GPT API를 통해 입력 데이터를 변환하는 위젯입니다.

**기능:**

- 텍스트 데이터를 LLM으로 변환
- 사용자 정의 프롬프트 입력
- OpenAI API Key 설정

**사용법:**

1. 위젯을 Canvas에 추가
2. OpenAI API Key 입력
3. 프롬프트 입력
4. 입력 데이터 연결 후 "변환 실행" 버튼 클릭

### 2. Image LLM

이미지와 텍스트를 입력받아 멀티모달 LLM으로 처리하는 위젯입니다.

**기능:**

- 이미지 + 텍스트 멀티모달 처리
- GPT-4o 모델 사용
- 실시간 이미지 표시

**사용법:**

1. 위젯을 Canvas에 추가
2. OpenAI API Key 입력
3. 이미지 데이터와 텍스트 데이터 연결
4. 프롬프트 입력 후 자동 처리 또는 버튼 클릭

### 3. Microbit Communicator

시리얼 포트를 통해 마이크로비트로 데이터를 전송하는 위젯입니다.

**기능:**

- 시리얼 포트 연결
- 텍스트 데이터 자동/수동 전송
- 연결 상태 모니터링

**사용법:**

1. 위젯을 Canvas에 추가
2. 포트 선택 및 연결
3. 입력 텍스트 데이터 연결
4. 자동 전송 활성화 또는 수동 전송 버튼 클릭

### 4. Webcam Viewer

웹캠을 실시간으로 표시하고 이미지를 캡쳐하는 위젯입니다.

**기능:**

- 실시간 웹캠 미리보기
- 이미지 캡쳐 및 전송
- 웹캠 시작/중지 제어

**사용법:**

1. 위젯을 Canvas에 추가
2. "웹캠 시작" 버튼 클릭
3. "이미지 캡쳐" 버튼으로 현재 프레임 캡쳐 및 전송

웹캠 기능은 선택 의존성입니다. 필요 시 다음으로 설치하세요:

```bash
pip install "orange3-example[webcam]"
```

## 요구사항

- Python 3.6+
- Orange3 >= 3.32.0
- OpenAI API Key (LLM 위젯 사용 시)

## 의존성

- Orange3
- openai
- PyQt5
- python-dotenv
- pyserial

## 라이선스

MIT License

## 저자

Gangjun Jo

## 링크

- GitHub: https://github.com/whyz-dev/Orange3-Widget
- PyPI: https://pypi.org/project/orange3-example/
