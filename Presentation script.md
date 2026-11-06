---
progetto: BDS-chiara
tipo: discorso della presentazione
lingua: inglese semplice
durata: circa 17 minuti
---

# Presentation script

*Inequalities in Youth Sports Participation in Italy: Gender, Family Background and Territory*

> About 2,300 words, ~17 minutes at a calm speed. Words in **bold** are the ones to stress. The time in brackets is a guide for each slide.

---

## 1 · Cover (20 s)

Good morning. My project is called *Inequalities in Youth Sports Participation in Italy*. I look at three things: **gender**, **family background** and **territory**. I use official data from ISTAT, and I compare them with a big data source, **OpenStreetMap**.

## 2 · Research question (40 s)

My question is simple: **who does sport among young Italians, who stops, and why?**

I look at three dimensions. First, **gender**: is the gap between boys and girls the same at every age? Second, **family background**: how much do the parents' education and money matter? Third, **territory**: is the gap between North and South explained by the number of sports facilities?

I also started from a personal idea: maybe young people stop doing sport because **school takes too much time**. ISTAT does not measure this directly, so I test it in an indirect way.

## 3 · Data (50 s)

I use five sources.

The main one is the ISTAT survey *Aspects of Daily Life*. I use eleven years, from 2014 to 2024: almost **490,000 people**. It is a **probability sample**, so every estimate uses the ISTAT sampling weights.

Second, the ISTAT tables on sport for 2024. They tell us **why** people do not do sport. This information is not in the microdata.

Then the big data side: **OpenStreetMap**, the free map made by volunteers. I count the sports facilities in each region, today and in every year since 2010.

Finally, the official ISTAT boundaries, to query the map region by region.

In this project, "young people" means **ages 11 to 24**.

## 4 · Method (50 s)

I followed the five steps of the **KDD process** that we saw in class.

First, **selection** of the data. Second, **pre-processing**: the variable names change from one year to another, so I had to harmonise eleven years of data. Third, **transformation**: for example, I built the highest level of education in each family. Fourth, **data mining**: regression, machine learning and clustering. Fifth, **interpretation**.

To check my work, I compared my estimate with the official one. For 2024 I get **37.7%** of people who do sport. ISTAT publishes **37.5%**. So the pipeline works.

## 5 · Trend (50 s)

Here is the first result. The method is simple: **weighted proportions with 95% confidence intervals**. Because of the weights, the sample is a bit less efficient, so I use the **Kish effective sample size**, about 33,000 people per year.

In ten years, participation goes up from **31.8% to 37.7%**. This is good news. But look at the two lines: they move together. Men are always about **10 points** above women, in 2014 and in 2024. The gap does not close.

You can also see the drop in **2021**, because of COVID.

## 6 · Age (50 s)

Now by age. I put together 2022, 2023 and 2024 to have bigger samples.

Sport is highest between **6 and 13 years old**. Then it goes down. But it goes down much faster for **girls**. At 11–13 the gap is 13 points. At **14–15 it is already 19 points**, and it stays there until 19.

So girls stop **earlier** and **faster** than boys. This is the "dropout curve" of my project.

## 7 · Reasons (50 s)

Why don't young people do sport? These data come from the ISTAT tables.

At 11–14, the main reason is **lack of interest**, 47%. Lack of time is 32%. But when young people start upper secondary school, **lack of time grows**: 43% at 15–17, and 49% at 20–24. It becomes as important as lack of interest.

This is the strongest clue for my school idea. But be careful: the table does not say **why** they have no time, and it also includes people who **never** did sport.

Facilities and cost are not the main problem: at most 11%.

## 8 · Regions (50 s)

Now territory. The same method: weighted proportions, with three years together for each region.

The difference is very big. In **Trentino-Alto Adige, 55%** of people do sport. In **Calabria, only 22%**. That is a gap of **33 points**, and the confidence intervals never overlap.

Almost every region improves since 2014, but the ranking stays the same. Calabria is the only region that goes down. In the South, about **half of the population is sedentary**.

## 9 · The model (60 s)

These are simple comparisons. But gender, family and territory are mixed together. To separate them, I use a **logistic regression**.

The outcome is: does the young person do sport, yes or no? I use the **survey weights**. And I use **robust standard errors clustered by household**, because brothers and sisters in the same family are similar, so they are not independent observations. The sample is 62,000 young people in 44,000 families.

The table shows the **odds ratios**. A value below one means less sport. Being a **girl**: 0.56, the odds are almost cut in half. Living in the **South**: 0.58. And the strongest effect is **family education**: when no adult in the family went beyond primary school, the odds ratio is **0.22**. All these effects are significant.

## 10 · Gender (50 s)

Odds ratios are not easy to read. So I transform the model into **predicted probabilities**: I give everybody the same region, the same family and the same year. Only sex and age change. The intervals come from **400 simulations** of the coefficients.

The gap grows from **12 points at 11–13** to almost **20 points at 18–19**: 65% of boys against 46% of girls. The interaction term is significant.

So girls do not do less sport because they live in different places or families. The gap is **still there** after we control for these factors.

## 11 · Family and territory (50 s)

Same method for the other two dimensions.

**Family education** has the biggest effect: **71%** of young people do sport when there is a graduate in the family, only **37%** when nobody went beyond primary school. That is **34 points**.

The **South** is 13 points below the North-East, even with the same family background. So the territorial gap is not only about who lives there.

**Money** matters less than education: about **6 points** between families with good and scarce resources.

## 12 · The school hypothesis (60 s)

Now back to my first idea: does school take time away from sport?

The microdata have no direct measure of school pressure. The only related variable is **private remedial tutoring**, extra lessons to catch up at school.

I expected less sport with tutoring. The result is the **opposite**: young people with tutoring do **more** sport. Maybe it is just money? So I estimated **three nested models** on the same sample. When I add the region, and then family education and resources, the odds ratio goes down from **1.70 to 1.49**, but it stays above one. With tutoring, 69.5% do sport; without tutoring, 61.5%.

My interpretation: tutoring shows families that **invest more** in their children in general. So this proxy does **not** support my hypothesis. Together with the previous slide on reasons, I have **two clues that point in different directions**.

## 13 · OpenStreetMap (60 s)

Now the big data part. For each region I count the sports facilities in OpenStreetMap: pitches, sports centres, gyms, stadiums and tracks. I use the map as it was on **1 January 2024**, the same period as the survey.

The **correlation** with sport participation is **0.68**. The Spearman rank correlation, which is robust to outliers, is 0.60.

Then I estimate three small **OLS regressions** with **HC3 robust errors**, which work well with small samples. Facilities alone explain 46% of the differences between regions. The South alone explains 64%. Together, **84%**. But when I add facilities, the South gap only moves from **minus 13 to minus 11 points**. So facilities explain **less than one fifth** of the North–South gap.

These are only 20 regions, so I cannot say anything about single people.

## 14 · OpenStreetMap over time (60 s)

Is OpenStreetMap a good measure? I rebuilt the map **for every year** since 2010 with the **ohsome** service.

In ten years, the mapped facilities in Italy go from **38,000 to more than 100,000**: an index of **266**. Sport participation only goes to **119**. Real facilities do not grow that fast. So this growth shows the work of the **volunteers**, not new facilities.

The Centre and the South grow faster: they are still **catching up** on mapping.

Look at **Sardinia**: in one year, from 2014 to 2015, it goes from 1,700 to 4,700 facilities, and then it stops. This looks like a **bulk import**. Sardinia is simply mapped better.

And the change in OpenStreetMap is **not correlated** with the change in sport: r = 0.28, not significant. So OpenStreetMap can compare regions **at one moment**, but it cannot measure **change over time**.

## 15 · Supervised learning (50 s)

Now machine learning. First, **supervised learning**: can we predict who does sport?

I compared the logistic regression with two more complex models, **random forest** and **gradient boosting**. I trained them on 2014–2022 and tested them on **2023–2024**, like a statistical office would do with new data.

The result: all three models have the **same AUC, 0.67**. More complex models do not add anything. When the performance is the same, the **simple and interpretable model is better** for official statistics.

The most important variables are the same as before: family education, sex, age and region.

One warning: a model that predicts less sport for girls and for the South can **repeat these inequalities** if we use it to make decisions.

## 16 · Clustering (50 s)

Second, **unsupervised learning**. I grouped the 20 regions with **hierarchical clustering**, Ward method, on seven indicators.

With two groups, the result is only South against the rest. With three groups, we see a new difference inside the Centre-North: regions with **many facilities**, and regions with **more educated families but fewer facilities**. The third group is the **South**, with low participation and half of the people sedentary.

Notice **Sardinia** again: it is in the "many facilities" group only because of the OpenStreetMap import. A problem in the big data goes all the way into the final classification.

## 17 · Quality (50 s)

So, how good are the two sources? I used the **quality framework** from the course.

The ISTAT survey is better on **accuracy and precision**: there is a standard definition, and the error can be measured, about half a point.

OpenStreetMap is better on **timeliness and detail**: it is updated every minute, and it shows every single facility. But it is **not comparable over time**, and nobody is responsible for its completeness.

## 18 · Errors and challenges (40 s)

The main error of OpenStreetMap is **coverage**, an error of non-observation. We only see the facilities that a volunteer decided to map. It is a kind of **self-selection**, and it changes between regions and years.

I also met all **five challenges** from the course: technical, methodological, institutional, legal and educational. For example, the servers were down for hours, so I had to write scripts that try again automatically.

The solution would be to **validate** OpenStreetMap with an official census of sports facilities.

## 19 · Conclusions (50 s)

To conclude, three inequalities.

**Gender**: girls do less sport at every age, and the gap reaches 20 points at 18–19.

**Family background**: education is the strongest factor, stronger than money.

**Territory**: the South stays behind, even with the same families, and facilities explain only a small part.

About **school**, the evidence is **mixed**.

About **big data**: OpenStreetMap gives a new angle on territory, but it measures the volunteers as much as the facilities. Before official use, it must be **validated**.

## 20 · Limitations and next steps (30 s)

This study has limits. These are **associations, not causes**. The standard errors are approximate. And I have no direct measure of school pressure.

Next steps: validate OpenStreetMap with the official census of facilities, and use it to estimate sport in **small areas**. All the work is **reproducible**, with scripts and notebooks.

**Thank you.** I am happy to answer your questions.

---

## Possible questions, with short answers

- **Why Kish effective sample size?** — Weights make the sample less efficient. Kish tells us how many "equivalent" random observations we have, so the intervals are not too narrow.
- **Why clustered standard errors?** — People in the same family are similar. If we treat them as independent, the errors are too small.
- **Why not more complex models?** — I tried them: same AUC. With equal performance, the logit is easier to explain and to check.
- **Can OpenStreetMap replace the survey?** — No. It measures facilities, not people, and its coverage changes. It can be a useful extra variable after validation.
- **Is the North–South gap real or a data problem?** — In the survey it is real: the intervals never overlap. In OpenStreetMap, part of the gap can come from mapping.
