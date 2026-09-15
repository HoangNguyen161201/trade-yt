import requests
import sys
import time


OPENCODE_URL = "http://127.0.0.1:55080"


def check_opencode():
    """
    Kiểm tra OpenCode server có đang chạy không.
    """
    try:
        response = requests.get(
            f"{OPENCODE_URL}/global/health",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("healthy"):
                print("OpenCode đang chạy.")
                print("Version:", data.get("version"))
                return True

    except requests.RequestException:
        pass

    return False


def create_session():
    """
    Tạo một session mới trong OpenCode.
    """

    response = requests.post(
        f"{OPENCODE_URL}/session",
        json={},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["id"]


def generate_content(prompt):
    """
    Gửi prompt tới OpenCode và lấy content trả về.
    """

    session_id = create_session()

    print("Session:", session_id)
    print("Đang yêu cầu OpenCode sinh content...")

    response = requests.post(
        f"{OPENCODE_URL}/session/{session_id}/message",
        json={
            "parts": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        },
        timeout=300
    )

    response.raise_for_status()

    data = response.json()

    return extract_text(data)


def extract_text(data):
    """
    Cố gắng lấy text từ response của OpenCode.
    """

    # Một số version/API có thể trả parts
    if isinstance(data, dict):

        # response trực tiếp có parts
        parts = data.get("parts")

        if isinstance(parts, list):
            texts = []

            for part in parts:
                if not isinstance(part, dict):
                    continue

                if part.get("type") == "text":
                    text = part.get("text")

                    if text:
                        texts.append(text)

            if texts:
                return "\n".join(texts)

        # response nằm trong message
        message = data.get("message")

        if isinstance(message, dict):

            parts = message.get("parts")

            if isinstance(parts, list):
                texts = []

                for part in parts:
                    if not isinstance(part, dict):
                        continue

                    if part.get("type") == "text":
                        text = part.get("text")

                        if text:
                            texts.append(text)

                if texts:
                    return "\n".join(texts)

    return str(data)


def main():

    if not check_opencode():

        print()
        print("Không kết nối được tới OpenCode.")
        print()
        print("Hãy chạy OpenCode server trước:")
        print()
        print("    opencode serve --port 4096")
        print()

        sys.exit(1)

    prompt = """
Bạn là một content writer chuyên nghiệp.

Hãy viết một đoạn content TikTok ngắn về chủ đề:

"Cà phê Việt Nam"

Yêu cầu:
- Khoảng 100 từ
- Hook mạnh ở câu đầu tiên
- Giọng văn tự nhiên
- Có cảm xúc
- Không giải thích gì thêm
- Chỉ trả về content
"""

    try:

        content = generate_content(prompt)

        print()
        print("=" * 60)
        print("CONTENT")
        print("=" * 60)
        print()
        print(content)
        print()
        print("=" * 60)

    except requests.RequestException as e:

        print("Lỗi kết nối OpenCode:")
        print(e)

        sys.exit(1)

    except Exception as e:

        print("Lỗi:")
        print(e)

        sys.exit(1)


if __name__ == "__main__":
    main()
