# Interactive python client for fizzbot

import json
import urllib.request
import urllib.error

domain = 'https://api.noopschallenge.com'

def print_sep(): print('----------------------------------------------------------------------')

# print server response
def print_response(dict):
    print('')
    print('message:')
    print(dict.get('message'))
    print('')
    for key in dict:
        if key != 'message':
            print('%s: %s' % (key, json.dumps(dict.get(key))))
    print('')

# try an answer and see what fizzbot thinks of it
def try_answer(question_url, answer):
    print_sep()
    body = json.dumps({ 'answer': answer })
    print('*** POST %s %s' % (question_url, body))
    try:
        req = urllib.request.Request(domain + question_url, data=body.encode('utf8'), headers={'Content-Type': 'application/json'})
        res = urllib.request.urlopen(req)
        response = json.load(res)
        print_response(response)
        print_sep()
        return response

    except urllib.error.HTTPError as e:
        response = json.load(e)
        print_response(response)
        return response


def generate_answer(question_data: dict):
    rules = question_data.get('rules')
    if not rules:
        # this is the first question, answer "Python" for it
        return 'Python'
    else:
        rule_numbers = [rule['number'] for rule in rules]
        rule_map = {rule['number']: rule['response'] for rule in rules}
        numbers = question_data.get('numbers', [])
        answers = []
        for number in numbers:
            number = int(number)
            answer = ''
            rule_is_matched = False
            for r in rule_numbers:
                if number % r == 0:
                    rule_is_matched = True
                    answer += rule_map[r]
            if not rule_is_matched:
                answer = str(number)
            answers.append(answer)
        return ' '.join(answers)


# keep trying answers until a correct one is given
def get_correct_answer(question_data: dict, answer_url: str):
    while True:
        answer = generate_answer(question_data)

        response = try_answer(answer_url, answer)

        if (response.get('result') == 'interview complete'):
            print('congratulations!')
            exit()

        if (response.get('result') == 'correct'):
            return response.get('nextQuestion')

# do the next question
def do_question(domain, question_url):
    print_sep()
    print('*** GET %s' % question_url)

    request = urllib.request.urlopen( ('%s%s' % (domain, question_url)) )
    question_data = json.load(request)
    print_response(question_data)
    print_sep()

    next_question = question_data.get('nextQuestion')

    if next_question: return next_question
    return get_correct_answer(question_data, question_url)


def main():
    question_url = '/fizzbot'
    while question_url:
        question_url = do_question(domain, question_url)

if __name__ == '__main__': main()
