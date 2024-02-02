# from bson import ObjectId
# import io

# from models.carDetection import imageChecker
# from models.nlpEngine import descriptionChecker
# from dataLoader import getData

# def carAdMain(carID):
#     try:
#         # check the car data
#         carData = getData(carID)

#         # print("Car Data:", carData)

#         if carData == None:
#             return {"Response": "The data of the requested Id is not available"}

#         if carData[0].get('adStatus') != "Pending":
#             return {"Response": "The Car AdStatus is not in Pending State"}

#         ID = carData[0].get('Id')
#         carImages = carData[0].get('images')
#         carDesc = carData[0].get('description')
        
#         # print("carImages", carImages)

#         if carImages is not None:
#             imageRes = [imageChecker(image) for image in carImages]
#             # print("Before Filtering the Images:", imageRes)

#             filtered_carImage = [img for img, result in zip(carImages, imageRes) if result == 1]

#             # print("After Filtering the Images", filtered_carImage)
#             # print("len of Filtering Image", len(filtered_carImage))

#             # Find rejected images
#             rejectedImages = list(set(carImages) - set(filtered_carImage))
            
#             if len(filtered_carImage) == 0:
#                 return {'Id': ID, 'CheckedDescription': carDesc, 'rejectedImages':rejectedImages,'adStatus': 'Rejected'}

#             # print("Description Before preprocessing:", carDesc)
#             descriptionCheck = descriptionChecker(carDesc)
#             # print("Description After preprocessing", descriptionCheck)

#             return {'Id': ID, 'CheckedDescription': descriptionCheck,'RejectedImages': rejectedImages, 'adStatus': 'Approved'}
#         else:
#             return {"Response": "No images available for this car ad."}

#     except Exception as e:
#         return f"Error inside the carAdMain Function {e}"



# def dummy(carID):
    
#     is_approved = random.choice([True, False])

#     # Construct the response based on the random result
#     response = {
#         'Id': carID,
#         'rejectedImages': [],
#         'checkedDescription': "",
#         'adStatus': 'Approved' if is_approved else 'Rejected'
#     }

#     return response

