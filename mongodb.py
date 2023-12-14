
from pymongo import MongoClient



connection_string = "mongodb+srv://aicarz:kxnJuY2Vc1UtHYVF@cluster0.uarux4m.mongodb.net/?retryWrites=true&w=majority"

mongodbConn = MongoClient(connection_string)
    
carzdb = mongodbConn["aicarsdb"]
carzcollection = carzdb["cars"]
print("mongodb connected")
