"""
STT 및 로컬 명령어 파싱 유틸리티 함수 모듈.

- Whisper로 음성 파일을 텍스트로 변환
- 텍스트에서 로컬 키워드를 기반으로 명령 해석
"""

import whisper

# 명령어와 관련된 키워드 딕셔너리
COMMAND_KEYWORDS = {
    "stop": ["멈춰", "정지", "스톱", "그만"],
    "forward": ["앞으로", "전진", "가"],
    "backward": ["뒤로", "후진"],
    "left": ["왼쪽", "좌회전"],
    "right": ["오른쪽", "우회전"],
}


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """Whisper로 오디오 파일을 텍스트로 변환한다.

    Args:
        audio_path (str): 입력 오디오 파일 경로 (wav, mp3 등)
        model_size (str): Whisper 모델 크기 (tiny, base, small, medium, large)

    Returns:
        str: 인식된 텍스트
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="ko")
    return result["text"].strip()


def parse_command_locally(text: str) -> str:
    """텍스트에서 키워드를 찾아 로봇 제어 명령으로 변환한다.

    Args:
        text (str): STT로 변환된 텍스트

    Returns:
        str: 파싱된 명령 (예: "forward", "stop")
    """
    # 가장 중요한 'stop' 명령을 먼저 확인
    for keyword in COMMAND_KEYWORDS["stop"]:
        if keyword in text:
            return "stop"

    # 다른 명령어들을 순서대로 확인
    for command, keywords in COMMAND_KEYWORDS.items():
        if command == "stop":
            continue
        for keyword in keywords:
            if keyword in text:
                return command

    return "unknown"