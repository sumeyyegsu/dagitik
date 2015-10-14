__author__ = 'sumeyye'

import numpy as np
import matplotlib.pyplot as plt

mu = np.random.uniform(-5.0, 5.0, 2)        #aralikta olan, random iki MU'den olusan bir array yaratiyoruz
sigma = np.random.uniform(0.5, 1.5, 2)      #aralikta olan, random iki SIGMA'dan olusan bir array yaratiyoruz
size = 10000

#rastgele 10000 sayidan olusan, mu ve sigmasi farkli olan iki ayri dizi yaratiyoruz
#bu dizilerdeki her sayiyi kendisine en yakin tam sayiya yuvarliyoruz
a = np.around(np.random.normal(mu[0], sigma[0], size))
b = np.around(np.random.normal(mu[1], sigma[1], size))

hist_a, hist_b = ([0] * 41), ([0] * 41)     #41 tane sifirdan olusan iki ayri histogram dizisi yaratiyoruz

#a ve b dizilerinin ayri ayri histogramlarini olusturuyoruz
for i in range(0, size):
    for j in range(-20, 21):
        if j == a[i]:
            hist_a[j+20] += 1
            continue
        if j == b[i]:
            hist_b[j+20] += 1

#olusturdugumuz iki histogrami da normalize ediyoruz.
hist_a_normalized = np.divide(hist_a, float(sum(hist_a)))
hist_b_normalized = np.divide(hist_b, float(sum(hist_b)))

#olusturdugumuz normalize edilmis histogramlari goruntuluyoruz
plt.axis((-20, 20, 0, 1))
plt.bar(range(-20, 21), hist_a_normalized, color='red')
plt.bar(range(-20, 21), hist_b_normalized, color='blue')
plt.show()

#histogramlar arasindaki mesafeyi hesapliyoruz
i, j, result = 0, 0, 0
while i <= 40 and j <= 40:
    if hist_a_normalized[i] == 0:
        i += 1
        continue
    if hist_b_normalized[j] == 0:
        j += 1
        continue
    if hist_a_normalized[i] > hist_b_normalized[j]:
        result += abs(i-j) * float(hist_b_normalized[j])
        hist_a_normalized[i] -= hist_b_normalized[j]
        hist_b_normalized[j] = 0
        continue
    if hist_a_normalized[i] < hist_b_normalized[j]:
        result += abs(i-j) * float(hist_a_normalized[i])
        hist_b_normalized[j] -= hist_a_normalized[i]
        hist_a_normalized[i] = 0
        continue
    if hist_a_normalized[i] == hist_b_normalized[j]:
        hist_a_normalized[i] = 0
        hist_b_normalized[j] = 0
        continue

print 'Histogramlar arasindaki mesafe: ', result
