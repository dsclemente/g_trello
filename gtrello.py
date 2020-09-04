from imbox import Imbox
import html2text
import requests
import json
import time

with open('config.json') as config_file:
    data = json.load(config_file)

API_KEY = data['API_KEY']
OAUTH_TOKEN = data['OAUTH_TOKEN']
trello_list_id = data['trello_list_id']

# SSL Context docs https://docs.python.org/3/library/ssl.html#ssl.create_default_context

def get_text(content):
  html = (str(content))

  text_maker = html2text.HTML2Text()
  text_maker.ignore_links = True
  text_maker.bypass_tables = False
  

  text = text_maker.handle(html)

  # Slice everything that comes between html': and ]}
  start = "html':"
  end = "]}"
  mail_content = text[text.find(start) + len(start):text.rfind(end)]
  
  # Normalize content, removing unknown chars
  mail_content = mail_content.replace("['","")
  mail_content = mail_content.replace('\\xa0', ' ')
  mail_content = mail_content.replace("\\r\\n'","")
  
  return mail_content


def send_to_trello(mail_content,subject):  
  
  r = requests.post("https://api.trello.com/1/cards?key=" + \
                    API_KEY + "&token=" + OAUTH_TOKEN + \
                    "&name=" + subject + "&idList=" + \
                    trello_list_id + "&desc=" + \
                    mail_content)

  return r
  
with Imbox('imap.gmail.com',
        username = data['mail_username'],
        password = data['mail_password'],
        ssl = True,
        ssl_context = None,
        starttls = False) as imbox:

    fetch_mail_type = imbox.messages(sent_from = data['mail_from_username'])

    # Get all folders
    #status, folders_with_additional_info = imbox.folders()

    # Gets all messages from the inbox
    #all_inbox_messages = imbox.messages()

    for uid, message in fetch_mail_type:
    # Every message is an object with the following keys

        origin = message.sent_from
        receiver = message.sent_to
        subject = message.subject
        headers = message.headers
        message_id = message.message_id
        message_date = message.date
        content = message.body
        message_attachments = message.attachments

        result = get_text(content)
        response = send_to_trello(result,subject)
        
        if response.status_code == 200:
          #imbox.mark_seen(uid)
          imbox.delete(uid)


        time.sleep(1)