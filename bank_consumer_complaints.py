from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
from datetime import datetime
from dateutil.parser import parse
import scipy
from scipy import stats


consumerdata = pd.read_csv("Consumer_Complaints.csv")

columns = list(consumerdata)

consumerdata.groupby("Company").size() #there are lots of smaller companies, so I would like to index just the top 5 banks"

bools = []

for each in consumerdata["Company"]:
    if "citibank" in each.lower():
        bools.append(True)
    elif "jpmorgan" in each.lower():
        bools.append(True)
    elif "bank of america" in each.lower():
        bools.append(True)
    elif "goldman sachs" in each.lower():
        bools.append(True)
    elif "wells fargo" in each.lower():
        bools.append(True)
    else:
        bools.append(False)

s = Series(bools)
#https://www.consumerfinance.gov/complaint/data-use/
top5frame = consumerdata[s.values]

timelyornot = top5frame.groupby(["Company", "Timely response?"]).size().unstack()

#"How Quickly Does Each Bank Response To Complaints?"
# print timelyornot
#Making a stacked barchart with my data
timelyornot = top5frame.groupby(["Company", "Timely response?"]).size().unstack()

timelyornot.plot(kind = "barh", stacked = True)

plt.title("How Quickly Does Each Bank Respond To Complaints?")
plt.ylabel("Bank")
plt.xlabel("Number of Complaints")
plt.show()


#calculate a percentage of issues and whether they were timely or not for each bank
totalcomplaints = timelyornot.No + timelyornot.Yes
pct = timelyornot.No / totalcomplaints
timelyornot["pct"] = pct

timelyornot.plot(kind = "barh", y = "pct", color = "y", legend = False)
plt.ylabel("Bank")
plt.xlabel("% Of Complaints That Were Responded To Slowly")
plt.title("What Percentage Of Complaints Are Responded To Slowly?")
plt.show()

#Top 5 States with the most complaints
#which companies get disputed the most?
# pct disputed timely vs. untimely, perhaps improve by being timely

#We want to see whethermany of the responses were disputed, meaning customers were not happy
disputedframe = top5frame.groupby(["Company", "Consumer disputed?"]).size().unstack()
disputedframe.plot(kind = "bar", stacked = True)
plt.xlabel("Bank")
plt.ylabel("Total # of complaints")
plt.title("Are Many Company Responses Disputed by Customers?")
plt.show()


total = disputedframe.No + disputedframe.Yes
pctdis = disputedframe.Yes / total
disputedframe["pct"] = pctdis
disputedframe.pct.plot(kind = "barh", color = "r")
plt.ylabel("Bank")
plt.xlabel("% of responses disputed")
plt.title("Percentage of Company Responses Disputed by Customers")
plt.show()

#not a dig difference!

#Now, we are curious about whether being timey vs untimely changes the percent of unhappy customers
#our hypothesis is that untimely groups will have higher percent of disputed claims

#TRY USING APPLY
grouped5 = top5frame.groupby(["Company", "Timely response?", "Consumer disputed?"]).size().unstack()
total = grouped5.No + grouped5.Yes
groupedpct = grouped5.No + grouped5.Yes
groupedpct = grouped5.Yes / groupedpct
grouped5["pct"] = groupedpct

grouped5["pct"].unstack().plot(kind = "bar")

plt.xlabel("Bank")
plt.ylabel("% of responses disputed")
plt.title("Percentage of Company Responses Disputed for Timely and Untimely Responses")
plt.show()

#actually our hypothesis was incorrect! It appears timely responses actually have a higher percentage of dispute, so these variables appear to be unrelated


#if they closed without relief, is it more likely to be diputed? Percentage of dispute for relief vs. non relief
typeofclosure = []

for each in top5frame["Company response to consumer"]:
    if "closed with explanation" in each.lower():
        typeofclosure.append("Explanation")
    elif "with monetary relief" in each.lower():
        typeofclosure.append("$ Relief")
    else:
        typeofclosure.append("Other")

top5frame["Response"] = typeofclosure

responsedisputed = top5frame.groupby(["Response", "Consumer disputed?"]).size().unstack()
tots = responsedisputed.No + responsedisputed.Yes
pctdisputed = responsedisputed.Yes / tots
responsedisputed["Pct"] = pctdisputed

responsedisputed.plot(kind = "bar", y = "Pct", color = ["g", "r", "b"], legend = False)
plt.xlabel("Type of Response from Bank")
plt.ylabel("% disputed")
plt.title("Percentage of Company Responses Disputed for Different Bank Responses")
plt.show()

#When only given an explanation (and not monetary compensation), the frequency of dispute is 2X!



#plot total number of complaints by month

monthlist = [int(each[0:2]) for each in top5frame["Date sent to company"]]
top5frame["month"] = monthlist

monthdict = {1:"January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

top5frame["monthname"] = top5frame["month"].map(monthdict)

top5frame.groupby("month").size().plot(kind = "line", style = "--bo", xticks = [1,2,3,4,5,6,7,8,9,10,11,12])

plt.xlabel("Month")
plt.ylabel("# of Complaints")
plt.title("Complaints per Month")
plt.show()

#as we can see, complaints take a drop at the end of the year

top5frame.groupby(["month", "Consumer disputed?"]).size().unstack().plot(kind = "line", style =[ "--bo", "--yo"])


plt.xlabel("Month")
plt.ylabel("# of Complaints")
plt.title("Complaints per Month")
plt.show()

#boxplot of complaints per month

#We can also see how things change for disputed and undisputed


top5frame.groupby(["month", "Company"]).size().unstack().plot(kind = "line", style = ["--ro", "--o", "--go", "--bo", "--yo"]) #by company
plt.xlabel("Month")
plt.ylabel("# of Complaints")
plt.title("Complaints per Month For Top 5 Banks")
plt.legend(loc="best", prop = {"size":4})
plt.show()


#next, for each company, lets see how the compaints have changed over time
#5 lines, plot one using a timeseries for each bank
#SUPER MESSY, so we focus on smaller timeframes to learn something about complaint behavior

top5frame = top5frame.rename(columns = {"Date sent to company": "date_sent"})
dater = []
for each in top5frame["date_sent"]:
    dater.append(parse(each))
top5frame["date_time"] = dater

top5frame.groupby(["date_time", "Company"]).size().unstack().plot(kind = "line")
plt.xlabel("Year")
plt.ylabel("# of Complaints")
plt.title("Complaints Over Time for Top 5 Banks")
plt.legend(loc="best", prop = {"size":5})
plt.show()


#lets zoom on 2012:
top5frame.groupby(["date_time", "Company"]).size().unstack().plot(kind= "line",xlim = (parse("1/1/2012"), parse("12/31/2012")))
plt.xlabel("Month")
plt.ylabel("# of Complaints")
plt.title("Complaints Over Time for Top 5 Banks")
plt.legend(loc="best", prop = {"size":5})
plt.show()

#now 2016

top5frame.groupby(["date_time", "Company"]).size().unstack().plot(kind= "line",xlim = (parse("1/1/2016"), parse("12/31/2016")))
plt.xlabel("Month")
plt.ylabel("# of Complaints")
plt.title("Complaints Over Time for Top 5 Banks")
plt.legend(loc="best", prop = {"size":5})
plt.show()

#Now we see it goes up and down, and some days tend to have no complaints. Lets choose a month and check out weekly complaint patters:

top5frame.groupby(["date_time", "Company"]).size().unstack().plot(kind= "line",xlim = (parse("12/1/2016"), parse("12/31/2016")))
plt.xlabel("Day")
plt.ylabel("# of Complaints")
plt.title("Complaints Over Time for Top 5 Banks")
plt.legend(loc="best", prop = {"size":5})
plt.show()

#WE CAN SEE A DISTINCT PATTERS WHERE COMPLAINTS PEEK ON/NEAR WEDNESDAY, AND FALL AT END OF THE WEEK
#by state
top5frame.groupby(["date_time", "Company"]).size().unstack().plot(kind= "line",xlim = (parse("12/18/2016"), parse("12/25/2016")))
plt.xlabel("Day")
plt.ylabel("# of Complaints")
plt.title("Complaints Over Time for Top 5 Banks")
plt.legend(loc="best", prop = {"size":5})
plt.show()

daydict = {6:"Sunday", 0: "Monday", 1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday"}
daylist = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daylist1 = [each.weekday() for each in top5frame.date_time]
top5frame["day_num"] = daylist1
top5frame["day_of_week"] = top5frame["day_num"].map(daydict)
dayplot = top5frame.groupby("day_num").size().plot(kind = "line", style = "--bo")
dayplot.set_xticklabels(daylist)
plt.xlabel("Day of Week")
plt.ylabel("Total # of Complaints")
plt.title("Complaints on Different Days from Top 5 Banks")
plt.show()



#lets check on which states have a lot of complaints
top5frame.groupby("State").size().sort_values()[-10:].plot(kind="barh")

plt.xlabel("Total Complaints")
plt.title("Complaints By State")
plt.show()

print "Next, we will run some statistical tests to see which variables are related. Because we are looking at relationships between discrete variables, we will use Chi-Squared test of independence."
print ""

print "First, lets test if there is a relationship between bank type and whether consumers disputed the complaint response"
print ""
print "Our null hypothesis is that there is no relationship between our two variables"
print "We will test at 1% significance level"

bank_disputed_cross = pd.crosstab(index = top5frame["Consumer disputed?"], columns = top5frame["Company"], dropna = True)
print bank_disputed_cross
print bank_disputed_cross.apply(lambda r: r/r.sum(), axis=0)

#Now with percentages


#
c_t_val, p_val, dof, e_table = scipy.stats.chi2_contingency(bank_disputed_cross)
#
print p_val
print ""
print "Our p-value is well below our significance value, so we reject our null hypothesis and conclude that the banks are not the same when it comes to disputed consumer complaints"
print ""

disputed_timely_cross = pd.crosstab(index = top5frame["Consumer disputed?"], columns = top5frame["Timely response?"], dropna = True)
print ""
print "lets check is being timely and getting disputed is related"
print ""
print disputed_timely_cross.apply(lambda x: x/x.sum(), axis = 0)
print ""
c, p, dof, e = scipy.stats.chi2_contingency(disputed_timely_cross)
print ""
print p
print ""
print "small p value reveals there is a relationship between timeliness and whether the complaints are disputed."
print ""
print "Banks -- be timely and you will have less complaints!"




