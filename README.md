# API-system-for-Cinema
using FastAPI to build API which can communicate to database. In here, I am using MySQL

There are some simple APIs for cinema system:
  1. Get information of cinema
      - input: name of the city, in which you want to search what cinema in it
      - output: list of cinema in this city
  2. Get list film in cinema in one day
      - input: None
      - output: list film in cinema
  3. Get film detail
      - input: film id
      - output: detail of this film
  4. Get list schedule of the film
      - input: film id
      - output: list schedule of this film in one day
  5. Get list free chair
      - input: schedule id
      - output: list free chair in this schedule
  6. Get account ID
      - input: an object in modelAccount, its attributes are: username and password
      - output: account ID of this account
  7. Book ticket
       - input: an object in model (accountID: int, ScheduleID: int, ChairID: list)
       - output: information of this ticket which you've booked
       - in this API, it can validate id chair, if it is correct in room of the schedule, user can not 
         book this chair.
         
  8. Cancel booking
      - input: order ID
      - output: cancel the order you booked
      
  9. Get transaction history
      - input: None
      - output: transaction history
      
  10. Get information of a movie
      - input: film ID
      - output: information of this movie. it includes type of film, duration, title, release date, 
                release date, cast, rated
                
  11. Get chair
       - input: room ID
       - output: list chair in this room
