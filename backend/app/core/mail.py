import emails
from app.config import settings 
import yagmail

def send_otp_email(email_to: str, otp: str):
    # Dùng yagmail để gửi mail. 
    # Nếu nó lỗi, nó sẽ throw Exception ngay tại đây, ông chỉ cần bắt nó.
    try:
        yag = yagmail.SMTP(user=settings.SMTP_USER, password=settings.SMTP_PASSWORD)
        yag.send(
            to=email_to,
            subject="[OldShop] Ma xac thuc OTP",
            contents = [
                f"Chào bạn,",
                f"Chúng tôi đã nhận được yêu cầu xác thực từ tài khoản của bạn tại {settings.PROJECT_NAME}.",
                f"",
                f"Mã OTP (One-Time Password) của bạn là:",
                f"----------------------------------------",
                f"             {otp}              ",
                f"----------------------------------------",
                f"",
                f"* Lưu ý: Mã xác thực này có hiệu lực trong vòng 05 phút và chỉ sử dụng một lần duy nhất.",
                f"Vì lý do an toàn, vui lòng không cung cấp mã này cho bất kỳ ai.",
                f"",
                f"Nếu bạn không thực hiện yêu cầu này, hãy bỏ qua email này hoặc liên hệ với đội ngũ hỗ trợ của chúng tôi.",
                f"",
                f"Trân trọng,",
                f"Đội ngũ vận hành {settings.PROJECT_NAME}"
            ]
        )
        return True
    except Exception as e:
        # Thay vì để app crash, mình in ra log để biết tại sao
        print(f"SMTP ERROR: {e}")
        return False