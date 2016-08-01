import requests
import lxml.html
import re
import json
import base64


def load_credentials(credentials_file):
    with open(credentials_file) as file:
        credentials = json.loads(file.read())
        return base64.b64decode(credentials["username"]), base64.b64decode(credentials["password"])


def get_title(page_text):
    doc = lxml.html.document_fromstring(page_text)
    search = doc.xpath("//div[@class='dotd-title']")
    return search[0].text_content().lstrip().rstrip()


with requests.session() as session:
    free_book_url = 'https://www.packtpub.com/packt/offers/free-learning'
    initial_page = session.get(free_book_url, verify=False)
    login_form = None
    for element in lxml.html.fromstring(initial_page.text).findall('.//form'):
        if 'packt-user-login-form' in element.values():
            form = element
            break

    login_payload = {form.inputs.keys()[index]: form.inputs[key].value for index, key in enumerate(form.inputs.keys())}
    login_payload["email"], login_payload["password"] = load_credentials("credentials.json")
    login = session.post(free_book_url, data=login_payload, verify=False)
    print("Today's free eBook is {0}".format(get_title(login.text)))

    claim_search = re.search('\/freelearning-claim\/\d+\/\d+', login.text)
    claim_book = session.get('https://www.packtpub.com' + claim_search.group(0), allow_redirects=False)
    if claim_book.status_code == 302:
        print("Successfully redeemed.")
    else:
        print("Error redeeming book. ")

