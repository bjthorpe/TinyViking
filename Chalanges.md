---
layout: page
title: "Python Coding Challenges"
permalink: /Challenges/
---

Here are a two challenges to attempt. Pick 1 to do today, although feel free to try them both.

Note These are intentionally a bit of a challenge. As such don't feel to bad if you get stuck and don't finish today.

Also we have given some hints to set you off but we expect to look things up, I hear google works well for this.

## 1. $\pi$ by Montecarlo

You mission, should you choose to accept it. Use a Monte Carlo simulation to estimate the irrational number $\pi$.

Monte Carlo methods are a broad class of computational algorithms that rely on repeated random sampling to obtain numerical results. One of the basic examples of getting started with the Monte Carlo algorithm is the estimation of $\pi$.

### Estimation of Pi.

The idea is to simulate random (x, y) points in a 2-D square of side length $2r$ with units centred on (0,0). Now take a circle inside the same square with radius $r$, again centred at (0,0). We can calculate the ratio of number points that land inside the circle against total number of generated points.

!["plot to show points inside the square/circle"](MonteCarlo.png "plot to show points inside the square/circle")

We know that area of the square is $4r^2$ while that of circle is $\pi r^2$. The ratio of these two areas is as follows :

$\tfrac{\pi r^2}{4r^2} = \tfrac{\pi}{4}$

Therefore if we use the number of points in the square as an estimate for the area we get:

$4*\frac{N_{Circle}}{N_{Total}} = \pi$

### 🎯 Goal

1. Estimate the value of $\pi$ using a Monte Carlo method by:
    * Randomly generating points in a unit square.
    * Count how many fall inside the unit circle.
    * compute $\pi$ ≈ 4 × (points inside circle / total points)
2. Time how long your estimate takes and output the result
3. Plot points inside the circle in red and outside in blue
4. check your accuracy against the "exact" value of $\pi$ to say 50-100 dp.
5. Try to get as close as possible in a runtime of under 1 minute.

### Tips

* To time how long something takes you will need the python time package.
* Python has a built in package for generating random numbers, however, we recommend looking into the numpy version **numpy.random()**.
* Although they display up to 16 decimal places, python's built-in floats are generally only accurate to about 8-10 decimal places. Thus you may wish to look up the decimal package for more accuracy.

## 2. Finding prime numbers

Very large prime numbers are useful in many areas of mathematics, especially cryptography.

You mission, should you choose to accept it is to:

1. Try to find the most prime numbers in under 1 minute.
2. Find which is the nearest prime number less than 52,000,000?

For reference a prime number is a number that only divides into 1 and itself. The first 8 prime numbers are 2,3,5,7,11,13 and 17.

A simple, if inefficient way to check if a integer N is prime would be to check if it divides into every integer smaller than itself. However, we hope you quickly realise **this will not scale**.

```python
N = 16
is_prime = True
for i in range(1,N):
# Note the % operator which you 
# may not have seen before.
    if N%i == 0:
        is_prime = False
print(is_prime)
```

Note the Modulus (%) operator will return the reminder of a division of two integers. In this case we are looking for 0 as that means the number i divides N exactly which tells us N is not prime.

### Some Helpful Advice

* To time how long something takes you will need the python time package.
* There exist many more efficient ways to achieve this goal. you may wish to look into the Sieve of Eratosthenes as a starting point.
* For the sake of checking things, (and possibly your sanity) you may wish to output the numbers to a file instead of the screen. Thus the write function may prove useful which can be used as follows:

```python
with open('output.txt', 'a') as f:
    f.write('Hi')
    f.write('Hello from AskPython')
    f.write('exit')
```
