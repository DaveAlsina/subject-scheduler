# Python3 program to find out all
# combinations of positive
# numbers that add upto given number

# fuente:
# https://www.geeksforgeeks.org/find-all-combinations-that-adds-upto-given-number-2/

# arr - array to store the combination
# index - next location in array
# num - given number
# reducedNum - reduced number

def findCombinationsUtil(arr, index, num, reducedNum, solutions):
    
# Base condition
    if (reducedNum < 0):
        return

# If combination is
# found, print it
    if (reducedNum == 0):

        ans = []
        for i in range(index):
            ans.append(arr[i])

        solutions.append(ans)
        return

# Find the previous number stored in arr[].
# It helps in maintaining increasing order
    prev = 1 if(index == 0) else arr[index - 1]

	# note loop starts from previous
	# number i.e. at array location
	# index - 1

    for k in range(prev, num + 1):
    
        # next element of array is k
        arr[index] = k

        # call recursively with
        # reduced number
        findCombinationsUtil(arr, index + 1, num, reducedNum - k, solutions)


# Function to find out all
# combinations of positive numbers
# that add upto given number.
# It uses findCombinationsUtil()
def findCombinations(n, solutions):
	
	# array to store the combinations
	# It can contain max n elements
	arr = [0] * n

	# find all combinations
	findCombinationsUtil(arr, 0, n, n, solutions)

def filter_combinations(n, solutions, length, max_creds):

    findCombinations(n, solutions);
    filtered_ans = [ans for ans in solutions if len(ans) == length]
    filtered_ans2 = []
    
    for ans in filtered_ans:
        ok = True 

        for number in ans:
            if number > max_creds:
                ok = False

        if ok:
            filtered_ans2.append(ans)
            

    return filtered_ans2

def test():
    # Driver code
    n = 9;
    solutions = []
    required_lenght = 5

    print(filter_combinations(n, solutions, required_lenght))

#test()

# This code is contributed by mits

