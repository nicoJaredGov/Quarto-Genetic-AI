import numpy as np

def encodeBoard(board_array):
    encoding = ""
    for i in range(4):
        for j in range(4):
            num = board_array[i][j]
            if num <= 9:
                encoding += "0"+str(num)
            else:
                encoding += str(num)
    
    return encoding
    
def decodeBoard(encoding):
    board_array = [int(encoding[i]+encoding[i+1]) for i in range(0,len(encoding),2)]
    board_array = np.reshape(board_array, (4,4))

    return board_array

def get2dCoords(ind):
    assert ind >= 0 and ind < 16, "Invalid linear index. Should be from 0 - 15 inclusive."
    row = ind // 4
    col = ind % 4

    return (row,col)

def getLinearCoords(row, col):
    return 4*row + col

#Determines if there is a matching column of bits for a list of integers between 0 (inclusive) and 16 (exclusive)
def matchingPropertyExists(line):
    #bitwiseAnd - checks if there is a column of 1s by getting the conjunction
    #bitwiseNot - checks if there is a column of 0s after negating all integers, masking by 15 (1111) and then getting the conjuction
    bitwiseAnd = line[0]
    bitwiseNot = ~line[0] & 15
    for i in range(1,len(line)):
        bitwiseAnd &= line[i]
        bitwiseNot &= ~line[i] & 15

    result = bitwiseAnd | bitwiseNot
    return result > 0