from bson import ObjectId

from models.carDetection import imageChecker
from models.nlpEngine import descriptionChecker
from dataLoader import getData

def carAdMain(carID):
    
    try:
        #check the car data
        carData = getData(carID)

        # print("Car Data:",carData)
        
        if carData == None:
            return {"Response":"The data of requested Id is not avaibale"}

        if carData[0].get('adStatus') != "Pending":
            return {"Response":"The Car AdStatus is not in Pending State"}
        
        ID = carData[0].get('Id')
        carImages = carData[0].get('images')
        # print("carImages",carImages)

        imageRes = []
        if carImages != None:
            for imagesCheck in carImages:
                imageRes.append(imageChecker(imagesCheck))

            # print("Before Filtering the Images:",imageRes)

        filteringCarImage = [d for d in imageRes if all(value != 0 for value in d.values())]

        # print("After Filtering the Images",filteringCarImage)
        # print("len of Filtering Image",len(filteringCarImage))
        
        if len(filteringCarImage) == 0:
            return {"Response":"Rejected"}

        carDesc = carData[0].get('description')
        # print("Description Before preprocessing:",carDesc)
        descriptionCheck = descriptionChecker(carDesc)
        # print("Description After preprocessing", descriptionCheck)

        return {'Id':ID,'description':descriptionCheck,'images':filteringCarImage,'adStatus':'Approved'}
    
    except Exception as e:
        return (f"Error inside the carAdMain Function {e}")
    
    
    
# aa = carAdMain("659fa7c195275f2595fc6045")
# print(aa)