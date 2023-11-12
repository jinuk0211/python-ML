import random
def guess(x):
    random_number = random.randint(1,x)

    while guess != random_number:
        guess = int.input(f'1과 {x} 사이에서 guess 해주세요 : ')
        if guess < random_number:
            print('틀렸습니다. 더 큰 수를 입력해주세요')
        elif guess > random_number:
            print('틀렸습니다. 더 작은수를 입력해주세요')
            
    print(f"축하합니다!! 정답은 {random_number}이였습니다!!")
guess(10)

def computer_guess(x):
    low = 1
    high = x
    feedback = ''
    #c is '정답'
    while feedback != '적중': 
        if low != high:
            guess = random.randint(low, high)
        else:
            guess = low
        feedback = input(f"제가 적은 {guess}가 너무 큰가요(네,아니요) 맞았다면(적중)을 쳐주세요 ")
        if feedback == '네':
            high = guess - 1
        elif feedback == '아니요':
            low = guess + 1

    print('!! 제가 당신이 생각한{guess}를 맞춰냈습니다!!')

    computer_guess(10)
