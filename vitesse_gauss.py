
# import matplotlib.pyplot as plt
# import pandas as pd
# from scipy import stats
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
domain=np.linspace(0,900,100)
pdf_norm = norm.pdf(domain, loc=400, scale=300)*20000
x=list(pdf_norm)

print('la matrice est ',pdf_norm)

#data_norm = norm.rvs(size=100, loc=10, scale=3)
#Y=plt.hist(data_norm, bins=30)
for z in pdf_norm :
    print(z)
plt.plot(domain,pdf_norm)
plt.show()
