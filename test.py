import smtplib  # SMTP 사용을 위한 모듈
import re  # Regular Expression을 활용하기 위한 모듈
from email.mime.multipart import MIMEMultipart  # 메일의 Data 영역의 메시지를 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from email.mime.image import MIMEImage  # 메일의 이미지 파일을 base64 형식으로 변환하기 위한 모듈
 
def sendEmail(addr):
    reg = "^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$"  # 유효성 검사를 위한 정규표현식
    if re.match(reg, addr):
        smtp.sendmail(my_account, to_mail, msg.as_string())
        print("정상적으로 메일이 발송되었습니다.")
    else:
        print("받으실 메일 주소를 정확히 입력하십시오.")
 
# smpt 서버와 연결
gmail_smtp = "smtp.gmail.com"  # gmail smtp 주소
gmail_port = 465  # gmail smtp 포트번호. 고정(변경 불가)
smtp = smtplib.SMTP_SSL(gmail_smtp, gmail_port)
 
# 로그인
my_account = "lgit1024372@gmail.com"
#my_password = "3721024lgit"
my_password ="cmvbwxafxrnlqvue"
smtp.login(my_account, my_password)
 
# 메일을 받을 계정
#to_mail = "ericsa@nate.com;ericsa@naver.com"

to_mail_list = ["ericsa@nate.com", "sarum007@naver.com"]

for to_mail in to_mail_list:
    # 메일 기본 정보 설정
    msg = MIMEMultipart()
    msg["Subject"] = f"조사해주시고 도와주세요"  # 메일 제목
    msg["From"] = my_account
    msg["To"] = to_mail

    content = """
    피해자 : 강세은
    가해자 : 김일환
    목격자 : 백승완, 고성수

    들은 내용:
    강세은, 김일환 업무 논의 중 목소리가 커지며 말싸움으로 번져
    김일환이 강세은에게 마우스를 던진 이후 한번더 커피를 뿌리고
    강세은이 소리 지르자 몇차례 더 언쟁 후 김일환 나갔고 목격자들이 뒷수습

    하고싶은 말:
    한달전쯤에 세은이가 어려운 상황을 겪었다는 소식을 듣고, 도와주고 싶었지만 세은이는 자존심이 강한 편이라서 제 도움을 받는 것을 꺼릴 것 같았어요.

    주변 지인들을 통해 광주쪽 JB에게 그녀의 상황을 이야기하고 면담을 요청했는데, 세은이가 응원만 해달라는... 답변을 받았다더라구요. 이후에 여기 개발팀 사람들과 얘기를 나눠보니, 세은이가 너무 어려운 상황에 처해 있다는 생각이 들어서 메일을 쓰게 되었어요.

    김일환이라는 분은 마곡에서는 그런 행동을 한 적이 없다고 하네요. 그런데 왜 이런 일이 발생했을까해서 개발팀 친한사람들께 물어보니 세은이가 속한 팀에 문제가 있다는 얘길 듣게 됐어요. 그 팀에 김일환님과 친한 사람은 마곡에서 불미스러운 일로 인해 광주로 오게 된 사람도 있고, 세은이 팀의 팀장도 원래는 개발팀에 있었지만, 여러 문제가 있었다고 하더라고요. 내용이 다 기억이 나지 않지만, 괴롭힘을 당한 팀원도 있었고, 인사팀에도 알정도의 많은 사건이 있었다고 해요.

    그래서 세은이가 그런 어려움을 겪고 있다는 것을 알면서도 팀장이 적극적인 조치를 취하지 않고 있고, 계속 그런 폭력에 노출될 가능성이 있다는 걱정이 들었어요... 더 걱정 되는건 광주에는 여직원 성추행으로 퇴사한 팀장도 있었다는데. 그런 환경에서 세은이가 계속해서 그 팀에 남아 있는 게 안전한지 의문스럽더라구요. 여기 개발팀에서 들은 이야기가 과장된 것인지는 모르겠지만, 그게 사실이라면 상당히 심각해 보였어요.

    세은이가 아이들 때문에 다른 지역이나 팀으로 이동할 수 없어서 힘들어하는 모습을 보니 마음이 아프더라구요... 다른 여직원들은 그런 상황이 없었을까요? 그리고 세은이가 피해를 입지 않도록 어떻게 조치를 취할 수 있을까요?

    익명으로 메일을 보내는 이유는 누가 보냈는지 알려면 세은이가 원망할 것 같아서예요... 이 메일은 비밀로 해주시고, 개발팀의 목격자 두분과 사실 조사를 먼저 해주시면 좋을 것 같아요.
    """
    content_part = MIMEText(content, "plain")
    msg.attach(content_part)

    # 받는 메일 유효성 검사 거친 후 메일 전송
    sendEmail(to_mail)

    # smtp 서버 연결 해제
smtp.quit()
