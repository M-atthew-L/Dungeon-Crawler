import math
listOfFactors = []
def factorial(number, halfOfNumber):
    halfOfNumber = math.ceil(number / 2)
    for num in halfOfNumber:
        isRemainderPresent = number % num
        if isRemainderPresent == 0:
            listOfFactors.append(num)
    return listOfFactors


if __name__ == "__main__": 
    print(factorial(5))