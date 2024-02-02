# import requests
# from PIL import Image
# from io import BytesIO
# import numpy as np
# import warnings
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.utils import get_file

# # from tensorflow import get_file, load_model, image

# warnings.filterwarnings("ignore")

# # URL of the Keras model in HDF5 format
# H5_url = "https://aitoolmodel.s3.eu-west-2.amazonaws.com/models/modelVGG.h5"

# # Load the Keras model
# model = load_model(get_file("modelVGG.h5", H5_url))


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
#         return {"response", e}


# def imageChecker(image_url):
#     try:
#         # Preprocess the image from the URL
#         example_image = preprocess_image_from_url(image_url)

#         # Make predictions
#         predictions = model.predict(example_image)
#         # Convert the predictions to binary classes
#         predicted_class = 1 if predictions[0] > 0.5 else 0
#         return predicted_class

#     except Exception as e:
#         return f"Error inside the ImageChecker Function {e}"


