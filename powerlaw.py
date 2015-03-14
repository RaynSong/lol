########import packages, set path, read excel file##########
import sys
sys.path.insert(0,"/Library/Python/2.7/site-packages/xlrd-0.9.3-py2.7.egg")    #insert xlrd path into python reading path
sys.path.insert(0, "/Library/Python/2.7/site-packages/powerlaw-1.3.1-py2.7.egg")
sys.path.insert(0,"/Library/Python/2.7/site-packages/pymc-2.3.4-py2.7")
import powerlaw
import numpy as np
import matplotlib.pyplot as plt
import pylab
from pylab import *
import math
from matplotlib import rc
from pylab import *
rc('text',usetex=True)
import xlrd
file_location = "Desktop/Research/N2403_MIPS24_extract_MOPEX.xlsx" #identify location of the #excel file
workbook=xlrd.open_workbook(file_location) # open the workbook specified by the #file_location
sheet = workbook.sheet_by_index(2)

########import all data #########
ir=[]
for r in range(0,2918):
  ir.append(sheet.cell_value(r,5))


#get fitting information from {powerlaw package}
fit=powerlaw.Fit(ir,xmin=min(ir),xmax=max(ir))
x,prob=fit.ccdf(ir)
#print len(x)  #how many catogories

#make a reversible list copy of x for later use#
x_re=[]
for n  in range(0,len(x)):
    x_re.append(x[len(x)-1-n])

#find where the break point correspond to
global break_pt
def chi_total(num):
    for n in range(0, len(x)):
         if (x_re[n]==ir[num]): #find the biggest index of the value equal to original break value
            break_pt = len(x)-1-n

    print "break_pt=",break_pt


    x1=np.array(x[:break_pt])
    prob1=np.array(prob[:break_pt])

    x2=np.array(x[break_pt:])
    prob2=np.array(prob[break_pt:])

#curve-fit
    print "For curve_fit:"
    from scipy.optimize import curve_fit

    def power(x,a,c):
        return c*(x**a)
   
    global ind,cons
    popt,pcov=curve_fit(power,x,prob)
    residual=prob-power(x,popt[0],popt[1])
    print "chi-sq=",sum(residual**2)
    ind=popt[0]
    print "index=",ind
    cons=popt[1]
    print "c=",cons
 
    global ind1,cons1
    popt1,pcov1=curve_fit(power,x1,prob1)
    residual1=prob1-power(x1,popt1[0],popt1[1])
    print "chi-sq1=",sum(residual1**2)
    ind1=popt1[0]
    print "index1=", ind1
    cons1=popt1[1]
    print "c=",cons1

    global ind2,cons2
    popt2,pcov2=curve_fit(power,x2,prob2)
    residual2=prob2-power(x2,popt2[0],popt2[1])
    print "chi-sq2=",sum(residual2**2)
    ind2=popt2[0]
    print "index2=", ind2
    cons2=popt2[1]
    print "c=",cons2
    
    curvefit_chisqr=sum(residual1**2)+sum(residual2**2)

#log log linear fit
    print "Log log linear fit:"
    global m,b
    m,b=polyfit(log(x),log(prob),1)
    print "m=",m
    print "b=",b
    res=prob-power(x,m,b)
    print "chi-sq=",sum(res**2)
    
    global m1,b1
    m1,b1=polyfit(log(x1),log(prob1),1)
    print"m1=",m1
    print"b1=",b1
    res1=prob1-power(x1,m1,b1)
    print "chi-sq1=",sum(res1**2)
    
    global m2,b2
    m2,b2=polyfit(log(x2),log(prob2),1)
    print"m2=",m2
    print"m3=",m2
    res2=prob2-power(x2,m2,b2)
    print "chi-sq=",sum(res2**2)
    
    linearfit_chisqr=sum(res1**2)+sum(res2**2)

    global chi_sqr
    if(linearfit_chisqr<=curvefit_chisqr):
         print "For ",num,"th value as break, least square is given by linear log log fit"
         chi_sqr=linearfit_chisqr
    else:
         print "For ",num,"th value as break, least square is given by curve fit"
         chi_sqr= curvefit_chisqr

    return ind,cons,ind1,cons1,ind2,cons2,m,b,m1,b1,m2,b2,linearfit_chisqr,curvefit_chisqr,chi_sqr
########locate break using least square on both sides########
total_chi=[] #total chi-sqr for before / after the break
break_candid=range(23,800)
for n in break_candid: #index of the value near break points
    total_chi.append(chi_total(n)[14])

final_parameters=[]
global index_in_ir
for val in total_chi:
    if val==min(total_chi):
        index_in_candid=total_chi.index(val)
        index_in_ir=break_candid[index_in_candid]
        print "the break is the ", index_in_ir,"th value is the break point"
        print "the break point flux is", ir[index_in_ir]
        print "the total chi square is",val
        final_parameters=chi_total(index_in_ir)
        if final_parameters[12]<=final_parameters[13]:
            print "use linear fit is better:"
            print "power index before break should be:",final_parameters[8]
            print "constant1 is",final_parameters[9]
            print "power index after break should be:",final_parameters[10]
            print "constant2 is",final_parameters[11]
        else:
            print "use curve fit is better:"
            print "power index before break should be:",final_parameters[2]
            print "constant1 is",final_parameters[3]
            print "power index after break should be:",final_parameters[4]
            print "constant2 is",final_parameters[5]

#####plot#######
plt.plot(x,prob,c='green')
plt.plot(x,(final_parameters[1])*(x**final_parameters[0]),c='green',linestyle='--')

plt.plot(x[:101],prob[:101],c='red')
plt.plot(x[:101],(final_parameters[3])*(x[:101]**final_parameters[2]),c='red',linestyle='--')
plt.plot(x[101:],prob[101:],c='blue')
plt.plot(x[101:],(final_parameters[5])*(x[101:]**final_parameters[4]),c='blue',linestyle='--')

#########Least Chi Square goodness of test##########
def least_chi_square():
    chi_2_before=0
    chi_2_after=0
    def before_break(x):
       return final_parameters[3]*(x**final_parameters[2])
    def after_break(x):
       return final_parameters[5]*(x**final_parameters[4])
    for n  in range(0,101):
       chi_2_before=chi_2_before+((x[n]-before_break(x[n]))**2)/before_break(x[n])
    chi_2_before=chi_2_before*2918
    for n in range(101,len(x)):
        chi_2_after=chi_2_after+((x[n]-after_break(x[n]))**2)/after_break(x[n])
    chi_2_after=chi_2_after*2918
    return chi_2_after+chi_2_before
    
print "total chi square is",least_chi_square()
print len(x)                                                                 
                                                                            
    
'''####K-S test for goodness of fit for ccdf fit calculated above (about -1)#####

#define indicator function
def indicatorsum (xvalue,array):
    indicator = 0
    for r in array:
        if (r >= xvalue):
           indicator=indicator+1
        else:
           indicator=indicator
    return indicator

#define the empirical distribution function Fn(x)
def fn (xvalue,array):
    n=2918  #total number of data
    return indicatorsum(xvalue,array)/n

#expected probablity according to calculated index
def f (xvalue, index):
    if index==m1 :
       return (math.exp(b1))*(xvalue**(index))
    elif index==m2:
       return (math.exp(b2))*(xvalue**(index))
    elif index==popt1[0]:
       return (popt1[1])*(xvalue**(index))
    elif index==p2[0]:
       return (popt2[1])*(xvalue**(index))
    else:
       print "input fail, index not right"

#define diffrence between fn and expected curve
def diff (xvalue,index,array):
   return abs(fn(xvalue,array)-f(xvalue,index))

#K-S statistic with 'div' divisions on range of x and power index 'index'
#higher div gives more precise result of dn
def dn(div,index,array):
   delta_x=(max(array)-min(array))/div
   xvalue=min(array)
   alldiff=[]
   while (xvalue<=max(array)):
        alldiff.append(diff(xvalue,index,array))
        xvalue=xvalue+delta_x
   return max(alldiff)

#finding the break point which gives the smallest dn on both side


#####execution of functions, trying to get small dn for both sides of the break######
#before break
print "dn_1=",dn(400,,ir[:1487])
#after break
print "dn_2=",dn(3600,chi_total(1487).popt2[0],ir[1487:])'''
######plot settings######
'''plt.legend([l1,l2],[r'$F_{6cm}<0.15 mJy$',r'$F_{6cm}>0.15 mJy$'],fontsize=12,loc=3)
plt.text(1.5,3.44,r'$y=0.002x+3.45$',fontsize=15,color='green',fontweight='bold')
plt.text(-1.9,1.52,r'$y=-0.16x+1.49$',fontsize=15,color='blue',fontweight='bold')
plt.text(-0.75,0.3,r'$y=-1.28x+0.52$',fontsize=15,color='green',fontweight='bold')'''
plt.annotate(r'break point flux = 0.195 mJy',xy=(0.199913,0.847649),xytext=(0.1,0.001),arrowprops=dict(arrowstyle="->"))
plt.text(0.1,0.0007,r'total $R^2=0.113$')
plt.xlabel(r'$(F_{24 \mu}/mJy)$',fontsize=20)
plt.ylabel(r'$P(((F_{24 \mu}/mJy)\geq F))$',fontsize=20)
plt.xscale('log')
plt.yscale('log')
plt.show()



