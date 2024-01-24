# import os
# import requests
# from PIL import Image
# from io import BytesIO
# import numpy as np
# from keras.preprocessing import image
# from keras.models import load_model

# # Load the saved model
# model = load_model('models\modelVGG.h5')

# # Function to load and preprocess an image from URL
# def preprocess_image_from_url(image_url):
#     try:
#         img_width = 300
#         img_height = 224

#         # Download the image from the URL
#         response = requests.get(image_url)
#         img = Image.open(BytesIO(response.content))

#         # Resize the image to the target size
#         img = img.resize((img_width, img_height))

#         # Convert the image to a NumPy array
#         img_array = image.img_to_array(img)

#         # Expand dimensions to match the model's expected input shape
#         img_array = np.expand_dims(img_array, axis=0)

#         # Normalize the pixel values
#         img_array /= 255.0
    
#         return img_array
    
#     except Exception as e:
#         return {"response",e}


    
# def imageChecker(image_url):
    try:
        # Preprocess the image from the URL
        example_image = preprocess_image_from_url(image_url)

        # Make predictions
        predictions = model.predict(example_image)
        # Convert the predictions to binary classes
        predicted_class = 1 if predictions[0] > 0.5 else 0

#         result_dict = {image_url: predicted_class}

        return predicted_class
    except Exception as e:
        return (f"Error inside the ImageChecker Function {e}")