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

to_mail_list = ["khjung@lginnotek.com", "ibkang@lginnotek.com", "kangjh@lginnotek.com", "yckwon@lginnotek.com", "hrleader@lginnotek.com", "pdpark@lginnotek.com", "whj00@lginnotek.com", "hslim0113@lginnotek.com", "ctm8106@lginnotek.com"]

for to_mail in to_mail_list:
    # 메일 기본 정보 설정
    msg = MIMEMultipart()
    msg["Subject"] = f"인사팀에서 조금더 현명하게 조치 해주세요."  # 메일 제목
    msg["From"] = my_account
    msg["To"] = to_mail

    content = """
최근 김일환과 강세은 사이에 발생한 사건조사 하셨을건데요. 그 과정이 적절하지 않았던 것 같습니다.

저는 목격자는 아니지만 사건 상황에 대해 간접적으로 들었습니다. 김일환은 업무 상의 불화로 인해 세은이에게 폭력을 행사하였고, 마우스를 던지며 주변 물건을 파손시키고 커피를 뿌리는 등 아마 블라인드 글로 인사팀에서 조사하는 과정에서 다 아셨을거라 생각 합니다.

세은이는 피해자인데 이 조사로 인해 더 큰 심리적 고통을 겪고 있는 것 같습니다. 사건 발생 당시에도 간접적으로 이야기를 들었고 세은이는 직접 연락하지 않았지만, 최근에 인사 처리 과정에서 얼마나 힘들었는지 전화가 와서 많이 힘들어하는 모습을 보였습니다.
특히 인사과 조사를 받은 사람들에게 추가적인 압박을 받아 매우 힘들어하고 불안해했습니다.

그래서 소식을 전해준 사람들에게 물어보니, 김일환은 이전에는 이러한 사건이 없었다고 했지만, 세은이가 속한 팀에 있는 주변 사람들에 대해 이야기를 들었는데요. 이런 사람들이 왜 주변에 모여 있는지 이해가 되지 않았습니다.
사건사고가 많고 문제가 있는 사람들이 주로 그팀을 리딩을 하고 있다고 했습니다.

세은이 팀에서 다른 여사원도 유사한 사건도 들었고, 가해자들이 선처받고 있다고 느꼈습니다. 만약 해당 팀에서 계속해서 이러한 문제가 발생한다면, 그건 인사팀의 안일한 대처 때문일 것입니다.

세은이에게 다른팀으로 이동하라고 제안해도 육아로 인해 갈수도 없고 팀장도 허락할일 없고 지금도 업무적인 압박이 심한데 더해질것 같아 말 못하겠다고 했습니다.

너무 힘겨워 했습니다. 본인이 하는 일도 그렇고 주변 사람들과도 그렇고... 인사팀에서는 이러한 문제를 심각하게 여겨주시고, 세은이가 더 큰 피해를 받지 않게 적절한 조치를 취하여 주시길 바랍니다.

익명으로 메일을 보내는 이유는 예전에 실명으로 신고 했을때 오히려 신고자가 더 심문 받고 분란을 조장하는 것 처럼 취급 된적이 있어서 입니다.

그때처럼 피해자는 보호받지 못하고 신고자는 제 2의 가해자가 되며 메뉴얼대로 징계처분 받은 가해자와 피해자가 분리되지 않아 지속적으로 위험상황에 노출되게 하지 말아 주세요
    """
    content_part = MIMEText(content, "plain")
    msg.attach(content_part)

    # 받는 메일 유효성 검사 거친 후 메일 전송
    sendEmail(to_mail)

    # smtp 서버 연결 해제
smtp.quit()
