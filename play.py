try:
    import Image
except ImportError:
    from PIL import Image, ImageGrab
import pytesseract
import time
import os
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

t_start = time.time()

test_folder_name = 'test_questions/'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
headers = {'User-Agent': user_agent}
google_url = "https://www.google.com/search?q="

bbox = (0, 550, 800, 1250)  # specific area in the screen


def print_green(text):
    print('\033[92m' + text + '\033[0m')


def make_query(text):
    q = urllib.parse.quote(text)
    query = ''.join([google_url, q])
    return query


def get_response(query):
    # print(query)
    req = urllib.request.Request(query, headers=headers)
    response = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    # removes all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text().lower()


def query_once(quest, ans):
    ans_occ = [0] * len(ans)
    query = make_query(quest)
    content = get_response(query)
    for i in range(0, len(ans)):
        ans_occ[i] += content.count(ans[i].lower())

    return ans_occ


def query_for_all(quest, ans):
    ans_occ = [0] * len(ans)
    for choice in ans:
        query = make_query(''.join([quest, ' %s' % choice]))  # todo if 8: in choice replace with &:
        content = get_response(query)
        for i in range(0, len(ans)):
            ans_occ[i] += content.count(ans[i].lower())
        if 'missing: ' in content:  # todo reduce score not continue
            print('%s missing' % choice)
            # continugnospio
    return ans_occ


def calculate_answer(quest, ans):
    print('Analyzing...')
    ans_occ = [0] * len(ans)
    ans_occ = [x + y for x, y in zip(ans_occ, query_once(quest, ans))]
    print(ans_occ)
    if max(ans_occ) == min(ans_occ) or len(ans) > 3:  # todo added 'or' as temporary fix for removing extra choices from noise
        ans_occ = [x + y for x, y in zip(ans_occ, query_for_all(quest, ans))]
        print(ans_occ)
    print('Answer is:')
    if ' NOT ' not in quest:  # todo never
        print_green(ans[ans_occ.index(max(ans_occ))])
    else:
        print_green(ans[ans_occ.index(min(ans_occ))])  # if quest contains 'NOT' return min(ans_occ)


def feed(image):
    text = pytesseract.image_to_string(image)
    if len(text) > 0:
        question, answers = text.split("?")
        question = question.replace("\n", " ")
        answers = [x for x in answers.split("\n") if x]  # todo remove "-" answers and extra noise
        print('QUESTION IS:', question)
        print('OPTIONS ARE:\n', answers)
        calculate_answer(question, answers)
    else:
        print('No question on screen')


def display_test(file):
    image = Image.open(file)
    feed(image)


def display_multiple_test():
    test_images_folder = os.listdir(test_folder_name)
    for file in test_images_folder:
        if file.endswith(".png"):
            display_test(''.join([test_folder_name, file]))


# tests
# display_test(''.join([test_folder_name, 'test_question_12.png']))
# display_multiple_test()

img = ImageGrab.grab(bbox)
feed(img)
# img.save('box.png')

t_end = time.time()

time_taken = t_end - t_start
print('Took: %f seconds' % time_taken)
