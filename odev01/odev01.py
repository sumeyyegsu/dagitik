__author__ = 'sumeyye'

import numpy as np
import matplotlib.pyplot as plt

mu = np.random.uniform(-5.0, 5.0, 2)        #aralikta olan, random iki MU'den olusan bir array yaratiyoruz
sigma = np.random.uniform(0.5, 1.5, 2)      #aralikta olan, random iki SIGMA'dan olusan bir array yaratiyoruz
size = 10000

#rastgele 10000 sayidan olusan, mu ve sigmasi farkli olan iki ayri dizi yaratiyoruz
a = np.around(np.random.normal(mu[0], sigma[0], size))
b = np.around(np.random.normal(mu[1], sigma[1], size))

hist_a, hist_b = ([0] * 41), ([0] * 41)     #41 tane sifirdan olusan iki ayri histogram dizisi yaratiyoruz

#a ve b dizilerinin ayri ayri histogramlarini olusturuyoruz
for i in range(0, 10000):
    for j in range(-20, 20):
        if j == a[i]:
            hist_a[j+20] += 1
        if j == b[i]:
            hist_b[j+20] += 1

#olusturdugumuz iki histogrami da normalize ediyoruz.
hist_a_normalized = np.divide(hist_a, sum(hist_a)*1.)
plt.hist(hist_a_normalized, bins=range(-20, 20))
hist_b_normalized = np.divide(hist_b, sum(hist_b)*1.)
plt.hist(hist_b_normalized, bins=range(-20, 20))

#olusturdugumuz histogramlari goruntuluyoruz
plt.show()