import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, join
from sqlalchemy.sql.expression import and_, or_

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
    response = db.query(models.ScheduleModel).filter(models.ScheduleModel.movie_id == idFilm)
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
    res = db.query(models.ScheduleModel).filter(models.ScheduleModel.id == idSchedule)
    if len(res.all()) == 0:
        # return {'can not find this schedule'}
        raise HTTPException(status_code=404, detail='CAN NOT FIND THIS SCHEDULE')
    res1 = db.query(models.TicketModel).filter(models.TicketModel.schedule_id == idSchedule)
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
        res3 = db.query(models.TicketModel).filter(models.TicketModel.order_id == i)
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

            raise HTTPException(status_code=404, detail='can not ')
        else:
            return response.first().id
    except Exception as e:
        logging.exception('this is bug')


class model1(BaseModel):
    accountID: int
    ScheduleID: int
    chairID: list = []


@app.post('/book_ticket', description='this is an API using to book ticket', tags=['cinema'])
def book(movie: model1, db: Session = Depends(get_db)):
    query2 = db.query(models.ScheduleModel).filter(models.ScheduleModel.id == movie.ScheduleID)
    if len(query2.all()) == 0:
        # return {"WARNING": 'THIS SCHEDULE IS NOT EXISTED'}
        raise HTTPException(status_code=404, detail='THIS SCHEDULE IS NOT EXISTED')
    listVal = {}
    indexList = 1
    chair = (set(movie.chairID))

    # check validation

    if checkValid(query2.first().room_id, chair, db):
        raise HTTPException(status_code=400, detail='the chair at index {} is not valid'.format(
            checkValid(query2.first().room_id, chair, db)))

    # if checkValid(query2.first().room_id, chair, db) != -1:
    #     raise HTTPException(status_code=400, detail='the chair at index = {0} is not valid' .format(checkValid(query2.first().room_id, chair, db)))
    # print(checkValid(query2.first().room_id, chair, db))

    for i in chair:
        if check_duplicate(movie.ScheduleID, i, db) == True:
            raise HTTPException(status_code=400,
                                detail='the chair at id = {0} is booked, you can not book it'.format(i))

        response = db.query(models.ScheduleModel).filter(
            and_(models.ScheduleModel.id == movie.ScheduleID, models.ChairModel.id == i))

        IDOrder = db.query(models.OrderModel).order_by(models.OrderModel.id.desc()).first()

        query3 = db.query(models.ChairModel).filter(models.ChairModel.id == i)

        IDTicket = db.query(models.TicketModel).order_by(models.TicketModel.id.desc()).first().id

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
            listVal[indexList] = valueReturn
            indexList = indexList + 1

            obj1 = models.OrderModel(id=int(IDOrder.id) + 1, account_id=movie.accountID, state='booking')
            db.add(obj1)
            db.commit()
            obj2 = models.TicketModel(id=int(IDTicket) + 1, order_id=int(IDOrder.id) + 1, schedule_id=movie.ScheduleID,
                                      chair_id=i)
            db.add(obj2)
            db.commit()
    return listVal


# check state of the chair, if it is booked or not
def check_duplicate(scheduleID: int, chairID: int, db: Session = Depends(get_db)):
    res = db.query(models.TicketModel).filter(
        and_(models.TicketModel.chair_id == chairID, models.ScheduleModel.id == scheduleID)).all()
    if len(res) == 0:
        return False
    else:
        return True


def checkValid(idRoom: int, arr: set, db: Session = Depends(get_db)):
    temp = getChair(idRoom, db)
    set_val = set()
    for i in arr:
        for row in temp:
            if row.__dict__['id'] == i:
                set_val.add(i)
    set_tmp = arr.difference(set_val)
    for i in set_tmp:
        print(i)
    return set_tmp


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
    return db.query(models.TicketModel).all()


@app.get('/movie', description='this is an API using to get information of a movie', tags=['cinema'])
def get_Info_Movie(idFilm: int, db: Session = Depends(get_db)):
    res = db.query(models.MovieInfo).filter(models.MovieInfo.id == idFilm)
    if len(res.all()) == 0:
        return {"can not find this film"}
    else:
        return res.first()


@app.get('/chair_in_room', tags=['cinema'])
def getChair(idRoom: int, db: Session = Depends(get_db)):
    return db.query(models.ChairModel).filter(models.ChairModel.room_id == idRoom).all()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port="8000")
