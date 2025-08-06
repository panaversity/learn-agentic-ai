# GQL DDL, DML, and DQL

Learning Resources:

[GQL: Schemas and Types](https://www.milowski.com/journal/entry/2024-06-26T12:00:00-07:00/)

[Draw Graph Diagrams](https://arrows.app/)

[Short Explaination of GQL](https://jtc1info.org/wp-content/uploads/2024/04/2024-Article-39075-Database-Language-GQL.docx.pdf)

[ISO GQL Pattern Language](https://tugraph-db.readthedocs.io/en/latest/8.query/2.gql.html)

[GQL Editor](https://opengql.github.io/editor/)

[Neo4j AuraDB](https://neo4j.com/cloud/)

[Build applications with Neo4j and Python](https://neo4j.com/docs/python-manual/current/)

[Python Project Management](https://github.com/astral-sh/uv)

In GQL (Graph Query Language), the ISO standard syntax 
for comments is the same as in many other programming 
languages. You use two forward slashes (//) for 
single-line comments or /* and */ for multi-line 
comments.




EduSmartSchema declared via phrases:

https://shorten.wilenskid.pl/cSKZv6

```gql
CREATE GRAPH TYPE EduSmartSchema AS {
   NODE :Program {
      name :: STRING NOT NULL,
      description :: STRING
   },
   NODE :Course {
      course_number :: STRING NOT NULL,
      name :: STRING NOT NULL,
      description :: STRING
   },
   3.
   NODE :Class {
      section_number :: STRING NOT NULL,
      start_date :: DATE NOT NULL,
      end_date :: DATE NOT NULL,
      class_days_of_week: STRING NOT NULL,
      class_time :: TIME NOT NULL,
      class_duration :: DURATION NOT NULL,
      lab_days_of_week: STRING NOT NULL,
      lab_time :: TIME NOT NULL,
      lab_duration :: DURATION NOT NULL,
   },
   DIRECTED EDGE scheduled {} CONNECTING (Course -> Class),
   NODE :Person {
      name :: STRING NOT NULL,
      url :: STRING,
      givenName :: STRING,
      familyName :: STRING NOT NULL,
      birthDate :: DATE NOT NULL
      signupDate :: DATETIME NOT NULL
   },
   NODE :Student => :Person {
    student_id :: STRING NOT NULL,
   } AS Student,
  DIRECTED EDGE admission {} CONNECTING (Student -> Program),
  DIRECTED EDGE registers {} CONNECTING (Student -> Class),
  
  NODE :Teacher => :Person {
    teacher_id :: STRING NOT NULL,
   } AS Teacher,

   DIRECTED EDGE teaches {} CONNECTING (Teacher -> Class),

  NODE :TextBook {
      title :: STRING NOT NULL,
      author_name :: STRING NOT NULL,
      description :: STRING
   },
   DIRECTED EDGE taught {} CONNECTING (Course -> TextBook),

  NODE :Topic {
      title :: STRING NOT NULL,
      url :: STRING,
      details :: STRING,
      lastReviewed :: STRING NOT NULL,
      creationDate :: DATE NOT NULL,
      sequenceNumber :: INT NOT NULL
   },

  DIRECTED EDGE contains {} CONNECTING (Topic -> TextBook),
  DIRECTED EDGE contains {} CONNECTING (Topic -> Topic),
  
  DIRECTED EDGE knows 
      { 
        level :: INT NOT NULL, 
        assesment_date :: DATETIME 
      } 
      CONNECTING (Student -> Topic),


     NODE :Interaction {
      title :: STRING NOT NULL,
      author_name :: STRING NOT NULL,
      description :: STRING,
    },

    DIRECTED EDGE covers {} CONNECTING (Interaction -> Topic),

}


```

https://shorten.wilenskid.pl/fVVbWE
```gql
/* Insert nodes */
INSERT (:Program {name: 'Certified Generative AI Engineer', description: 'This is Agentic and Physical AI Program'})

INSERT (:Course {course_number: 'ai-101', name: 'Python AI', description: 'Coding Python using AI'})

MATCH (p : Program {name: 'Certified Generative AI Engineer'})
 ,(c : Course {course_number: 'ai-101'})
INSERT (p)-[:contains]->(c)

/* Insert two nodes and an edge */
INSERT (:Program {name: 'AI', description: 'AI Program' })
 -[:contains {}]->
 (:Course {course_number: 'ai-201', name: 'Generative AI', description: 'Coding in Generative AI'})

 ```




