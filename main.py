import logging

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models

from database import SessionLocal


tag_metadata = []
app = FastAPI(title="API Cinema", description="this is a simple API", version="2.5.0", openapi_tags=tag_metadata)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# @app.get("/chairs/", description='this is an API using to get information of chair')
# def getChair(id: int, db: Session = Depends(get_db)):
#     # res = db.query(models.ChairModel).join(models.RoomModel).filter(models.RoomModel.id == id).all()
#     #
#     # if len(res) == 0:
#     #     return None
#     # return res
#     res = db.query(models.ChairModel).filter(models.ChairModel.id == id)
#     return res.all()


class model(BaseModel):
    accountID: int
    ScheduleID: int
    chairID: int


@app.get('/films', description=' this is an API using to return a list film', tags=['cinema'])
def get_List_Film(db: Session = Depends(get_db)):
    listVal = {}
    res = db.query(models.MovieInfo).all()
    i = 1
    for row in res:
        print(type(row))
        element = {}
        element['Title'] = row.title
        element['Type'] = row.typeFilm
        element['Duration'] = row.duration
        element['Release date'] = row.release_date
        listVal[i] = element
        i = i + 1
    return listVal


@app.get('/movie_detail', description='this is an API using to get film details', tags=['cinema'])
def get_Film_Detail(idFilm: int, db: Session = Depends(get_db)):
    res = db.query(models.MovieInfo).filter(models.MovieInfo.id == idFilm).all()
    if len(res) == 0:
        raise HTTPException(status_code=404, detail='CAN NOT FIND THIS FILM')
    return res


@app.get("/schedules/{idFilm}", description='this is an API using to return a list schedule of a film', tags=['cinema'])
def get_List_Schedule(idFilm: int, db: Session = Depends(get_db)):
    response = db.query(models.ScheduleInfo).filter(models.ScheduleInfo.movie_id == idFilm)
    if len(response.all()) == 0:
        raise HTTPException(status_code=404, detail='CAN NOT FIND THIS FILM')
    listDict = response.all()
    print(response.all())
    for i in range(len(response.all())):
        res = db.query(models.RoomModel).filter(models.RoomModel.id == listDict[i].room_id)
        query = db.query(models.CinemaInfo).filter(models.CinemaInfo.id == res.first().cinema_id)
        name = query.first().info
        element = listDict[i].__dict__
        element['cinema'] = name + ' ' + query.first().address
        listDict[i] = element
        print(type(listDict[i]))
    return listDict


@app.get('/chairs', tags=['cinema'])
def get_List_Free_Chair(idSchedule: int, db: Session = Depends(get_db)):
    res = db.query(models.ScheduleInfo).filter(models.ScheduleInfo.id == idSchedule)
    if len(res.all()) == 0:
        # return {'can not find this schedule'}
        raise HTTPException(status_code=404, detail='CAN NOT FIND THIS SCHEDULE')
    res1 = db.query(models.TicketInfo).filter(models.TicketInfo.schedule_id == idSchedule)
    listVal = {}
    pos = []
    for row in res1.all():
        print(type(row))
        print(row.__dict__['order_id'])
        res2 = db.query(models.OrderModel).filter(models.OrderModel.id == row.__dict__['order_id'])
        if res2.first().state == 'booking':
            pos.append(res2.first().id)

    arr = []
    for i in pos:
        res3 = db.query(models.TicketInfo).filter(models.TicketInfo.order_id == i)
        arr.append(res3.first().chair_id)
    i = 0
    for row1 in db.query(models.ChairModel).all():
        listVal[i] = row1.__dict__
        i = i + 1

    for j in arr:
        # res4 = db.query(models.ChairModel).filter(models.ChairModel.id == j).first()
        print(j, type(j))
        del listVal[j - 1]

    return listVal


@app.get("/cinemas", description='this is an API using to get information of cinema', tags=['cinema'])
def get_Info_Cinema(city: str, db: Session = Depends(get_db)):
    response = db.query(models.CinemaInfo).filter(models.CinemaInfo.city == city)
    return response.all()


class modelAccount(BaseModel):
    username: str
    password: str


@app.post('/account/', description='this is an API using to get account id', tags=['cinema'])
def get_AccountID(acc: modelAccount, db: Session = Depends(get_db)):
    response = db.query(models.AccountModel).filter(
        and_(models.AccountModel.username == acc.username, models.AccountModel.password == acc.password))
    try:
        if len(response.all()) == 0:

            return 0
        else:
            return response.first().id
    except Exception as e:
        logging.exception('this is bug')


class model1(BaseModel):
    accountID: int
    ScheduleID: int
    chairID: list = []


@app.post('/book', description='this is an API using to book ticket', tags=['cinema'])
def book_Ticket(movie: model1, db: Session = Depends(get_db)):
    query2 = db.query(models.ScheduleInfo).filter(models.ScheduleInfo.id == movie.ScheduleID)
    if len(query2.all()) == 0:
        # return {"WARNING": 'THIS SCHEDULE IS NOT EXISTED'}
        raise HTTPException(status_code=404, detail='THIS SCHEDULE IS NOT EXISTED')
    listVal = {}
    k = 1
    for i in movie.chairID:
        if check_duplicate(movie.ScheduleID, i, db) == True:
            raise HTTPException(status_code=400,
                                detail='the chair at id = {0} is booked, you can not book it'.format(i))

        response = db.query(models.ScheduleInfo).filter(
            and_(models.ScheduleInfo.id == movie.ScheduleID, models.ChairModel.id == i))

        IDOrder = db.query(models.OrderModel).order_by(models.OrderModel.id.desc()).first()

        query3 = db.query(models.ChairModel).filter(models.ChairModel.id == i)

        IDTicket = db.query(models.TicketInfo).order_by(models.TicketInfo.id.desc()).first().id

        if len(query3.all()) == 0:
            return {"WARNING": "THIS CHAIR IS BOOKED, YOU CAN NOT BOOK IT. PLEASE CHOSE ANOTHER CHAIR"}

        if len(response.all()) == 0:
            return {"Can not find this Schedule or this chair"}
        else:
            valueReturn = {}
            priceTicket = query2.first().price
            time = query2.first().time_start
            res = db.query(models.RoomModel).filter(models.RoomModel.id == query2.first().room_id)
            res1 = db.query(models.CinemaInfo).filter(models.CinemaInfo.id == res.first().cinema_id)
            cinema = res1.first().info + ' ' + res1.first().address
            valueReturn['Cinema'] = cinema
            valueReturn['Schedule'] = time
            valueReturn['Room'] = res.first().name
            valueReturn['Price'] = priceTicket
            valueReturn['Position'] = query3.first().position
            listVal[k] = valueReturn
            k = k + 1

            obj1 = models.OrderModel(id=int(IDOrder.id) + 1, account_id=movie.accountID, state='booking')
            db.add(obj1)
            db.commit()
            obj2 = models.TicketInfo(id=int(IDTicket) + 1, order_id=int(IDOrder.id) + 1, schedule_id=movie.ScheduleID,
                                     chair_id=i)
            db.add(obj2)
            db.commit()
    return listVal


# check state of the chair, if it is booked or not
def check_duplicate(scheduleID: int, chairID: int, db: Session = Depends(get_db)):
    res = db.query(models.TicketInfo).filter(
        and_(models.TicketInfo.chair_id == chairID, models.ScheduleInfo.id == scheduleID)).all()
    if len(res) == 0:
        return False
    else:
        return True


@app.patch('/cancel_ticket', description='this is an API using to cancel booking', tags=['cinema'])
def cancel_booking(idOrder: int, db: Session = Depends(get_db)):
    res = db.query(models.OrderModel).filter(models.OrderModel.id == idOrder)

    if len(res.all()) == 0:
        return {"can not find this deal"}
    else:
        res.update({'state': 'cancel'})
        db.commit()
        return {'cancel successfully'}


@app.get('/history', description='this is an API using to get transaction history', tags=['cinema'])
def get_Transaciton_History(db: Session = Depends(get_db)):
    return db.query(models.TicketInfo).all()


@app.get('/movie', description='this is an API using to get information of a movie', tags=['cinema'])
def get_Info_Movie(idFilm: int, db: Session = Depends(get_db)):
    res = db.query(models.MovieInfo).filter(models.MovieInfo.id == idFilm)
    if len(res.all()) == 0:
        return {"can not find this film"}
    else:
        return res.first()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port="8000")
