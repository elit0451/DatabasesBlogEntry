<h5 align="right">11.12.2019</h5>
<hr><h1 align="center">:page_with_curl: Restructuring MongoDB for performance :page_with_curl:</h1>
<h3 align="right">Semester assignment of <em>"Investigation & reporting (UFO)"</em> course</h3>
</br>

Picking the wrong schema for MongoDB can significantly decrease query performance. This becomes an issue when applications require large amounts of data to be aggregated and integrated in a fast manner. By designing the schema in accordance with the querying needs of the domain, execution time will drop to the point it is close to instantaneous. By crafting a schema in this manner, developers can be certain to achieve best database performance, therefore, making their applications much more responsive when requesting data.

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
The aim of this blogpost is to sensitize the entire community of developers who use MongoDB as their persistence layer. We were inspired to improve a final project based on the critique provided during its examination. The complete source code and documentation of our results can be found in [Github](https://github.com/elit0451/GutenbergProject). 

The domain for this blogpost was a selection of books containing a title and an author, as well as a list of cities including their name and their geographical coordinates. The resources we have used to supply this domain were the [Gutenberg archive](http://www.gutenberg.org) of English books and [GeoNames](http://download.geonames.org/export/dump/) for the cities data.

During the examination, based on the previously recorded performance data, our attention was drawn to a specific query which was taking far too long to execute within MongoDB. 

In the underlying sections, we present how we moved away from a separate collection approach and embraced a nested collection instead, in order to bring up optimal performance for our domain and correct the query's abnormal response time.

</br>

---
<a name="problem"></a>
## Problem statement :rotating_light:
The pre-formulated search query which originated this investigation was:  
_"Given an author name list all books written by that author, as well as all the cities mentioned within the books' content."_

The first schema approach we took was a divided collection model, one for the books and another for the geospatial data accommodating thousands of records in each of them, which lead to our poor performance results.

The previous paragraph depicts the main bottleneck we had, which is demonstrated through the execution times shown by MongoDB. Depending on the data, some of the times the query was executed could take up to 30 seconds, which is far too long for any user to wait for data.

This was the problem we tackled and experimented with, so we could present some arguments about why it is important to analyse the domain beforehand and comprehend which queries will be executed within.

</br>

---
<a name="investigation"></a>
## Investigation :mag_right:
We started our investigation phase by having a closer look at our previously developed database schema, which is represented in the figure below. There we could observe that the **Books collection** has a title and author text attributes, together with an array of city names. In order to correlate the geographical coordinates with a city, a lookup had to be done between the 2 collections.   

<p align="center">
<img src="https://user-images.githubusercontent.com/21998037/70529413-c5e9f800-1b50-11ea-8d17-ecd8d71d01a5.png"></p>
<p align="center">
<em>Separate collections schema</em>
</p>

We noticed that only the `geodata` collection had indexes associated with it (marked in **red** on the schema above). From the competences we gained during a Database course, we knew indexes could speed up lookup times by reducing the number of processed documents. Therefore, our experiment was to add an index to the author field in the `books` collection, since that was a significant field for the investigated query. At this moment we ran several performance tests against our experiment and verified that the timings presented within had suffered no major changes. We did, however, see a reduction of the documents processed from _36 263_ to _39_. 

</br>

The previous statement was based on the query below:

<details><summary>Initial query stage</summary>
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

</br>

Since adding an index lead to intangible results, we were exposed to the idea that we need to dig deeper in order to deal with the undesirable performance.
A resource we often referred to for inspiration was the [MongoDB documentation website](https://docs.mongodb.com). What also helped us advance was going through a [developer course dedicated to MongoDB](https://www.linkedin.com/learning/learning-mongodb/replication-and-sharding?u=57077785) in the _Linkedin Learning platform_, where we got to refresh all our knowledge about this database engine. 

We were using the isolated environment of Mongo Client and its native profiling tool for performance results, however, we have developed a specific application for the books’ processing and importation processes into the specified collection(s). This step helped us to reduce the time gap between investigation iterations.

Our final endeavour was to remake the schema from including a different collection by reference, to embedding all the relevant data into one big collection. Running the profiler against this new method, revealed a significant drop in execution time.

The newly designed schema model, followed by the modified query look is presented below. Changing the schema also reduced the complexity of the used query.

<p align="center">
<img src="https://user-images.githubusercontent.com/21998037/70529664-68a27680-1b51-11ea-911d-c63dbfaf4cbb.png" width=20%></p>
<p align="center">
<em>Nested collection schema</em>
</p>
  
<details><summary>Final query stage</summary>
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

</br>

---
<a name="findings"></a>
## Findings :bellhop_bell:
The last step from our investigation phase yielded the most jaw-dropping results. With a simple change to how our schema was constructed, we managed to reduce the timings from ~30 seconds to some mere milliseconds. Since no relation between collections had to be made the performance hit its peek status. 

As it can be seen below we managed to develop from a linear dependency to a constant one.  
<img width="797" src="https://user-images.githubusercontent.com/21998037/69785702-00e74580-11b9-11ea-9e05-d273d41291d0.png">

On the first graph, the connection between the number of lookups and the amount of cities a text references is depicted. Following up, we are presenting a box-plot graphic that represents the timings taken before and after altering the schema (all measurements were recorded by executing the query 20 times with indexes applied).

<img src="https://user-images.githubusercontent.com/21998037/69785636-d4cbc480-11b8-11ea-91d6-e34fe1139615.png"> 

Our curiosity and experience provoked us to evaluate the efficiency of our new schema after taking advantage of text indexes. Taking into consideration the immense amount of documents the chosen database engine had to evaluate against the executed query, the application of indexes was a very valued resource (_i.e. from 36 263 documents processed, down to 39_).

By the end, we ended up with a sample application which exemplifies both approaches to schemas in a way which is convenient to reproduce. It helps to demonstrate our investigation and findings for all the readers who are willing to reproduce the results. Further instructions can be found in the [guidelines document](https://github.com/elit0451/DatabasesBlogEntry/blob/master/Guidelines.md).

</br>

---
<a name="end"></a>
## Conclusion :checkered_flag:
As a result of the investigation period and all our findings, we can conclude that in order to improve the efficiency of our query we had to change a very basic component - the database schema. We have agreed that by the early stages of our exam  project, not enough effort was put into projecting a valid and efficient schema due to the wrong assumption that indexes would compensate for it. By using the knowledge gathered from different reliable sources, and taking the time to apply it, we have designed an optimal schema for our specific use case which reflected on the performance by making the query execution time almost instant.

</br>

---
<a name="reflection"></a>
## Perspectivation :crystal_ball:
As an overall retrospective, we have reached the consensus that taking the extra time to analyse your domain and think about the types of data you want to retrieve, will lead to better design early on. Having a good design is very important since it is the foundation of your entire data structure. From there on you can apply the best practices and achieve maximum performance for your applications.

It should also be pointed out that it is good to test your applications with as much data as possible in advance, in order to spot any bottlenecks that might stop you from a flawless scalability plan down the line. In our specific case, having thousands of book records in connection with thousands of cities was what revealed our implementation disadvantages when it came to relating data between the two collections.

With all this said, by the end of the day, experimenting with new visions and concepts of a problem can bring you to epiphanies and imaginative solutions that will improve the overall quality of your work. By having a proper data structure and following best practices, MongoDB can compete directly with other fast performant database engines.

</br>

___
> #### Blogpost made by:   
`David Alves 👨🏻‍💻 ` :octocat: [Github](https://github.com/davi7725) <br />
`Elitsa Marinovska 👩🏻‍💻 ` :octocat: [Github](https://github.com/elit0451) <br />
> Attending "Investigation & reporting (UFO)" course of Software Development bachelor's degree
