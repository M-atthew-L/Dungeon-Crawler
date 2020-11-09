import math
#ax^2 + bx + c
#Question 1
def factorial(number):
    finalAnswer = number
    for n in range(number -1, 1, -1):
        finalAnswer *= n
    return finalAnswer


#Question 2
def fraction(fractionList):
    finalDenominator = fractionList[0][1]
    for i in range(1,len(fractionList)):
        finalDenominator *= fractionList[i][1]
    finalNumerator = 0
    for i in range(len(fractionList)):
        numerator = fractionList[i][0]
        for j in range(len(fractionList)):
            if i != j:
                numerator *= fractionList[j][1]
        finalNumerator += numerator
    return round(finalNumerator / finalDenominator)


#Question 3
def findLongestWord(sentence):
    words = sentence.split(" ")
    currentLongestWord = 0
    for word in words:
        if len(word) > currentLongestWord:
            currentLongestWord = len(word)
            longestWord = word
    return longestWord


#Question 4
#function that takes two parameters a lower bound and an upper bound. It returns all of the prime numbers inside the bounds. Specify no bounds and it will print all prime numbers until stopped.\
def isOdd(number):
    isNumberOdd = number % 2
    if isNumberOdd != 0:
        return True
    else:
        return False

def isPrime(number):
    if isOdd(number) or number == 2:
        halfOfNumber = math.ceil(number / 2)
        for n in range(2, halfOfNumber + 1):
            isNumberPrime = number % n
            if isNumberPrime == 0:
                return False   
        return True
    else:
        return False

def findPrimeNumbers(lowerBound = None, upperBound = None):
    if lowerBound is not None and upperBound is not None:
        if lowerBound >= upperBound:
            raise AssertionError("Upper bound should be greater than lower bound.")
    if lowerBound is not None:
        n = lowerBound
    else:
        n = 2
    while True:
        if upperBound is not None:
            if n >= upperBound:
                break
        if isPrime(n):
            print(n)
        n += 1
    


if __name__ == "__main__": 
    print(fraction([[18, 13], [4, 5]]))
    print(fraction([[36, 4], [22, 60]]))
    print(fraction([[11, 2], [3, 4], [5, 4], [21, 11], [12, 6]]))
    print(findLongestWord("Margaret's toy is a pretty doll."))
    print(findLongestWord("A thing of beauty is a joy forever."))
    print(findLongestWord("Forgetfulness is by all means powerless!"))
    print(factorial(5))
    print(factorial(7))
    print(factorial(12))
    findPrimeNumbers()
    


