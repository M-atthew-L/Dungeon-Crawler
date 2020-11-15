import math
listOfFactors = []
def factors(number):
    listOfFactors = []
    for num in range(1, number + 1):
        isRemainderPresent = number % num
        if isRemainderPresent == 0:
            listOfFactors.append(num)
    return listOfFactors



def timeDisplay(seconds):
    remainingSeconds = seconds % 60
    minutes = math.floor(seconds / 60)
    remainingMinutes = minutes % 60
    hours = math.floor(minutes / 60)
    time = [[0,0],[0,0],[0,0]]
    stringOfHours = str(hours)
    if hours < 24:
        if hours >= 10:
            hoursInTensPlace = stringOfHours[0]
            hoursInOnesPlace = stringOfHours[1]
        else:
            hoursInTensPlace = 0
            hoursInOnesPlace = stringOfHours
    else:
        hoursInTensPlace = 0
        hoursInOnesPlace = 0
    stringOfMinutes = str(remainingMinutes)
    if remainingMinutes >= 10:
        minutesInTensPlace = stringOfMinutes[0]
        minutesInOnesPlace = stringOfMinutes[1]
    else:
        minutesInTensPlace = 0
        minutesInOnesPlace = stringOfMinutes
    stringOfSeconds = str(remainingSeconds)
    if remainingSeconds >= 10:
        secondsInTensPlace = stringOfSeconds[0]
        secondsInOnesPlace = stringOfSeconds[1]
    else:
        secondsInTensPlace = 0
        secondsInOnesPlace = stringOfSeconds
    time[0][0] = hoursInTensPlace
    time[0][1] = hoursInOnesPlace
    time[1][0] = minutesInTensPlace
    time[1][1] = minutesInOnesPlace
    time[2][0] = secondsInTensPlace
    time[2][1] = secondsInOnesPlace
    stringTime = ""
    for subtime in time:
        for number in subtime:
            stringTime = stringTime + str(number)
        stringTime = stringTime + ":"
    return stringTime.strip(":")


     
def formatNumber(number):
    finalNumber = []
    setOfThree = 0
    stringFinalNumber = ""
    stringNumber = str(number)
    lengthOfNumber = len(stringNumber)
    numberOfCommas = math.floor((lengthOfNumber - 1)/ 3)
    numbersToTheLeft = lengthOfNumber - (numberOfCommas * 3)
    if numberOfCommas > 0:
        if numbersToTheLeft > 0:
            finalNumber.append(stringNumber[0:numbersToTheLeft])
            for comma in range(numberOfCommas):
                lastSetOfThree = setOfThree
                setOfThree = 3 * (comma + 1)
                finalNumber.append(stringNumber[numbersToTheLeft + lastSetOfThree: numbersToTheLeft + setOfThree])
    else:
        return str(number)
    for subNum in finalNumber:
        for num in subNum:
            stringFinalNumber = stringFinalNumber + str(num)
        stringFinalNumber = stringFinalNumber + ","
    return stringFinalNumber.strip(",")



def sumFromArray(array):
    listOfFactors = []
    listOfNumbers = array.split(",")
    for num in listOfNumbers:
        finalAnswer += num 
    return finalAnswer


if __name__ == "__main__": 
    print(factors(10))
    assert factors(10) == [1, 2, 5, 10], f"Factors of 10 incorrect, returns {factors(10)} instead of [1, 2, 5, 10]"
    print(timeDisplay(5025))
    assert timeDisplay(5025) == "01:23:45", f"Time of 5025 seconds is incorrect, return {timeDisplay(5025)} instead of 01:23:45"
    print(timeDisplay(61201))
    assert timeDisplay(61201) == "17:00:01", f"Returns {timeDisplay(61201)} instead of 17:00:01"
    print(timeDisplay(87000))
    assert timeDisplay(87000) == "00:10:00", f"Returns {timeDisplay(87000)} instead of 00:10:00"
    print(formatNumber(1000))
    assert formatNumber(1000) == "1,000", f"Returns {formatNumber(1000)} instead of 1,000"
    print(formatNumber(100000))
    assert formatNumber(100000) == "100,000", f"Returns {formatNumber(100000)} instead of 100,000"
    print(formatNumber(20))
    assert formatNumber(20) == "20", f"Returns {formatNumber(20)} instead of 20"