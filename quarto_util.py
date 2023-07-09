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