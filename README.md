<h5 align="right">28.11.2019</h5>
<hr><h1 align="center">:page_with_curl: Restructuring Mongo DB for performance :page_with_curl:</h1>
<h3 align="right">Semester assignment of <em>"Investigation & reporting (UFO)"</em> course</h3>
</br>

Picking the wrong schema for Mongo DB can significantly decrease query performance. This becomes an issue when applications require large amounts of data to be aggregated and integrated in a fast manner. By designing the schema in accordance with the querying needs of the domain, execution time will drop to the point it is close to instantaneous. By crafting a schema in this manner, developers can be certain to achieve best database performance, therefore, making their applications much more responsive when requesting data.

</br>

---
<a name="toc"></a>
## Table of Contents <img src="https://user-images.githubusercontent.com/21998037/69780340-47ce3e80-11ab-11ea-9704-41304f605668.png" align="center" height="45"> 
* [Introduction](#intro)
* [Problem statement](#problem)
* [Investigation](#investigation)
* [Findings](#findings)
* [Conclusion](#end)
* [Perspectivation](#reflection)

</br>

---
<a name="intro"></a>
## Introduction <img src="https://user-images.githubusercontent.com/21998037/69781481-96310c80-11ae-11ea-8f6b-0ac987d1d559.png" align="center" height="45"> 
The aim of this blogpost is to sensitize the entire community of developers who use Mongo DB as their persistence layer. We are two very passionate Software Development students who had a Database course as part of the education and were inspired to improve our final project based on the critique provided during the examination for this course. The complete source code and documentation of our results can be found in [Github](https://github.com/elit0451/GutenbergProject). 

Our semester project was named “Gutenberg project” since our main resources were English books [Gutenberg archive](http://www.gutenberg.org). The [main objective](https://github.com/datsoftlyngby/soft2019spring-databases/blob/master/Exam/GutenbergProject.md) was to develop an application which would connect to two databases and execute a number of pre-formulated search criteria. Additionally, we needed to measure the performance of each database in order to draw conclusions on which would fit this domain the best.

At the point when we were recording performance data, we noticed a huge discrepancy between Mongo DB and Neo4j when it came to the third query response time. This led us to believe something was amiss and we decided to dedicate our efforts to investigate the root cause of such gap.

In the underlying sections, we present how we moved away from a separate collection approach and embraced a nested collection instead, in order to bring us optimal performance for our domain and correct the third query abnormal response time. 

</br>

---
<a name="problem"></a>
## Problem statement :rotating_light:
The first schema approach we took was a divided collection model, one for the books and another for the geospatial data, which lead to our bad performance results regarding the third query defined in the project. 

The previous paragraph depicts the main bottleneck we had in our application which is demonstrated through the execution times shown by Mongo DB. Depending on the data, some queries could take up to 30 seconds, which is far too long for any user to wait for data.

This was the problem we tackled and experimented with, so we could present some arguments about why it is important to analyse the domain beforehand and comprehend which queries will be executed within.

</br>

---
<a name="investigation"></a>
## Investigation :mag_right:
We started our investigation phase by having a closer look at our previously developed application logic and noticed that only the `geodata` collection had indexes associated with it. From the competences we gained during the Database course, we knew indexes could speed up the lookup times when executing a query. Therefore, our experiment was to add an index to the author field in the `books` collection, since that was a significant field for query three. At this moment we launched our application again and verified that the timings presented within had suffered no changes. The used query three for the previous statement can be seen below:

<details><summary>Query three (initial stage)</summary>
</br>

```javascript
db.books.aggregate(
  {
      "$match":{"$text": { "$search": authorName}}
  },
  {
      "$project":
      {
          "title": 1,
          "cities": 1,
          "_id": 0
      }
  })
```
</details>

The next thing we noticed was that our query three was heavily dependant on the execution of query two through the code. With this new knowledge, we set our minds to make query three fully independent with the hope that the reduced amount of calls would lead to faster performance. The final look of it was:

<details><summary>Query three (final stage)</summary>
</br>

```javascript
db.books.aggregate(
  {
      "$match":{"$text": { "$search": authorName}}
  },
  {
      "$unwind": "$cities"
  },
  {
      "$lookup":
      {
          "from": "geodata",
          "localField": "cities",
          "foreignField": "city",
          "as": "cityCoordinates"
      }
  },
  {
      "$project":
      {
          "title": 1,
          "cities": 1,
          "location": { "$arrayElemAt": ["$cityCoordinates.location", 0] },
          "_id": 0
      }
  })
```
</details>

After refactoring the python code to use the new autonomous query implementation, performance testing followed but once again lead to intangible results. This exposed us to the idea that we need to dig deeper in order to deal with this undesirable performance.
A resource we often referred to for inspiration was the [Mongo DB documentation website](https://docs.mongodb.com). What also helped us advance was going through a [developer course dedicated to Mongo DB](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=2ahUKEwifo8-q4YrmAhXFEVAKHQ0NA7YQFjAAegQIARAB&url=https%3A%2F%2Fwww.linkedin.com%2Flearning%2Flearning-mongodb&usg=AOvVaw3Hw1l5uoD4HATak9S7Xbec) in the _Linkedin Learning platform_, where we got to refresh all our knowledge about this database engine. 

So far we had been using the application itself for performance measurements, which might not fully reflect the actual timing. It was also adding a layer of complexity while meddling around with different changes to the database, therefore we shifted to the isolated environment of Mongo Client and its native profiling tool. We kept, however, the application's involvement in the books’ processing and importation processes into the specified collection(s).

Our final endeavour was to remake the schema from including a different collection by reference, to embedding all the relevant data into one big collection. Running the profiler against this new method, revealed a significant drop in execution time.

</br>

---
<a name="findings"></a>
## Findings :bellhop_bell:
The last step from our investigation phase yielded the most jaw-dropping results. With a simple change to how our schema was constructed, we managed to reduce the timings from ~30 seconds to some mere milliseconds. We found out that after redesigning the schema our initial query worked perfectly fine without any dependencies. This resulted in only one call directed to the database and since no relation between collections had to be made the performance hit its peek status. 

As it can be seen below we managed to develop from a linear dependency to a constant one. 
<img width="795" alt="Screenshot 2019-11-28 06 02 48" src="https://user-images.githubusercontent.com/21998037/69785688-f6c54700-11b8-11ea-868e-96b985a31746.png">
<img width="797" alt="Screenshot 2019-11-28 06 03 59" src="https://user-images.githubusercontent.com/21998037/69785702-00e74580-11b9-11ea-9e05-d273d41291d0.png">

On the first graph, we are relating the number of calls our application had to make to the database with the number of books that were returned for a certain author. Besides it, stands a graph which depicts the connection between the number of lookups and the amount of cities a text references. Following up, we are presenting a box-plot graphic that represents the timings taken before and after altering the schema (all measurements were recorded with indexes applied).

<img src="https://user-images.githubusercontent.com/21998037/69785636-d4cbc480-11b8-11ea-91d6-e34fe1139615.png"> 

Our curiosity and experience provoked us to evaluate the efficiency of our new schema after taking advantage of text indexes. Taking into consideration the immense amount of documents the chosen database engine had to evaluate against the executed query, the application of indexes was a very valued resource (_i.e. from 36 263 documents processed to 39_).

By the end, we ended up with a sample application which exemplifies both approaches to schemas in a way which is convenient to reproduce. It helps to demonstrate our investigation and findings for all the readers who are willing to reproduce the results. Further instructions can be found in the [guidelines document](https://github.com/elit0451/DatabasesBlogEntry/blob/master/Guidelines.md).

</br>

---
<a name="end"></a>
## Conclusion :checkered_flag:
As a result of the investigation period and all our findings, we can conclude that in order to improve the efficiency of query number three we had to change a very basic component - the database schema. We have agreed that by the early stages of the Gutenberg project, not enough effort was put into projecting a valid and efficient schema due to the wrong assumption that indexes would compensate for it. By using the knowledge gathered from different reliable sources, and taking the time to apply it, we have designed an optimal schema for our specific use case which reflected on the performance by making the query execution time almost instant.

</br>

---
<a name="reflection"></a>
## Perspectivation :crystal_ball:
As an overall retrospective, we have reached the consensus that taking the extra time to analyse your domain and think about the types of data you want to retrieve, will lead to better design early on. Having a good design is very important since it is the foundation of your entire data structure. From there on you can apply the best practices and achieve maximum performance for your applications.

It should also be pointed out that it is good to test your applications with as much data as possible in advance, in order to spot any bottlenecks that might stop you from a flawless scalability plan down the line. In our specific case, having thousands of book records in connection with thousands of cities was what revealed our implementation disadvantages when it came to relating data between the two collections.

With all this said, by the end of the day, experimenting with new visions and concepts of a problem can bring you to epiphanies and imaginative solutions that will improve the overall quality of your work. By having a proper data structure and following best practices, Mongo DB can compete directly with a fast performant graph database like Neo4j.

</br>

___
> #### Assignment made by:   
`David Alves 👨🏻‍💻 ` :octocat: [Github](https://github.com/davi7725) <br />
`Elitsa Marinovska 👩🏻‍💻 ` :octocat: [Github](https://github.com/elit0451) <br />
> Attending "Investigation & reporting (UFO)" course of Software Development bachelor's degree
