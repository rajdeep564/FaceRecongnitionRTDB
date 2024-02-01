import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://faceattendancert-1cf09-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')
data = {
    "21012011167":
    {
        "name":"Rajdeep Singh",
        "major":"Computer",
        "starting-year":2017,
        "total-attendance":6,
        "Standing":"G",
        "Year":4,
        "last-Attendance-time":"2023-12-28  12:54:24"
    },
    "21012011163":
        {
            "name": "Namit Joshi",
            "major": "Computer",
            "starting-year": 2018,
            "total-attendance": 9,
            "Standing": "VG",
            "Year": 4,
            "last-Attendance-time": "2023-12-28  13:54:24"
        },
    "21012011161":
        {
            "name": "Unnati Rathod",
            "major": "Computer",
            "starting-year": 2017,
            "total-attendance": 9,
            "Standing": "VG",
            "Year": 3,
            "last-Attendance-time": "2023-12-27  17:54:24"
        },

}
for key,value in data.items():
    ref.child(key).set(value)


