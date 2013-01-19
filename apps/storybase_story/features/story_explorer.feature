Feature: Users can browse stories

    Scenario: Test scenario
        Given the following organizations have been created:
            | name                   |
            | The Piton Foundation   |
            | The Denver Foundation  |
            | Urban Land Conservancy |

        Given the following geolevels have been created:
            | name         | slug         | parent_slug  |
            | State        | state        |              |
            | County       | county       | state        |
            | City         | city         | county       |
            | Neighborhood | neighborhood | city         |
            | Zip Code     | zip-code     | neighborhood |

        Given the following places have been created:
            | name               | geolevel_slug |
            | Colorado           | state         |
            | Green Valley Ranch | neighborhood  |
            | Montbello          | neighborhood  |
            | Park Hill          | neighborhood  |

        Given the following locations have been created:
            | name                       | address                    | address2 |  city       | state | postcode | 
            | Hinkley High School        | 1250 Chambers Road         |          | Aurora      | CO    | 80011    |
            | East 33rd Ave and Holly St | East 33rd Ave and Holly St |          | Denver      | CO    |          |
            | Urban Land Conservancy     | 305 Park Avenue            |          | West Denver | CO    | 80205    |

        Given the following stories have been created:
            | title | summary | byline | organizations | projects | topics | places | locations | 
            | TCAP Reading Results Reveal Trends | <p>Nearly three-fourths of Colorado third-graders are reading at grade level, a slight increase that matches the highest proficiency mark achieved in the past ten years, according to results released Wednesday.</p><p>Results of the first administration of the Transitional Colorado Assessment Program, which is replacing the Colorado Student Assessment Program as the state shifts to new academic standards, show 73.9 percent of third-graders scored proficient or advanced.</p><p>Proficiency rates have hovered between 70 and 74 percent since at least 2003.</p><p>That leaves 25 percent of the state’s third-graders – more than 16,000 mostly 9-year-olds – struggling to master basic literacy skills.</p> | Nancy Mitchell, EdNewsColorado.org | | | Education | Colorado | |
            | Reform Schools in Far Northeast Show Growth in Third-Grade Reading | <p>Standardized test scores are in, and preliminary results show that in Far Northeast Denver, two elementary schools that were part of another controversial reform plan approved in 2011 saw gains.</p><p>Both Green Valley and McGlone elementaries saw 17-point increases in third-grade reading proficiency over last year.  Reform efforts at those schools included the requirement that teachers reapply for their jobs this past fall.</p> | Jennifer Newcome, The Piton Foundation | The Piton Foundation | | Education | Green Valley Ranch, Montbello | |
            | Taking Action After a Schoolyard Fight | When two Hinkley High students got in a fight, their mothers ended up talking. Instead of pointing fingers, they decided to take action. Now, parents and students are changing the culture of their school from the inside out. | Gabriela Jacobo | The Denver Foundation | Restorative Justice at Hinkley High School | Education | | Hinkley High School |
            | The Holly: Redesigning Park Hill | This is the story of a shopping center that burned to the ground. Formerly a blemish, it's now being redeveloped as a community asset in Park Hill with input from residents. | Urban Land Conservancy | Urban Land Conservancy | | | Park Hill | East 33rd Ave and Holly St, Urban Land Conservancy |
