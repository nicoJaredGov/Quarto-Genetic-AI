import numpy as np
import pandas as pd

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

# Determines if there is a matching column of bits for a list of integers between 0 (inclusive) and 16 (exclusive)
def matchingPropertyExists(line):
    # bitwiseAnd - checks if there is a column of 1s by getting the conjunction
    # bitwiseNot - checks if there is a column of 0s after negating all integers, masking by 15 (1111) and then getting the conjuction
    bitwiseAnd = line[0]
    bitwiseNot = ~line[0] & 15
    for i in range(1,len(line)):
        bitwiseAnd &= line[i]
        bitwiseNot &= ~line[i] & 15

    result = bitwiseAnd | bitwiseNot
    return result > 0

def isGameOver(board): 
    for i in range(4):
        # check horizontal lines
        if np.count_nonzero(board[i] == 16) == 0:
            if matchingPropertyExists(board[i]):
                return True
            
        # check vertical lines
        if np.count_nonzero(board[:,i] == 16) == 0:
            if matchingPropertyExists(board[:,i]):
                return True

    # check obtuse diagonal line
    if np.count_nonzero(np.diag(board) == 16) == 0:
        if matchingPropertyExists(np.diag(board)):
                return True
        
    # check acute diagonal line:
    if np.count_nonzero(np.diag(board[::-1]) == 16) == 0:
        if matchingPropertyExists(np.diag(board[::-1])):
                return True
    
    # no winning line found
    return False

# transposition table functions
def createTable(file_name: str):
    df = pd.DataFrame(columns=['encoding', 'evaluation', 'movePos', 'movePiece'])

    df['encoding'] = df['encoding'].astype('str')
    df['evaluation'] = df['evaluation'].astype('int8')
    df['movePos'] = df['movePos'].astype('int8')
    df['movePiece'] = df['movePiece'].astype('int8')

    df.to_pickle(f'tables/{file_name}.pkl')

