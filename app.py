from flask import Flask, request, Response
from datetime import datetime, timedelta
import peewee as pw
import numpy as np
import time
import os

# structure stolen from https://github.com/cpatrickalves/simple-flask-api/blob/master/app.py

# peewee database config
db = pw.SqliteDatabase('database.db', timeout=10)

class BaseModel(pw.Model):
    class Meta:
        database = db

class SearchField(BaseModel):
    base           = pw.IntegerField()
    search_start   = pw.IntegerField(unique=True)
    search_end     = pw.IntegerField(unique=True)
    search_range   = pw.IntegerField()
    claimed_time   = pw.DateTimeField(null=True)
    claimed_by     = pw.CharField(null=True)
    completed_time = pw.DateTimeField(null=True)
    completed_by   = pw.CharField(null=True)
    client_version = pw.CharField(null=True)

class UniqueCount(BaseModel):
    field       = pw.ForeignKeyField(SearchField)
    uniques     = pw.IntegerField()
    count       = pw.IntegerField()
    class Meta:
        indexes = (
            (('field', 'uniques'), True),
        )

class NearMiss(BaseModel):
    field       = pw.ForeignKeyField(SearchField)
    number      = pw.IntegerField(unique=True)
    uniques     = pw.IntegerField()

# Init app
app = Flask(__name__)

@app.route('/claim', methods=['GET'])
def claim():
    valid_time = timedelta(hours=12)
    query_parameters = request.args
    claimed_by = query_parameters.get('username','anonymous')

    # retry loop: often times we get many claim requests simultaneously
    for i in range(10):
        try:
            if np.random.random() > 0.25:
                field = ( # sequential
                    SearchField.select().where(
                        (SearchField.completed_time == None),
                        (SearchField.claimed_time == None) | (SearchField.claimed_time < datetime.now()-valid_time)
                    ).order_by(SearchField.search_start).get()
                )
            else:
                field = ( # random
                    SearchField.select().where(
                        (SearchField.completed_time == None),
                        (SearchField.claimed_time == None) | (SearchField.claimed_time < datetime.now()-valid_time)
                    ).order_by(pw.fn.Random()).get()
                )
            field.claimed_time = datetime.now()
            field.claimed_by   = query_parameters.get('username','anonymous')
            field.save()
            break
        except:
            if i > 8:
                print('Claim operation is waiting quite a while...')
            time.sleep(np.random.rand()*i)

    claimResponse = {
        'search_id':       field.id,
        'base':            field.base,
        'search_start':    field.search_start,
        'search_end':      field.search_end,
        'claimed_time':    field.claimed_time,
        'claimed_by':      field.claimed_by,
        'expiration_time': field.claimed_time+valid_time,
    }

    return claimResponse

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    #print(data)
    
    # validation: check if all required fields are present
    if not data.get('search_id') or not data.get('unique_count'):
        print('Missing one or more required fields.')
        return 'Missing one or more required fields.', 400
    
    # get search field
    field = SearchField.get_by_id(data['search_id'])
    
    # validation: check if the field is already completed
    if field.completed_by:
        print('This field has already been completed.')
        return 'This field has already been completed.', 400

    # validation: check if the field hasn't been claimed
    if not field.claimed_by:
        print('This field wasn\'t claimed.')
        return 'This field wasn\'t claimed.', 400
    
    # validation: check if unique_count has all digits present, from 1 to base
    for i in range(1,field.base+1):
        if not str(i) in data['unique_count'].keys():
            print('Missing one or more digits in unique_count.')
            return 'Missing one or more digits in unique_count.', 400

    # validation: check if the sum of unique_count counts equals search_range
    if not sum(data['unique_count'].values()) == field.search_range:
        print('Missing one or more counts in unique_count.')
        return 'Missing one or more counts in unique_count.', 400

    # validation: check the distribution of unique_count matches the near_misses
        # TODO

    # save completed_time now, before potentially having to wait on db writes
    field.completed_time = datetime.now()
    
    qty_uniques = [
        {
            'field': field,
            'uniques': unique,
            'count': data['unique_count'][unique],
        } for unique in data['unique_count']
    ]
    with db.atomic():
        for batch in pw.chunked(qty_uniques, 999):
            for i in range(10):
                try:
                    UniqueCount.insert_many(batch).execute()
                    break
                except:
                    if i > 8:
                        print('UniqueCount insert operation is waiting quite a while...')
                    time.sleep(np.random.rand()*i)

    near_misses = [
        {
            'field': field,
            'number': num,
            'uniques': data['near_misses'][num],
        } for num in data['near_misses']
    ]
    with db.atomic():
        for batch in pw.chunked(near_misses, 999):
            for i in range(10):
                try:
                    NearMiss.insert_many(batch).execute()
                    break
                except:
                    if i > 8:
                        print('NearMiss insert operation is waiting quite a while...')
                    time.sleep(np.random.rand()*i)
    
    field.completed_by   = data.get('username', 'anonymous')
    field.client_version = data.get('client_version', 'unknown')
    for i in range(10):
        try:
            field.save()
        except:
            if i > 8:
                print('Final submit operation is waiting quite a while...')
            time.sleep(np.random.rand()*10)

    return 'Submission accepted.', 200

# A method that runs the application server.
if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)