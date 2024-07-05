from random import random
import time

def naive_pi(number_of_samples):
    within_circle_count = 0

    for _ in range(number_of_samples):
        x = random()
        y = random()

        if x ** 2 + y ** 2 < 1:
            within_circle_count += 1

    return within_circle_count / number_of_samples * 4

if __name__ == '__main__':
    # how many seconds since 00:00 on the 01/01/1970
    start = time.time()
    x = naive_pi(100000000)
    end = time.time()
    time_secs = end - start
    print('pi is approximately:' ,x)
    print('This took:',time_secs,'Seconds')
    pi_exact="3.14159265358979323"
    # print the final value of pi and elapsed time
    print("For reference the exact value of pi is:")
    print(pi_exact)