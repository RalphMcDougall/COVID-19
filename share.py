import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date


STYLING = """<style>
body {
    font-family: Arial;
}
section {
    border-bottom-style: solid;

}

h1 {
    color: darkblue;
    font-size: 200%;
    align: center;
}
h2 {
    color: darkslateblue;
    font-size: 150%;
    align: center;
}

p {
    font-size: 125%;
    padding: 5px;
}

table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}

th, td {
    padding: 5px;
}

img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 50%
}

</style>
"""


def sendEmail(covInfo, images, testing):
    print("Sending email")
    ME = ""
    PASSWORD = ""

    with open("../ralphmcddev.txt", "r") as f:
        l = f.readlines()
        ME = l[0].strip()
        PASSWORD = l[1].strip()
        f.close()

    msg = MIMEMultipart()
    today = date.today()
    d = today.strftime("%d %B %Y")
    msg["Subject"] = "COVID-19 Analysis: " + d
    msg["From"] = ME
    MAILING_LIST = []

    if not testing:
        print("GETTING MAILING LIST")
        with open("mailing_list.txt", "r") as f:
            MAILING_LIST = f.readlines()
            MAILING_LIST = map(lambda v: v.strip(), MAILING_LIST)
            f.close()
    else:
        MAILING_LIST = [ME]
    msg["To"] = ", ".join(MAILING_LIST)

    print()
    print("From:", msg["From"])
    print("To:", msg["To"])
    print("Subject:", msg["Subject"])
    print()

    mail_content = """\
<html>
    <head>{0}</head>
    <body>
        <h1> DAILY COVID-19 REPORT: {1}</h1>
        {2}
        <p>
        Data source: Johns Hopkins University <br>
        <i>
        If there are any problems with this email, please contact <a href="mailto:ralphmcdougall2000@gmail.com">Ralph McDougall</a>.
        </i>
        </p>
    </body>
</html>
""".format(STYLING, d, covInfo)
    #print("Message contents:\n\n" + mail_content)

    with open("reports/" + today.strftime("%d-%m-%Y") + "_report.html", "w") as f:
        f.write(mail_content)
        f.close()

    for file in images:
        with open(file, "rb") as fp:
            img = MIMEImage(fp.read(), name=file.split("/")[1])
            img.add_header("Content-ID", "<" + file + ">")
        print("Attaching image:", file)
        msg.attach(img)
    msg.attach(MIMEText(mail_content, "html"))

    print("Connecting to SMTP server")
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(ME, PASSWORD)
    s.sendmail(ME, MAILING_LIST, msg.as_string())
    s.quit()
    print("Success")
